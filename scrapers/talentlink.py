import logging
from typing import List
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)


class TalentLinkScraper(BaseScraper):
    """
    Scraper for Saba TalentLink (tal.net) career sites.
    Companies: Lazard.
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

        logger.info(f"[TalentLink/{self.company_name}] Total unique offers: {len(offers)}")
        return offers

    def _search(self, base_url: str, query: str, seen_urls: set) -> List[JobOffer]:
        offers = []

        # TalentLink search URL - append search parameters
        search_url = base_url
        params = {
            "ftq": query,  # Free text query
        }

        resp = self._safe_get(search_url, params=params)
        if not resp:
            return offers

        soup = BeautifulSoup(resp.text, "lxml")

        # TalentLink uses various structures - look for vacancy listing elements
        job_cards = (
            soup.select("div.ts-offer-card") or
            soup.select("div[class*='vacancy']") or
            soup.select("li[class*='vacancy']") or
            soup.select("tr[class*='vacancy']") or
            soup.select("a[href*='vacancy']")
        )

        for card in job_cards:
            try:
                link = card.find("a", href=True) if card.name != "a" else card
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

                # Extract location
                location = ""
                loc_elem = card.find(["span", "div"], class_=lambda x: x and "location" in str(x).lower()) if hasattr(card, 'find') else None
                if loc_elem:
                    location = loc_elem.get_text(strip=True)

                offer = JobOffer(
                    title=title,
                    company=self.company_name,
                    location=location,
                    url=job_url,
                    date_posted="",
                    description_snippet="",
                    source="talentlink",
                    job_type="",
                    duration=None,
                    department=None,
                )
                offers.append(offer)

            except Exception as e:
                logger.debug(f"[TalentLink/{self.company_name}] Error parsing card: {e}")
                continue

        return offers
