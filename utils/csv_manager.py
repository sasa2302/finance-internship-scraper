import pandas as pd
from pathlib import Path
from datetime import datetime, timezone


class CSVManager:
    COLUMNS = [
        "id", "title", "company", "location", "url", "date_posted",
        "date_scraped", "description_snippet", "source", "job_type",
        "duration", "department", "relevance_score", "status",
    ]

    def __init__(self, csv_dir="data"):
        self.csv_dir = Path(csv_dir)
        # Each run creates a new file with today's date
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.csv_path = self.csv_dir / f"internships_{today}.csv"

    def save_offers(self, new_offers, dedup_manager) -> int:
        """Save today's offers to a new dated CSV file (no appending to old files)."""
        added_count = 0
        rows = []

        for offer in new_offers:
            if dedup_manager.is_duplicate(offer.url, offer.title):
                continue

            dedup_manager.mark_seen(offer.url, offer.title)
            rows.append({
                "id": dedup_manager.compute_hash(offer.url, offer.title),
                "title": offer.title,
                "company": offer.company,
                "location": offer.location or "",
                "url": offer.url,
                "date_posted": offer.date_posted or "",
                "date_scraped": datetime.now(timezone.utc).isoformat(),
                "description_snippet": (offer.description_snippet or "")[:300],
                "source": offer.source,
                "job_type": offer.job_type or "",
                "duration": offer.duration or "",
                "department": offer.department or "",
                "relevance_score": round(offer.relevance_score, 2),
                "status": "new",
            })
            added_count += 1

        if rows:
            new_df = pd.DataFrame(rows, columns=self.COLUMNS)
            self.csv_dir.mkdir(parents=True, exist_ok=True)
            new_df.to_csv(self.csv_path, index=False)

        return added_count
