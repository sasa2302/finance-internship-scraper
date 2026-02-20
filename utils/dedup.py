import hashlib
import json
from pathlib import Path


class DeduplicationManager:
    def __init__(self, hashes_path="data/seen_hashes.json"):
        self.hashes_path = Path(hashes_path)
        self.seen = self._load()

    def _load(self):
        if self.hashes_path.exists():
            try:
                return set(json.loads(self.hashes_path.read_text()))
            except (json.JSONDecodeError, TypeError):
                return set()
        return set()

    def save(self):
        self.hashes_path.parent.mkdir(parents=True, exist_ok=True)
        self.hashes_path.write_text(json.dumps(sorted(self.seen), indent=2))

    def compute_hash(self, url: str, title: str) -> str:
        normalized = f"{url.strip().lower()}|{title.strip().lower()}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def is_duplicate(self, url: str, title: str) -> bool:
        h = self.compute_hash(url, title)
        return h in self.seen

    def mark_seen(self, url: str, title: str):
        h = self.compute_hash(url, title)
        self.seen.add(h)
