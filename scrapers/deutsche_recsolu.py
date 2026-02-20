import logging
from typing import List
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)


class DeutscheRecsoluScraper(BaseScraper):
    """
    Scraper for Deutsche Bank career site (Yello/Recsolu).
    Companies: Deutsche Bank.
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

        logger.info(f"[Recsolu/{self.company_name}] Total unique offers: {len(offers)}")
        return offers

    def _search(self, base_url: str, query: str, seen_urls: set) -> List[JobOffer]:
        offers = []

        # Recsolu/Yello job board search
        search_url = base_url
        params = {
            "q": query,
        }

        resp = self._safe_get(search_url, params=params)
        if not resp:
            return offers

        soup = BeautifulSoup(resp.text, "lxml")

        # Recsolu uses card/list-based job listings
        job_cards = (
            soup.select("div.job-board-entry") or
            soup.select("div[class*='job']") or
            soup.select("div[class*='posting']") or
            soup.select("a[href*='positions']")
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

                if href.startswith("http"):
                    job_url = href
                elif href.startswith("/"):
                    job_url = f"https://db.recsolu.com{href}"
                else:
                    job_url = f"{base_url}/{href}"

                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                # Extract location
                location = ""
                loc_elem = card.find(["span", "div", "p"], class_=lambda x: x and "location" in str(x).lower()) if hasattr(card, 'find') else None
                if loc_elem:
                    location = loc_elem.get_text(strip=True)

                offer = JobOffer(
                    title=title,
                    company=self.company_name,
                    location=location,
                    url=job_url,
                    date_posted="",
                    description_snippet="",
                    source="recsolu",
                    job_type="",
                    duration=None,
                    department=None,
                )
                offers.append(offer)

            except Exception as e:
                logger.debug(f"[Recsolu/{self.company_name}] Error parsing card: {e}")
                continue

        return offers
