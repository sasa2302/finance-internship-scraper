import logging
from typing import List
from scrapers.base import BaseScraper, JobOffer

logger = logging.getLogger(__name__)

API_BASE = "https://api.smartrecruiters.com/v1/companies"


class SmartRecruitersScraper(BaseScraper):
    """
    Scraper for SmartRecruiters-powered career sites.
    Uses the public SmartRecruiters API (no auth needed).
    Companies: Societe Generale, Natixis.
    """

    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        identifier = self.config["identifier"]
        extra_params = self.config.get("extra_params", {})
        offers = []
        seen_ids = set()

        queries = self._build_search_queries(keywords)
        # Limit to a representative subset to avoid excessive API calls
        queries = queries[:15]

        for query in queries:
            page_offers = self._search(identifier, query, extra_params, seen_ids)
            offers.extend(page_offers)

        logger.info(f"[SmartRecruiters/{self.company_name}] Total unique offers: {len(offers)}")
        return offers

    def _search(self, identifier: str, query: str, extra_params: dict, seen_ids: set) -> List[JobOffer]:
        offers = []
        offset = 0
        limit = 100

        while True:
            url = f"{API_BASE}/{identifier}/postings"
            params = {
                "q": query,
                "limit": limit,
                "offset": offset,
                **extra_params,
            }

            resp = self._safe_get(url, params=params)
            if not resp:
                break

            try:
                data = resp.json()
            except Exception:
                logger.warning(f"[SmartRecruiters/{self.company_name}] Invalid JSON for query '{query}'")
                break

            content = data.get("content", [])
            if not content:
                break

            for posting in content:
                posting_id = posting.get("id", "")
                if posting_id in seen_ids:
                    continue
                seen_ids.add(posting_id)

                ref_url = posting.get("ref", "")
                if not ref_url:
                    company_id = posting.get("company", {}).get("identifier", identifier)
                    ref_url = f"https://jobs.smartrecruiters.com/{company_id}/{posting_id}"

                location_parts = []
                loc = posting.get("location", {})
                if loc.get("city"):
                    location_parts.append(loc["city"])
                if loc.get("country"):
                    location_parts.append(loc["country"])
                location = ", ".join(location_parts)

                department = ""
                dept_data = posting.get("department", {})
                if dept_data:
                    department = dept_data.get("label", "")

                type_of_employment = posting.get("typeOfEmployment", {})
                job_type = ""
                if isinstance(type_of_employment, dict):
                    job_type = type_of_employment.get("label", "")
                elif isinstance(type_of_employment, str):
                    job_type = type_of_employment

                experience_level = posting.get("experienceLevel", {})
                if isinstance(experience_level, dict):
                    exp_label = experience_level.get("label", "").lower()
                else:
                    exp_label = str(experience_level).lower()

                offer = JobOffer(
                    title=posting.get("name", ""),
                    company=self.company_name,
                    location=location,
                    url=ref_url,
                    date_posted=posting.get("releasedDate", ""),
                    description_snippet=posting.get("customField", [{}])[0].get("valueLabel", "") if posting.get("customField") else "",
                    source="smartrecruiters",
                    job_type=job_type or exp_label,
                    duration=None,
                    department=department,
                )
                offers.append(offer)

            total_found = data.get("totalFound", 0)
            offset += limit
            if offset >= total_found or offset >= 300:
                break

        return offers
