import logging
from typing import List
from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)


class WorkdayScraper(BaseScraper):
    """
    Scraper for Workday-powered career sites.
    Uses the internal /wday/cxs/ JSON API (same API the JS frontend calls).
    Companies: Barclays, Morgan Stanley, Citi, Fidelity, HSBC, UBS.
    """

    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        base_url = self.config["base_url"]
        wday_path = self.config["wday_path"]
        offers = []
        seen_ids = set()

        queries = self._build_search_queries(keywords)
        queries = queries[:12]

        for query in queries:
            page_offers = self._search(base_url, wday_path, query, seen_ids)
            offers.extend(page_offers)

        logger.info(f"[Workday/{self.company_name}] Total unique offers: {len(offers)}")
        return offers

    def _search(self, base_url: str, wday_path: str, query: str, seen_ids: set) -> List[JobOffer]:
        offers = []

        # Determine the Workday host from the base_url
        # e.g., https://barclays.wd3.myworkdayjobs.com/en-US/external_career_site_barclays
        # API: https://barclays.wd3.myworkdayjobs.com/wday/cxs/barclays/external_career_site_barclays/jobs
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        api_url = f"{host}/wday/cxs/{wday_path}/jobs"

        offset = 0
        limit = 20

        while True:
            payload = {
                "appliedFacets": {},
                "limit": limit,
                "offset": offset,
                "searchText": query,
            }

            resp = self._safe_post(
                api_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            if not resp:
                break

            try:
                data = resp.json()
            except Exception:
                logger.warning(f"[Workday/{self.company_name}] Invalid JSON for query '{query}'")
                break

            job_postings = data.get("jobPostings", [])
            if not job_postings:
                break

            for posting in job_postings:
                external_path = posting.get("externalPath", "")
                job_id = external_path or posting.get("bulletFields", [""])[0]

                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                job_url = f"{base_url}{external_path}" if external_path else base_url

                # Extract info from bulletFields (often contains location, date, etc.)
                bullet_fields = posting.get("bulletFields", [])
                location = bullet_fields[0] if bullet_fields else ""
                posted_on = bullet_fields[1] if len(bullet_fields) > 1 else ""

                offer = JobOffer(
                    title=posting.get("title", ""),
                    company=self.company_name,
                    location=posting.get("locationsText", location),
                    url=job_url,
                    date_posted=posting.get("postedOn", posted_on),
                    description_snippet="",
                    source="workday",
                    job_type=posting.get("subtitleText", ""),
                    duration=None,
                    department=None,
                )
                offers.append(offer)

            total = data.get("total", 0)
            offset += limit
            if offset >= total or offset >= 200:
                break

        return offers
