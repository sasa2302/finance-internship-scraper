"""Scraper Greenhouse (API publique des job boards).

La plupart des hedge funds et prop firms publient via Greenhouse, qui expose
un JSON public et stable :
    https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true

C'est infiniment plus fiable que le parsing HTML generique : ces sites sont
des applications JavaScript dont le scraper custom_html ne tirait rien.
"""

import html
import logging
import re
from typing import List

from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)

API = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(raw: str, limit: int = 600) -> str:
    if not raw:
        return ""
    text = html.unescape(str(raw))
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()[:limit]


class GreenhouseScraper(BaseScraper):
    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        token = self.config.get("board_token")
        if not token:
            logger.warning(f"[Greenhouse/{self.company_name}] board_token manquant")
            return []

        resp = self._safe_get(API.format(token=token), params={"content": "true"})
        if resp is None:
            return []

        try:
            payload = resp.json()
        except ValueError:
            logger.warning(f"[Greenhouse/{self.company_name}] JSON invalide")
            return []

        offers = []
        for job in payload.get("jobs", []) or []:
            title = str(job.get("title") or "").strip()
            url = str(job.get("absolute_url") or "").strip()
            if not title or not url:
                continue

            location = ""
            loc = job.get("location")
            if isinstance(loc, dict):
                location = str(loc.get("name") or "")
            elif isinstance(loc, str):
                location = loc
            # Certains boards listent plusieurs bureaux
            offices = job.get("offices") or []
            if not location and isinstance(offices, list):
                location = ", ".join(str(o.get("name", "")) for o in offices if isinstance(o, dict))

            departments = job.get("departments") or []
            department = ""
            if isinstance(departments, list) and departments:
                first = departments[0]
                if isinstance(first, dict):
                    department = str(first.get("name") or "")

            offers.append(JobOffer(
                title=title,
                company=self.company_name,
                location=location,
                url=url,
                date_posted=str(job.get("updated_at") or "")[:10],
                description_snippet=strip_html(job.get("content", "")),
                source="greenhouse",
                job_type=None,
                duration=None,
                department=department,
            ))

        logger.info(f"[Greenhouse/{self.company_name}] {len(offers)} offres")
        return offers
