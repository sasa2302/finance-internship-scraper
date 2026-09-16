"""Scraper IBM Kenexa BrassRing (Talent Gateway), utilise par UBS.

Le site charge ses offres par un appel AJAX qui exige un jeton anti-CSRF
present dans la page d'accueil, et les cookies de la meme session :

  1. GET  https://{host}/TGnewUI/Search/Home/Home?partnerid=..&siteid=..
         -> cookies + champ cache __RequestVerificationToken
  2. POST https://{host}/TgNewUI/Search/Ajax/ProcessSortAndShowMoreJobs
         en-tete RFT = jeton, corps JSON avec pageNumber (50 offres par page)

Confirme sur UBS (jobs.ubs.com, partnerid 25008, site 5131 "Job Board for
Graduates") : 160 offres, dont les Off-Cycle et Summer Global Markets.
Environ 5 requetes par run.
"""

import html
import logging
import re
from typing import List

from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)

HOME = "https://{host}/TGnewUI/Search/Home/Home?partnerid={partner}&siteid={site}"
SEARCH = "https://{host}/TgNewUI/Search/Ajax/ProcessSortAndShowMoreJobs"
TOKEN_RE = re.compile(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"')
TAG_RE = re.compile(r"<[^>]+>")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
PAGE_SIZE = 50
MAX_PAGES = 10


class BrassRingScraper(BaseScraper):
    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        host = self.config.get("host")
        partner = self.config.get("partner_id")
        site = self.config.get("site_id")
        if not (host and partner and site):
            logger.warning(f"[BrassRing/{self.company_name}] host, partner_id ou site_id manquant")
            return []

        home_url = HOME.format(host=host, partner=partner, site=site)
        resp = self._safe_get(home_url, headers={"User-Agent": UA})
        if resp is None:
            return []
        match = TOKEN_RE.search(resp.text)
        if not match:
            logger.warning(f"[BrassRing/{self.company_name}] jeton de session introuvable")
            return []
        headers = {
            "User-Agent": UA,
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "RFT": match.group(1),
            "Referer": home_url,
        }

        offers, seen = [], set()
        for page in range(1, MAX_PAGES + 1):
            body = {
                "partnerId": str(partner), "siteId": str(site),
                "keyword": "", "location": "",
                "keywordCustomSolrFields": "AutoReq,JobTitle,FORMTEXT2",
                "locationCustomSolrFields": "FORMTEXT2",
                "linkId": "", "Latitude": 0, "Longitude": 0,
                "facetfilterfields": {"Facet": []},
                "powersearchoptions": {"PowerSearchOption": []},
                "SortType": "LastUpdated", "pageNumber": page,
                "encryptedSessionValue": "",
            }
            r = self._safe_post(SEARCH.format(host=host), json=body, headers=dict(headers))
            if r is None:
                break
            try:
                data = r.json()
            except ValueError:
                logger.warning(f"[BrassRing/{self.company_name}] JSON invalide page {page}")
                break

            jobs = (data.get("Jobs") or {}).get("Job") or []
            for job in jobs:
                offer = self._parse(job, host, partner, site)
                if offer and offer.url not in seen:
                    seen.add(offer.url)
                    offers.append(offer)

            total = data.get("JobsCount") or 0
            if len(jobs) < PAGE_SIZE or page * PAGE_SIZE >= total:
                break

        logger.info(f"[BrassRing/{self.company_name}] {len(offers)} offres")
        return offers

    def _parse(self, job, host, partner, site):
        values = {q.get("QuestionName"): q.get("Value") for q in job.get("Questions") or []}
        title = html.unescape(str(values.get("jobtitle") or "")).strip()
        reqid = str(values.get("reqid") or "").strip()
        if not title or not reqid:
            return None
        link = job.get("Link") or (
            f"https://{host}/TGnewUI/Search/home/HomeWithPreLoad?partnerid={partner}"
            f"&siteid={site}&PageType=JobDetails&jobid={reqid}")
        description = TAG_RE.sub(" ", html.unescape(str(values.get("jobdescription") or "")))
        return JobOffer(
            title=title,
            company=self.company_name,
            # formtext23 porte le pays / la ville ("Switzerland - Zürich")
            location=html.unescape(str(values.get("formtext23") or "")),
            url=link,
            date_posted="",
            description_snippet=re.sub(r"\s+", " ", description).strip()[:4000],
            source="brassring",
            job_type=None,
            duration=None,
            department=str(values.get("formtext21") or "") or None,
        )
