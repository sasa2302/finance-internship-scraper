from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class JobOffer:
    title: str
    company: str
    location: str
    url: str
    date_posted: Optional[str] = None
    description_snippet: str = ""
    source: str = ""
    job_type: Optional[str] = None
    duration: Optional[str] = None
    department: Optional[str] = None
    relevance_score: float = 0.0


class BaseScraper(ABC):
    def __init__(self, company_config: dict, http_client):
        self.company_name = company_config["name"]
        self.config = company_config
        self.client = http_client

    @abstractmethod
    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        pass

    def _build_search_queries(self, keywords: List[str]) -> List[str]:
        prefixes = ["stage", "internship", "stagiaire", "intern"]
        queries = []
        for prefix in prefixes:
            for kw in keywords:
                queries.append(f"{prefix} {kw}")
        return queries

    def _safe_get(self, url: str, **kwargs):
        try:
            resp = self.client.get(url, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:
            logger.warning(f"[{self.company_name}] GET {url} failed: {e}")
            return None

    def _safe_post(self, url: str, **kwargs):
        try:
            resp = self.client.post(url, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:
            logger.warning(f"[{self.company_name}] POST {url} failed: {e}")
            return None
