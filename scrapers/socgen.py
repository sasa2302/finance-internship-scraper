"""Scraper Societe Generale.

Le site carriere expose la liste complete de ses offres sur une seule page
rendue cote serveur :
    https://careers.societegenerale.com/en/Technical/all-job-offers

Une requete suffit donc pour l'integralite du catalogue (660 offres au moment
de l'ecriture), sans JavaScript ni pagination.

C'est la premiere grande banque francaise branchee : elle publie ses stages
Global Markets a Paris, la zone prioritaire de l'utilisatrice.
"""

import logging
import re
from typing import List

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)

ALL_OFFERS_URL = "https://careers.societegenerale.com/en/Technical/all-job-offers"
_ID_RE = re.compile(r"-([0-9A-Z]{6,})-[a-z]{2}$")


class SocGenScraper(BaseScraper):
    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        url = self.config.get("all_offers_url", ALL_OFFERS_URL)
        resp = self._safe_get(url)
        if resp is None:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        offers, seen = [], set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/job-offers/" not in href or href in seen:
                continue

            title = link.get_text(" ", strip=True)
            if not title or len(title) < 5:
                continue
            seen.add(href)

            # La carte porte : titre | lieu | type de contrat | metier
            card = link.find_parent("div")
            location = contract = department = ""
            if card is not None:
                parts = [p.strip() for p in card.get_text("|", strip=True).split("|") if p.strip()]
                # On retire le titre, le reste suit toujours le meme ordre
                rest = [p for p in parts if p != title]
                if len(rest) >= 1:
                    location = rest[0]
                if len(rest) >= 2:
                    contract = rest[1]
                if len(rest) >= 3:
                    department = rest[2]

            offers.append(JobOffer(
                title=title,
                company=self.company_name,
                location=location,
                url=href if href.startswith("http") else f"https://careers.societegenerale.com{href}",
                date_posted="",
                description_snippet=" ".join(filter(None, [contract, department])),
                source="socgen",
                job_type=contract or None,
                duration=None,
                department=department or None,
            ))

        logger.info(f"[SocGen/{self.company_name}] {len(offers)} offres")
        return offers
