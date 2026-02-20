import logging
from typing import List
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)


class CustomHTMLScraper(BaseScraper):
    """
    Generic HTML scraper for career sites without a known API.
    Parses HTML pages to find job listings matching search keywords.
    Companies: Murex, Kepler Cheuvreux, Credit Agricole CIB, Rothschild, HSBC, UBS, BofA.
    """

    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        offers = []
        seen_urls = set()
        base_url = self.config["base_url"]

        # Strategy: just fetch the listing page directly.
        # Most career sites are SPAs and don't support server-side search params.
        # The aggregators (LinkedIn/Indeed) will catch offers from these companies.
        page_offers = self._scrape_listing_page(base_url, seen_urls)
        offers.extend(page_offers)

        logger.info(f"[CustomHTML/{self.company_name}] Total unique offers: {len(offers)}")
        return offers

    def _scrape_listing_page(self, url: str, seen_urls: set) -> List[JobOffer]:
        """Fetch and parse a careers listing page directly."""
        resp = self._safe_get(url)
        if not resp:
            return []
        return self._parse_job_listings(resp.text, url, seen_urls)

    def _parse_job_listings(self, html: str, base_url: str, seen_urls: set) -> List[JobOffer]:
        """Parse HTML to find job listing links and details."""
        offers = []
        soup = BeautifulSoup(html, "lxml")
        parsed_base = urlparse(base_url)
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

        # Strategy: find all links that look like job postings
        # Look for links containing job-related URL patterns
        job_patterns = [
            "job", "career", "position", "opening", "vacancy",
            "offre", "emploi", "stage", "internship", "recruit",
        ]

        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link.get("href", "").strip()
            title = link.get_text(strip=True)

            # Skip empty, short, or navigation links
            if not title or len(title) < 8 or len(title) > 200:
                continue

            # Check if this looks like a job listing link
            href_lower = href.lower()
            title_lower = title.lower()

            is_job_link = (
                any(p in href_lower for p in job_patterns) or
                any(p in title_lower for p in ["stage", "intern", "analyst", "trading",
                                                "sales", "quant", "risk", "derivative"])
            )

            if not is_job_link:
                continue

            # Build full URL
            if href.startswith("http"):
                job_url = href
            elif href.startswith("/"):
                job_url = f"{base_domain}{href}"
            elif href.startswith("#"):
                continue
            else:
                job_url = urljoin(base_url, href)

            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            # Try to extract additional info from surrounding context
            parent = link.parent
            location = ""
            date_posted = ""

            if parent:
                # Look for location in sibling or parent elements
                loc_elem = parent.find(
                    ["span", "div", "p"],
                    class_=lambda x: x and any(
                        term in str(x).lower()
                        for term in ["location", "lieu", "city", "ville"]
                    )
                )
                if loc_elem:
                    location = loc_elem.get_text(strip=True)

                # Look for date
                date_elem = parent.find(
                    ["span", "div", "time"],
                    class_=lambda x: x and any(
                        term in str(x).lower()
                        for term in ["date", "posted", "publi"]
                    )
                )
                if date_elem:
                    date_posted = date_elem.get_text(strip=True)

            offer = JobOffer(
                title=title,
                company=self.company_name,
                location=location,
                url=job_url,
                date_posted=date_posted,
                description_snippet="",
                source="custom_html",
                job_type="",
                duration=None,
                department=None,
            )
            offers.append(offer)

        return offers
