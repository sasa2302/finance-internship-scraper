#!/usr/bin/env python3
"""
Finance Internship Scraper - run quotidien.

Scrape les sites carriere des acteurs de finance de marche + les agregateurs,
filtre sur l'univers finance de marche (banques, hedge funds, prop firms,
brokers, asset managers), puis produit un classeur Excel avec un onglet
Off-Cycle et un onglet Summer.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.companies import COMPANIES
from config.keywords import ROLE_KEYWORDS
from config.settings import (
    MIN_DELAY, MAX_DELAY, MAX_RETRIES, REQUEST_TIMEOUT, RUN_LOG_PATH,
    MAX_RUNTIME_MINUTES, COMPANIES_BUDGET_SHARE,
)
from utils.budget import Deadline
from utils.http_client import HttpClient
from utils.dedup import DeduplicationManager
from utils.report import ReportManager
from utils.filters import JobFilter
from scrapers.workday import WorkdayScraper
from scrapers.custom_html import CustomHTMLScraper
from scrapers.greenhouse import GreenhouseScraper
from scrapers.smartrecruiters import SmartRecruitersScraper
from scrapers.taleo import TaleoScraper
from scrapers.oracle_hcm import OracleHCMScraper
from scrapers.talentlink import TalentLinkScraper
from scrapers.goldman_avature import GoldmanAvatureScraper
from scrapers.deutsche_recsolu import DeutscheRecsoluScraper
from scrapers.aggregators import AggregatorScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

SCRAPER_REGISTRY = {
    "greenhouse": GreenhouseScraper,
    "workday": WorkdayScraper,
    "smartrecruiters": SmartRecruitersScraper,
    "taleo": TaleoScraper,
    "oracle_hcm": OracleHCMScraper,
    "talentlink": TalentLinkScraper,
    "goldman_avature": GoldmanAvatureScraper,
    "deutsche_recsolu": DeutscheRecsoluScraper,
    "custom_html": CustomHTMLScraper,
}

# Ordre de passage : les sources a API JSON d'abord, le parsing HTML generique
# en dernier. Mesure faite sur 10 sites : custom_html rend 0 offre (ce sont des
# applications JavaScript), Workday en rend 120 sur 3 sites. Si le budget de
# temps s'epuise, on ne perd donc que les sources improductives.
SCRAPER_PRIORITY = {
    "greenhouse": 0,
    "workday": 1,
    "smartrecruiters": 2,
    "taleo": 3,
    "oracle_hcm": 4,
    "talentlink": 5,
    "goldman_avature": 6,
    "deutsche_recsolu": 7,
    "custom_html": 9,
}


def collect_offers(http_client, skip_companies=False, skip_aggregators=False):
    """Phase de collecte brute, sous contrainte de temps.

    Renvoie (offres, erreurs, stats). La collecte s'interrompt proprement quand
    le budget est epuise : mieux vaut un rapport partiel qu'un job tue par le
    timeout GitHub sans avoir rien ecrit.
    """
    all_offers, errors = [], []
    skipped_companies = 0

    companies_budget = MAX_RUNTIME_MINUTES * COMPANIES_BUDGET_SHARE
    deadline = Deadline(companies_budget)

    if not skip_companies:
        logger.info(f"Phase 1 : {len(COMPANIES)} sites carriere "
                    f"(budget {companies_budget:.0f} min)...")
        ordered = sorted(COMPANIES,
                         key=lambda c: SCRAPER_PRIORITY.get(c["scraper_type"], 8))
        for company_config in ordered:
            scraper_type = company_config["scraper_type"]
            name = company_config["name"]

            if deadline.expired():
                skipped_companies += 1
                continue

            if scraper_type not in SCRAPER_REGISTRY:
                logger.warning(f"  Type de scraper inconnu '{scraper_type}' pour {name}")
                continue
            try:
                scraper = SCRAPER_REGISTRY[scraper_type](company_config, http_client)
                offers = scraper.scrape(ROLE_KEYWORDS)
                logger.info(f"  {name}: {len(offers)} offres brutes")
                # Le nom de la societe fait foi pour la whitelist employeur
                for offer in offers:
                    if not offer.company:
                        offer.company = name
                all_offers.extend(offers)
            except Exception as e:
                logger.error(f"  ECHEC {name}: {e}")
                errors.append({"company": name, "scraper": scraper_type, "error": str(e)})

    if skipped_companies:
        logger.warning(f"  {skipped_companies} sites carriere non interroges (budget epuise). "
                       f"Ils passeront en tete au prochain run.")
    logger.info(f"  Phase 1 terminee : {deadline.summary()}")

    if not skip_aggregators:
        agg_budget = MAX_RUNTIME_MINUTES - (deadline.elapsed / 60.0)
        agg_deadline = Deadline(max(agg_budget, 3.0))
        logger.info(f"Phase 2 : agregateurs (budget {agg_deadline.limit / 60:.0f} min)...")
        try:
            agg_offers = AggregatorScraper(http_client).scrape(ROLE_KEYWORDS, deadline=agg_deadline)
            logger.info(f"  {len(agg_offers)} offres brutes depuis les agregateurs")
            all_offers.extend(agg_offers)
        except Exception as e:
            logger.error(f"  ECHEC agregateurs: {e}")
            errors.append({"company": "aggregators", "scraper": "aggregators", "error": str(e)})

    stats = {"companies_skipped": skipped_companies}
    return all_offers, errors, stats


def main():
    parser = argparse.ArgumentParser(description="Scraper stages finance de marche")
    parser.add_argument("--skip-companies", action="store_true",
                        help="Ne pas scraper les sites carriere")
    parser.add_argument("--skip-aggregators", action="store_true",
                        help="Ne pas scraper les agregateurs")
    parser.add_argument("--no-dedup", action="store_true",
                        help="Ignorer l'historique de deduplication (rapport complet)")
    args = parser.parse_args()

    logger.info("=" * 64)
    logger.info("Finance Internship Scraper - stages de finance de marche")
    logger.info("=" * 64)

    http_client = HttpClient(
        min_delay=MIN_DELAY, max_delay=MAX_DELAY,
        max_retries=MAX_RETRIES, timeout=REQUEST_TIMEOUT,
    )
    dedup = DeduplicationManager()
    if args.no_dedup:
        # Rapport complet : on ignore l'historique SANS l'ecraser ensuite.
        dedup.seen = set()
        logger.info("Deduplication desactivee (l'historique ne sera pas modifie).")

    report = ReportManager()
    job_filter = JobFilter()

    all_offers, errors, collect_stats = collect_offers(
        http_client, args.skip_companies, args.skip_aggregators)

    logger.info(f"Phase 3 : filtrage de {len(all_offers)} offres brutes...")
    kept = job_filter.filter_and_score(all_offers)
    job_filter.log_rejections()
    buckets = job_filter.split_by_period(kept)
    logger.info(f"    -> {len(kept)} offres retenues "
                f"(off-cycle {len(buckets['off_cycle'])}, "
                f"summer {len(buckets['summer'])}, "
                f"a trier {len(buckets['unknown'])})")

    logger.info("Phase 4 : mise a jour du rapport...")
    run_stats = {
        "Offres brutes collectees": len(all_offers),
        "Retenues apres filtrage": len(kept),
        "Sites carriere interroges": 0 if args.skip_companies else len(COMPANIES),
        "Erreurs de scraping": len(errors),
        "Sites non interroges (budget)": collect_stats["companies_skipped"],
    }
    added, report_buckets = report.save(kept, dedup, run_stats=run_stats)
    if args.no_dedup:
        logger.info("Historique de deduplication laisse intact (--no-dedup).")
    else:
        dedup.save()

    run_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_raw_offers": len(all_offers),
        "total_after_filter": len(kept),
        "new_offers_added": added,
        "by_type": {k: len(v) for k, v in buckets.items()},
        "companies_scraped": run_stats["Sites carriere interroges"],
        "rejections": dict(job_filter.rejections),
        "errors_count": len(errors),
        "errors": errors,
        "report": str(report.path),
    }
    log_path = Path(RUN_LOG_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(run_log, indent=2, ensure_ascii=False))

    logger.info("=" * 64)
    logger.info("RUN TERMINE")
    logger.info(f"  Offres brutes        : {len(all_offers)}")
    logger.info(f"  Retenues (marche)    : {len(kept)}")
    logger.info(f"  Nouvelles ce jour    : {added}")
    logger.info(f"    - Off-Cycle        : {sum(1 for r in report_buckets['off_cycle'] if r.get('_is_new'))}")
    logger.info(f"    - Summer           : {sum(1 for r in report_buckets['summer'] if r.get('_is_new'))}")
    logger.info(f"    - A trier          : {sum(1 for r in report_buckets['unknown'] if r.get('_is_new'))}")
    logger.info(f"  Rapport              : {report.path} "
                f"({sum(len(v) for v in report_buckets.values())} lignes au total)")
    logger.info(f"  Erreurs              : {len(errors)}")
    for err in errors[:10]:
        logger.info(f"    - {err['company']}: {err['error'][:70]}")
    logger.info("=" * 64)

    return 0


if __name__ == "__main__":
    sys.exit(main())
