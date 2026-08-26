"""Construction du rapport unique.

Remplace l'ancien CSVManager, qui ecrivait quatre fichiers dates par run
(un CSV maitre, un off-cycle, un summer, plus le classeur). On n'ecrit
desormais qu'un seul fichier : data/stages_finance_marche.xlsx, mis a jour
a chaque run.
"""

import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from config.settings import REPORT_PATH, REPORT_WINDOW_DAYS
from utils.excel_export import build_workbook, read_existing

logger = logging.getLogger(__name__)

BUCKETS = ("off_cycle", "summer", "unknown")


def _parse_day(value):
    if not value:
        return None
    text = str(value).strip()[:10]
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


class ReportManager:
    def __init__(self, report_path=REPORT_PATH, window_days=REPORT_WINDOW_DAYS):
        self.path = Path(report_path)
        self.window_days = window_days
        self.today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _row_from_offer(self, offer, offer_id):
        return {
            "id": offer_id,
            "title": offer.title,
            "company": offer.company or "",
            "employer_category": offer.employer_category or "",
            "location": offer.location or "",
            "zone": offer.zone or "",
            "zone_label": offer.zone_label or "",
            "period_label": getattr(offer, "period_label", "") or "",
            "period_note": getattr(offer, "period_note", "") or "",
            "internship_type": offer.internship_type or "unknown",
            "type_reason": offer.type_reason or "",
            "duration": offer.duration or "",
            "url": offer.url,
            "date_posted": (offer.date_posted or "")[:10],
            "date_added": self.today,
            "source": offer.source,
            "relevance_score": round(float(offer.relevance_score or 0), 2),
            "description_snippet": (offer.description_snippet or "")[:400],
            "_is_new": True,
        }

    def save(self, offers, dedup_manager, run_stats=None):
        """Fusionne les nouvelles offres avec le rapport precedent.

        Renvoie (nb_nouvelles, buckets).
        """
        previous = read_existing(self.path)
        cutoff = date.today() - timedelta(days=self.window_days)

        buckets = {k: [] for k in BUCKETS}
        seen_urls = set()

        # 1. Les nouveautes de ce run, en tete
        added = 0
        for offer in offers:
            if dedup_manager.is_duplicate(offer.url, offer.title):
                continue
            dedup_manager.mark_seen(offer.url, offer.title)
            row = self._row_from_offer(offer, dedup_manager.compute_hash(offer.url, offer.title))
            key = row["internship_type"] if row["internship_type"] in buckets else "unknown"
            buckets[key].append(row)
            seen_urls.add(str(row["url"]))
            added += 1

        # 2. Les offres des runs precedents, dans la fenetre
        kept_old, expired = 0, 0
        for row in previous:
            url = str(row.get("url") or "")
            if not url or url in seen_urls:
                continue
            day = _parse_day(row.get("date_added"))
            if day is not None and day < cutoff:
                expired += 1
                continue
            row["_is_new"] = False
            key = str(row.get("internship_type") or "unknown")
            buckets[key if key in buckets else "unknown"].append(row)
            seen_urls.add(url)
            kept_old += 1

        build_workbook(buckets, self.path, run_stats=run_stats, window_days=self.window_days)

        total = sum(len(v) for v in buckets.values())
        logger.info(f"  {added} nouvelle(s), {kept_old} conservee(s), "
                    f"{expired} sortie(s) de la fenetre {self.window_days} j "
                    f"-> {total} lignes dans {self.path.name}")
        return added, buckets
