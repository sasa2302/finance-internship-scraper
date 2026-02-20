import re
from config.keywords import (
    ROLE_KEYWORDS,
    INTERNSHIP_PREFIXES_FR,
    INTERNSHIP_PREFIXES_EN,
    DURATION_PATTERNS,
    EXCLUDE_KEYWORDS,
)


class JobFilter:
    def is_internship(self, offer) -> bool:
        text = f"{offer.title} {offer.description_snippet} {offer.job_type or ''}".lower()
        all_prefixes = INTERNSHIP_PREFIXES_FR + INTERNSHIP_PREFIXES_EN
        return any(prefix in text for prefix in all_prefixes)

    def matches_keywords(self, offer) -> bool:
        text = f"{offer.title} {offer.description_snippet}".lower()
        return any(kw.lower() in text for kw in ROLE_KEYWORDS)

    def is_excluded(self, offer) -> bool:
        title_lower = offer.title.lower()
        # Only exclude based on title to avoid false positives from descriptions
        return any(kw.lower() in title_lower for kw in EXCLUDE_KEYWORDS)

    def detect_duration(self, offer) -> str:
        text = f"{offer.description_snippet} {offer.duration or ''}"
        for pattern in DURATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return ""

    def compute_relevance_score(self, offer) -> float:
        score = 0.0
        text = f"{offer.title} {offer.description_snippet}".lower()
        title_lower = offer.title.lower()

        # Title keyword match (high weight)
        for kw in ROLE_KEYWORDS:
            if kw.lower() in title_lower:
                score += 0.3
                break

        # Description keyword matches
        kw_count = sum(1 for kw in ROLE_KEYWORDS if kw.lower() in text)
        score += min(kw_count * 0.05, 0.2)

        # Internship confirmation
        if self.is_internship(offer):
            score += 0.2

        # Duration match
        if self.detect_duration(offer):
            score += 0.15

        # Location bonus
        location_lower = (offer.location or "").lower()
        if "paris" in location_lower or "london" in location_lower:
            score += 0.1

        # Department match
        dept = (offer.department or "").lower()
        if any(kw in dept for kw in ["global markets", "cib", "capital markets", "markets"]):
            score += 0.05

        return min(round(score, 2), 1.0)

    def filter_and_score(self, offers) -> list:
        results = []
        for offer in offers:
            if self.is_excluded(offer):
                continue
            if not self.is_internship(offer) and not self.matches_keywords(offer):
                continue

            offer.duration = self.detect_duration(offer) or offer.duration
            offer.relevance_score = self.compute_relevance_score(offer)
            results.append(offer)

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
