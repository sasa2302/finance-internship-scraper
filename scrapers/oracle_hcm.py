"""Scraper Oracle Cloud Recruiting (Oracle HCM).

API REST publique utilisee par les sites carriere Oracle Cloud :
    https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions
      ?onlyData=true&expand=requisitionList
      &finder=findReqs;siteNumber={site},keyword={mot},limit={n}

Confirme sur JP Morgan (jpmc.fa.oraclecloud.com, CX_1001) et Schroders
(ekbq.fa.em2.oraclecloud.com, CX_1).

Remplace la version precedente, qui devinait un motif d'URL et ne renvoyait
jamais rien.
"""

import logging
from typing import List

from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)

API_PATH = "/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
JOB_URL = "https://{host}/hcmUI/CandidateExperience/en/sites/{site}/job/{job_id}"

# Peu de mots-cles suffisent : l'API cherche dans tout le contenu de l'annonce,
# et le filtrage fin est fait ensuite par utils/filters.py
KEYWORDS = ["internship", "intern", "stage", "summer analyst"]
PAGE_LIMIT = 200


class OracleHCMScraper(BaseScraper):
    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        host = self.config.get("host")
        site = self.config.get("site_number")
        if not host or not site:
            logger.warning(f"[OracleHCM/{self.company_name}] host ou site_number manquant")
            return []

        offers, seen = [], set()
        for keyword in KEYWORDS:
            offers.extend(self._search(host, site, keyword, seen))

        logger.info(f"[OracleHCM/{self.company_name}] {len(offers)} offres")
        return offers

    def _search(self, host, site, keyword, seen) -> List[JobOffer]:
        params = {
            "onlyData": "true",
            "expand": "requisitionList",
            "finder": f"findReqs;siteNumber={site},keyword={keyword},limit={PAGE_LIMIT}",
        }
        resp = self._safe_get(f"https://{host}{API_PATH}", params=params)
        if resp is None:
            return []

        try:
            items = resp.json().get("items") or []
        except ValueError:
            logger.warning(f"[OracleHCM/{self.company_name}] JSON invalide ('{keyword}')")
            return []
        if not items:
            return []

        offers = []
        for job in items[0].get("requisitionList") or []:
            job_id = str(job.get("Id") or "").strip()
            title = str(job.get("Title") or "").strip()
            if not job_id or not title or job_id in seen:
                continue
            seen.add(job_id)

            # L'API expose la duree du contrat : precieux pour off-cycle vs summer
            duration = ""
            months = job.get("WorkDurationMonths")
            if months:
                duration = f"{months} mois"

            offers.append(JobOffer(
                title=title,
                company=self.company_name,
                location=str(job.get("PrimaryLocation") or ""),
                url=JOB_URL.format(host=host, site=site, job_id=job_id),
                date_posted=str(job.get("PostedDate") or "")[:10],
                description_snippet=str(job.get("ShortDescriptionStr") or "")[:600],
                source="oracle_hcm",
                job_type=str(job.get("JobType") or "") or None,
                duration=duration or None,
                department=str(job.get("Department") or "") or None,
            ))
        return offers
