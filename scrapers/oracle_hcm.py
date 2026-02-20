import logging
from typing import List
from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)


class OracleHCMScraper(BaseScraper):
    """
    Scraper for Oracle HCM Cloud career sites.
    Uses the internal REST API that the JS frontend calls.
    Companies: JP Morgan.
    """

    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        offers = []
        seen_ids = set()
        base_url = self.config["base_url"]

        queries = self._build_search_queries(keywords)
        queries = queries[:10]

        for query in queries:
            page_offers = self._search(base_url, query, seen_ids)
            offers.extend(page_offers)

        logger.info(f"[OracleHCM/{self.company_name}] Total unique offers: {len(offers)}")
        return offers

    def _search(self, base_url: str, query: str, seen_ids: set) -> List[JobOffer]:
        offers = []

        # Oracle HCM uses a REST API for requisition search
        # The frontend at jpmc.fa.oraclecloud.com calls this API
        api_url = base_url.rstrip("/")

        # Try the common Oracle HCM API pattern
        search_url = f"{api_url}"
        params = {
            "keyword": query,
            "mode": "location",
            "sortBy": "RELEVANCE",
            "limit": 25,
            "offset": 0,
        }

        resp = self._safe_get(search_url, params=params)
        if not resp:
            # Fallback: try POST-based search
            resp = self._safe_post(
                search_url,
                json={
                    "keyword": query,
                    "limit": 25,
                    "offset": 0,
                    "sortBy": "RELEVANCE",
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

        if not resp:
            return offers

        try:
            data = resp.json()
        except Exception:
            # If JSON fails, try HTML parsing as fallback
            return self._parse_html_fallback(resp.text, base_url, seen_ids)

        # Parse Oracle HCM JSON response
        items = data.get("items", data.get("requisitionList", []))
        if isinstance(data, list):
            items = data

        for item in items:
            req_id = str(item.get("Id", item.get("requisitionId", item.get("id", ""))))
            if req_id in seen_ids:
                continue
            seen_ids.add(req_id)

            title = item.get("Title", item.get("title", ""))
            location = item.get("PrimaryLocation", item.get("primaryLocation", ""))
            if isinstance(location, dict):
                location = location.get("name", str(location))

            job_url = f"{base_url}/{req_id}" if req_id else base_url

            offer = JobOffer(
                title=title,
                company=self.company_name,
                location=str(location),
                url=job_url,
                date_posted=item.get("PostedDate", item.get("postedDate", "")),
                description_snippet=str(item.get("ShortDescriptionStr", item.get("description", "")))[:300],
                source="oracle_hcm",
                job_type=item.get("JobType", item.get("jobType", "")),
                duration=None,
                department=item.get("Organization", item.get("department", "")),
            )
            offers.append(offer)

        return offers

    def _parse_html_fallback(self, html: str, base_url: str, seen_ids: set) -> List[JobOffer]:
        """Fallback HTML parsing if API returns HTML instead of JSON."""
        from bs4 import BeautifulSoup
        offers = []

        soup = BeautifulSoup(html, "lxml")
        job_links = soup.find_all("a", href=True)

        for link in job_links:
            href = link.get("href", "")
            if "requisition" not in href.lower() and "job" not in href.lower():
                continue

            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue

            job_url = href if href.startswith("http") else f"{base_url}/{href.lstrip('/')}"
            if job_url in seen_ids:
                continue
            seen_ids.add(job_url)

            offer = JobOffer(
                title=title,
                company=self.company_name,
                location="",
                url=job_url,
                source="oracle_hcm",
            )
            offers.append(offer)

        return offers
