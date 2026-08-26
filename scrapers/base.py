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
    # Champs remplis par les filtres
    employer_category: str = ""      # Banque / Hedge Fund / Prop Trading / ...
    internship_type: str = ""        # off_cycle | summer | unknown
    type_reason: str = ""            # motif de la classification calendaire
    zone: str = ""                   # CORE | EUROPE | GLOBAL | INCONNU
    zone_label: str = ""             # "Paris / IDF", "Londres", "Hong Kong"...
    period_label: str = ""           # "janvier 2027", "2027", "" si inconnue
    period_note: str = ""            # "date non identifiee" le cas echeant


class BaseScraper(ABC):
    def __init__(self, company_config: dict, http_client):
        self.company_name = company_config["name"]
        self.config = company_config
        self.client = http_client

    @abstractmethod
    def scrape(self, keywords: List[str]) -> List[JobOffer]:
        pass

    def _build_search_queries(self, keywords: List[str]) -> List[str]:
        """Requetes de recherche, prefixes ALTERNES.

        Les appelants tronquent cette liste (ex. les 12 premieres). En groupant
        par prefixe, la troncature ne gardait que les requetes "stage ..." et
        n'envoyait jamais "internship" ni "summer" : les programmes Summer
        anglophones passaient donc a la trappe. On alterne pour que toute
        troncature conserve un melange francais / anglais.
        """
        prefixes = ["stage", "internship", "summer internship", "off-cycle internship"]
        queries = []
        for kw in keywords:
            for prefix in prefixes:
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
