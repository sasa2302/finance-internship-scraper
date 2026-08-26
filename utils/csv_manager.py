"""Ecriture des sorties : CSV maitre + CSV par type de stage + classeur Excel."""

import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from utils.classify import LABELS
from utils.excel_export import build_workbook

logger = logging.getLogger(__name__)


class CSVManager:
    COLUMNS = [
        "id", "title", "company", "employer_category", "location", "zone",
        "zone_label", "internship_type", "type_label", "type_reason",
        "duration", "url", "date_posted", "date_scraped",
        "description_snippet", "source", "job_type", "department",
        "relevance_score", "status",
    ]

    def __init__(self, csv_dir="data"):
        self.csv_dir = Path(csv_dir)
        self.day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.csv_path = self.csv_dir / f"internships_{self.day}.csv"
        self.off_cycle_path = self.csv_dir / f"off_cycle_{self.day}.csv"
        self.summer_path = self.csv_dir / f"summer_{self.day}.csv"
        self.excel_path = self.csv_dir / f"stages_finance_marche_{self.day}.xlsx"

    def _row(self, offer, offer_id):
        return {
            "id": offer_id,
            "title": offer.title,
            "company": offer.company or "",
            "employer_category": offer.employer_category or "",
            "location": offer.location or "",
            "zone": offer.zone or "",
            "zone_label": offer.zone_label or "",
            "internship_type": offer.internship_type or "unknown",
            "type_label": LABELS.get(offer.internship_type, "A trier"),
            "type_reason": offer.type_reason or "",
            "duration": offer.duration or "",
            "url": offer.url,
            "date_posted": offer.date_posted or "",
            "date_scraped": datetime.now(timezone.utc).isoformat(),
            "description_snippet": (offer.description_snippet or "")[:400],
            "source": offer.source,
            "job_type": offer.job_type or "",
            "department": offer.department or "",
            "relevance_score": round(float(offer.relevance_score or 0), 2),
            "status": "new",
        }

    def save(self, offers, buckets, dedup_manager, run_stats=None):
        """Deduplique, ecrit les CSV et le classeur Excel.

        Renvoie (nb_nouvelles, buckets_dedupliques).
        """
        self.csv_dir.mkdir(parents=True, exist_ok=True)

        fresh = []
        for offer in offers:
            if dedup_manager.is_duplicate(offer.url, offer.title):
                continue
            dedup_manager.mark_seen(offer.url, offer.title)
            fresh.append(offer)

        fresh_buckets = {"off_cycle": [], "summer": [], "unknown": []}
        rows = []
        for offer in fresh:
            offer_id = dedup_manager.compute_hash(offer.url, offer.title)
            rows.append(self._row(offer, offer_id))
            key = offer.internship_type if offer.internship_type in fresh_buckets else "unknown"
            fresh_buckets[key].append(offer)

        df = pd.DataFrame(rows, columns=self.COLUMNS)
        df.to_csv(self.csv_path, index=False)

        df[df["internship_type"] == "off_cycle"].to_csv(self.off_cycle_path, index=False)
        df[df["internship_type"] == "summer"].to_csv(self.summer_path, index=False)

        build_workbook(fresh_buckets, self.excel_path, run_stats=run_stats)

        logger.info(f"  CSV maitre  : {self.csv_path.name} ({len(rows)} lignes)")
        logger.info(f"  CSV off-cyc : {self.off_cycle_path.name} ({len(fresh_buckets['off_cycle'])})")
        logger.info(f"  CSV summer  : {self.summer_path.name} ({len(fresh_buckets['summer'])})")
        logger.info(f"  Excel       : {self.excel_path.name}")

        return len(rows), fresh_buckets

    # Compatibilite avec l'ancienne interface
    def save_offers(self, new_offers, dedup_manager):
        buckets = {"off_cycle": [], "summer": [], "unknown": []}
        for o in new_offers:
            key = o.internship_type if o.internship_type in buckets else "unknown"
            buckets[key].append(o)
        added, _ = self.save(new_offers, buckets, dedup_manager)
        return added
