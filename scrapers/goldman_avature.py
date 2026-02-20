import logging
from typing import List
from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)


class GoldmanAvatureScraper(BaseScraper):
    """
    Scraper for Goldman Sachs career site (higher.gs.com / Avature).
    Companies: Goldman Sachs.
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

        logger.info(f"[Goldman/{self.company_name}] Total unique offers: {len(offers)}")
        return offers

    def _search(self, base_url: str, query: str, seen_ids: set) -> List[JobOffer]:
        offers = []

        # Goldman's higher.gs.com uses an internal API
        # Try the common Avature API pattern
        api_url = f"{base_url.rstrip('/')}/search"

        # Try JSON API first
        resp = self._safe_get(
            api_url,
            params={
                "q": query,
                "page": 1,
                "pageSize": 25,
            },
        )

        if resp and resp.headers.get("content-type", "").startswith("application/json"):
            try:
                data = resp.json()
                roles = data.get("roles", data.get("results", data.get("data", [])))
                if isinstance(roles, list):
                    for role in roles:
                        role_id = str(role.get("id", ""))
                        if role_id in seen_ids:
                            continue
                        seen_ids.add(role_id)

                        offer = JobOffer(
                            title=role.get("title", role.get("name", "")),
                            company=self.company_name,
                            location=role.get("location", role.get("city", "")),
                            url=role.get("url", f"{base_url}/{role_id}"),
                            date_posted=role.get("postedDate", ""),
                            description_snippet=str(role.get("description", ""))[:300],
                            source="goldman_avature",
                            job_type=role.get("type", ""),
                            duration=None,
                            department=role.get("division", role.get("department", "")),
                        )
                        offers.append(offer)
                return offers
            except Exception:
                pass

        # Fallback: HTML parsing
        resp = self._safe_get(base_url, params={"q": query})
        if not resp:
            return offers

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")

        # Look for role/job listing elements
        job_cards = (
            soup.select("div[class*='role']") or
            soup.select("a[class*='role']") or
            soup.select("div[class*='job']") or
            soup.select("li[class*='opportunity']")
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

                job_url = href if href.startswith("http") else f"https://higher.gs.com{href}"
                if job_url in seen_ids:
                    continue
                seen_ids.add(job_url)

                offer = JobOffer(
                    title=title,
                    company=self.company_name,
                    location="",
                    url=job_url,
                    source="goldman_avature",
                )
                offers.append(offer)

            except Exception as e:
                logger.debug(f"[Goldman] Error parsing card: {e}")
                continue

        return offers
