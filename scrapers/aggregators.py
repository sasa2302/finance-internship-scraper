import logging
from typing import List
from scrapers.base import BaseScraper, JobOffer
from config.settings import (
    AGGREGATOR_RESULTS_WANTED,
    AGGREGATOR_HOURS_OLD,
    AGGREGATOR_MAX_QUERIES,
)
from config.locations import AGGREGATOR_SEARCH_LOCATIONS

logger = logging.getLogger(__name__)


class AggregatorScraper:
    """
    Scraper for job aggregator sites using python-jobspy.
    Covers: LinkedIn, Indeed, Glassdoor.
    Also includes Welcome to the Jungle via HTML scraping.
    """

    def __init__(self, http_client):
        self.client = http_client

    def scrape(self, keywords: List[str], deadline=None) -> List[JobOffer]:
        offers = []
        offers.extend(self._scrape_jobspy(keywords, deadline))
        offers.extend(self._scrape_wttj(keywords, deadline))
        return offers

    def _scrape_jobspy(self, keywords: List[str], deadline=None) -> List[JobOffer]:
        try:
            from jobspy import scrape_jobs
        except ImportError:
            logger.warning("python-jobspy not installed, skipping aggregator scraping")
            return []

        offers = []
        seen_urls = set()

        # Plan de requetes HIERARCHISE.
        # Le produit cartesien complet (16 termes x 14 zones = 224 appels)
        # depassait largement le temps disponible. On interroge donc a fond
        # les places prioritaires, et plus legerement les autres.
        core_terms = [
            "stage trading", "stage structuration", "stage sales trading",
            "summer internship global markets", "off-cycle internship trading",
            "stage quantitative finance de marche",
        ]
        wide_terms = ["summer internship trading", "internship global markets"]

        priority = {"Paris, France", "London, United Kingdom",
                    "Switzerland", "Luxembourg"}

        plan = []
        for location, country in AGGREGATOR_SEARCH_LOCATIONS:
            terms = core_terms if location in priority else wide_terms
            for term in terms:
                plan.append((term, location, country))

        logger.info(f"[Aggregators] Plan : {len(plan)} requetes "
                    f"({len(priority)} zones prioritaires)")

        for search_term, location, indeed_country in plan:
            if deadline is not None and deadline.expired():
                logger.warning("[Aggregators] Budget epuise, arret de la collecte.")
                break
            try:
                logger.info(f"[Aggregators] '{search_term}' dans {location}...")
                jobs_df = scrape_jobs(
                    site_name=["indeed", "linkedin", "glassdoor"],
                    search_term=search_term,
                    location=location,
                    results_wanted=AGGREGATOR_RESULTS_WANTED,
                    hours_old=AGGREGATOR_HOURS_OLD,
                    country_indeed=indeed_country,
                )

                if jobs_df is None or jobs_df.empty:
                    continue

                for _, row in jobs_df.iterrows():
                    url = str(row.get("job_url", ""))
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)

                    offer = JobOffer(
                        title=str(row.get("title", "")),
                        company=str(row.get("company", "")),
                        location=str(row.get("location", "")),
                        url=url,
                        date_posted=str(row.get("date_posted", "")),
                        description_snippet=str(row.get("description", ""))[:300],
                        source=str(row.get("site", "aggregator")),
                        # Le vrai type renvoye par jobspy : ne pas forcer
                        # "internship", sinon tout passe le test is_internship.
                        job_type=str(row.get("job_type", "") or ""),
                        duration=None,
                        department=None,
                    )
                    offers.append(offer)

            except Exception as e:
                logger.warning(f"[Aggregators] Erreur '{search_term}' / {location}: {e}")
                continue

        logger.info(f"[Aggregators/JobSpy] Total offers: {len(offers)}")
        return offers

    def _scrape_wttj(self, keywords: List[str], deadline=None) -> List[JobOffer]:
        """Scrape Welcome to the Jungle job listings."""
        from bs4 import BeautifulSoup

        offers = []
        seen_urls = set()
        core_keywords = ["trading", "sales trading", "structuration", "derivatives",
                         "quant", "market risk", "fixed income", "hedge fund",
                         "portfolio management", "global markets"]

        for kw in core_keywords:
            if deadline is not None and deadline.expired():
                logger.warning("[WTTJ] Budget epuise, arret.")
                break
            query = f"stage {kw}"
            url = (
                "https://www.welcometothejungle.com/fr/jobs"
                f"?query={query}"
                "&refinementList%5Bcontract_type%5D%5B%5D=internship"
            )

            try:
                resp = self.client.get(url)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")

                # WTTJ uses various card structures - look for job listing links
                job_links = soup.find_all("a", href=True)
                for link in job_links:
                    href = link.get("href", "")
                    if "/companies/" not in href or "/jobs/" not in href:
                        continue

                    full_url = f"https://www.welcometothejungle.com{href}" if href.startswith("/") else href
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)

                    # Try to extract title from the link or its parent
                    title_text = link.get_text(strip=True)
                    if not title_text or len(title_text) < 5:
                        continue

                    offer = JobOffer(
                        title=title_text,
                        company="",  # Will be extracted from URL or page
                        location="",
                        url=full_url,
                        date_posted="",
                        description_snippet="",
                        source="welcometothejungle",
                        job_type="stage",
                        duration=None,
                        department=None,
                    )

                    # Try to extract company from URL path
                    # Pattern: /companies/COMPANY_NAME/jobs/JOB_TITLE
                    parts = href.split("/companies/")
                    if len(parts) > 1:
                        company_part = parts[1].split("/")[0]
                        offer.company = company_part.replace("-", " ").title()

                    offers.append(offer)

            except Exception as e:
                logger.warning(f"[WTTJ] Error for query '{query}': {e}")
                continue

        logger.info(f"[Aggregators/WTTJ] Total offers: {len(offers)}")
        return offers
