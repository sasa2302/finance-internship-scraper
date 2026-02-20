import logging
from typing import List
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)


class TaleoScraper(BaseScraper):
    """
    Scraper for Taleo (Oracle)-powered career sites.
    Uses HTML parsing of the career section search results.
    Companies: BNP Paribas.
    """

    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        offers = []
        seen_urls = set()
        base_url = self.config["base_url"]

        queries = self._build_search_queries(keywords)
        queries = queries[:10]

        for query in queries:
            page_offers = self._search(base_url, query, seen_urls)
            offers.extend(page_offers)

        logger.info(f"[Taleo/{self.company_name}] Total unique offers: {len(offers)}")
        return offers

    def _search(self, base_url: str, query: str, seen_urls: set) -> List[JobOffer]:
        offers = []

        # Taleo search URL pattern
        params = {
            "keywords": query,
            "location": "",
            "sortBy": "0",  # Sort by relevance
        }

        resp = self._safe_get(base_url, params=params)
        if not resp:
            return offers

        soup = BeautifulSoup(resp.text, "lxml")

        # Taleo typically uses table rows or div-based job listing containers
        # Try multiple common Taleo HTML patterns
        job_rows = (
            soup.select("tr.cellBGWhite, tr.cellBGGrey") or  # Classic Taleo table
            soup.select("div.job-result") or  # Modern Taleo
            soup.select("div[class*='requisition']") or  # Another variant
            soup.select("a[href*='jobdetail']")  # Direct links
        )

        for row in job_rows:
            try:
                # Extract title and URL
                link = row.find("a", href=True) if row.name != "a" else row
                if not link:
                    continue

                title = link.get_text(strip=True)
                href = link.get("href", "")

                if not title or len(title) < 5:
                    continue

                # Build full URL
                if href.startswith("http"):
                    job_url = href
                elif href.startswith("/"):
                    from urllib.parse import urlparse
                    parsed = urlparse(base_url)
                    job_url = f"{parsed.scheme}://{parsed.netloc}{href}"
                else:
                    job_url = f"{base_url.rsplit('/', 1)[0]}/{href}"

                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                # Try to extract location
                location = ""
                loc_elem = row.find("span", class_=lambda x: x and "location" in x.lower()) if hasattr(row, 'find') else None
                if loc_elem:
                    location = loc_elem.get_text(strip=True)

                # Try to extract date
                date_posted = ""
                date_elem = row.find("span", class_=lambda x: x and "date" in x.lower()) if hasattr(row, 'find') else None
                if date_elem:
                    date_posted = date_elem.get_text(strip=True)

                offer = JobOffer(
                    title=title,
                    company=self.company_name,
                    location=location,
                    url=job_url,
                    date_posted=date_posted,
                    description_snippet="",
                    source="taleo",
                    job_type="",
                    duration=None,
                    department=None,
                )
                offers.append(offer)

            except Exception as e:
                logger.debug(f"[Taleo/{self.company_name}] Error parsing row: {e}")
                continue

        return offers
