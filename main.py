#!/usr/bin/env python3
"""
Finance Internship Scraper - Daily autonomous job scraper
Scrapes bank career sites and aggregators for trading/sales/structuring internships.
"""

import logging
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from config.companies import COMPANIES
from config.keywords import ROLE_KEYWORDS
from config.settings import MIN_DELAY, MAX_DELAY, MAX_RETRIES, REQUEST_TIMEOUT
from utils.http_client import HttpClient
from utils.dedup import DeduplicationManager
from utils.csv_manager import CSVManager
from utils.filters import JobFilter
from scrapers.workday import WorkdayScraper
from scrapers.custom_html import CustomHTMLScraper
from scrapers.aggregators import AggregatorScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

SCRAPER_REGISTRY = {
    "workday": WorkdayScraper,
    "custom_html": CustomHTMLScraper,
}


def main():
    logger.info("=" * 60)
    logger.info("Finance Internship Scraper - Starting daily run")
    logger.info("=" * 60)

    # Initialize components
    http_client = HttpClient(
        min_delay=MIN_DELAY,
        max_delay=MAX_DELAY,
        max_retries=MAX_RETRIES,
        timeout=REQUEST_TIMEOUT,
    )
    dedup = DeduplicationManager()
    csv_mgr = CSVManager()
    job_filter = JobFilter()

    all_offers = []
    errors = []

    # Phase 1: Scrape individual company career sites
    logger.info(f"Phase 1: Scraping {len(COMPANIES)} company career sites...")
    for company_config in COMPANIES:
        scraper_type = company_config["scraper_type"]
        company_name = company_config["name"]

        if scraper_type not in SCRAPER_REGISTRY:
            logger.warning(f"Unknown scraper type '{scraper_type}' for {company_name}, skipping")
            continue

        try:
            scraper_class = SCRAPER_REGISTRY[scraper_type]
            scraper = scraper_class(company_config, http_client)
            logger.info(f"  Scraping {company_name} ({scraper_type})...")
            offers = scraper.scrape(ROLE_KEYWORDS)
            logger.info(f"    -> {len(offers)} raw offers from {company_name}")
            all_offers.extend(offers)
        except Exception as e:
            logger.error(f"    FAILED: {company_name}: {e}")
            errors.append({"company": company_name, "scraper": scraper_type, "error": str(e)})

    # Phase 2: Scrape aggregator sites
    logger.info("Phase 2: Scraping aggregator sites (LinkedIn, Indeed, Glassdoor, WTTJ)...")
    try:
        agg_scraper = AggregatorScraper(http_client)
        agg_offers = agg_scraper.scrape(ROLE_KEYWORDS)
        logger.info(f"    -> {len(agg_offers)} offers from aggregators")
        all_offers.extend(agg_offers)
    except Exception as e:
        logger.error(f"    FAILED: aggregators: {e}")
        errors.append({"company": "aggregators", "scraper": "aggregators", "error": str(e)})

    # Phase 3: Filter and score
    logger.info(f"Phase 3: Filtering {len(all_offers)} raw offers...")
    filtered_offers = job_filter.filter_and_score(all_offers)
    logger.info(f"    -> {len(filtered_offers)} relevant offers after filtering")

    # Phase 4: Deduplicate and save to CSV
    logger.info("Phase 4: Deduplicating and saving to CSV...")
    added_count = csv_mgr.append_new_offers(filtered_offers, dedup)
    dedup.save()
    logger.info(f"    -> {added_count} NEW offers added to CSV")

    # Phase 5: Write run log
    run_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_raw_offers": len(all_offers),
        "total_after_filter": len(filtered_offers),
        "new_offers_added": added_count,
        "companies_scraped": len(COMPANIES),
        "errors_count": len(errors),
        "errors": errors,
    }

    log_path = Path("data/run_log.json")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(run_log, indent=2, ensure_ascii=False))

    # Summary
    logger.info("=" * 60)
    logger.info("RUN COMPLETE")
    logger.info(f"  Raw offers collected:  {len(all_offers)}")
    logger.info(f"  After filtering:       {len(filtered_offers)}")
    logger.info(f"  New offers added:      {added_count}")
    logger.info(f"  Errors:                {len(errors)}")
    if errors:
        for err in errors:
            logger.info(f"    - {err['company']}: {err['error'][:80]}")
    logger.info("=" * 60)

    return 0 if not errors or added_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
