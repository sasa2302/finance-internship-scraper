import re
from config.keywords import (
    ROLE_KEYWORDS,
    INTERNSHIP_PREFIXES_FR,
    INTERNSHIP_PREFIXES_EN,
    DURATION_PATTERNS,
    EXCLUDE_DURATION_PATTERNS,
    EXCLUDE_KEYWORDS,
    EXCLUDE_COMPANIES,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_LOCATIONS,
    ACCEPTED_LOCATIONS,
    EXCLUDE_UK_LOCATIONS,
)

# Non-stage job types to reject outright
NON_STAGE_TYPES = [
    "full-time", "full_time", "permanent", "cdi", "cdd",
    "alternance", "apprenticeship", "contrat pro", "freelance",
    "contractor", "temporary", "interim", "vie",
]


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
        text_lower = f"{offer.title} {offer.description_snippet}".lower()

        # Exclude based on title keywords (M&A, PE, corporate, seniority, etc.)
        if any(kw.lower() in title_lower for kw in EXCLUDE_KEYWORDS):
            return True

        # Exclude non-finance-de-marché title patterns
        if any(kw.lower() in title_lower for kw in EXCLUDE_TITLE_KEYWORDS):
            return True

        # Exclude based on company name (retail, luxury, FMCG, consulting, etc.)
        company_lower = (offer.company or "").lower()
        if any(exc.lower() in company_lower for exc in EXCLUDE_COMPANIES):
            return True

        # Exclude bad durations (12 months, alternance, etc.)
        for pattern in EXCLUDE_DURATION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False

    def is_location_excluded(self, offer) -> bool:
        """Check if the offer is in an excluded location (secondary French cities + non-London/Dublin UK)."""
        location_lower = (offer.location or "").lower()

        # If no location info, don't exclude (let it through)
        if not location_lower or location_lower.strip() == "":
            return False

        # Check if it's in a secondary French city
        is_in_excluded_city = any(city in location_lower for city in EXCLUDE_LOCATIONS)
        if is_in_excluded_city:
            is_in_accepted = any(loc in location_lower for loc in ACCEPTED_LOCATIONS)
            if not is_in_accepted:
                return True

        # Check UK locations - only London and Dublin are accepted
        uk_indicators = ["united kingdom", "uk", "great britain", "england", "scotland",
                         "wales", "ireland", "northern ireland"]
        is_uk = any(ind in location_lower for ind in uk_indicators)
        is_in_excluded_uk = any(city in location_lower for city in EXCLUDE_UK_LOCATIONS)

        if is_uk or is_in_excluded_uk:
            # Must mention London or Dublin to be accepted
            uk_accepted = ["london", "canary wharf", "city of london", "dublin"]
            if not any(loc in location_lower for loc in uk_accepted):
                return True

        return False

    def is_location_accepted(self, offer) -> bool:
        """Check if the offer is in an accepted location."""
        location_lower = (offer.location or "").lower()

        # If no location, accept it (don't filter out unknowns)
        if not location_lower or location_lower.strip() == "":
            return True

        # Check for France specifically - only Paris area is OK
        france_indicators = ["france", "français", "francais"]
        is_france = any(ind in location_lower for ind in france_indicators)

        if is_france:
            # Must also mention Paris area
            paris_area = ["paris", "la defense", "la défense", "puteaux", "courbevoie",
                          "levallois", "neuilly", "issy", "boulogne", "ile-de-france",
                          "île-de-france", "idf", "92", "75"]
            return any(loc in location_lower for loc in paris_area)

        # Check for UK specifically - only London and Dublin are OK
        uk_indicators = ["united kingdom", "uk", "great britain", "england",
                         "scotland", "wales", "ireland"]
        is_uk = any(ind in location_lower for ind in uk_indicators)

        if is_uk:
            uk_accepted = ["london", "canary wharf", "city of london", "dublin"]
            return any(loc in location_lower for loc in uk_accepted)

        # Check for accepted locations
        if any(loc in location_lower for loc in ACCEPTED_LOCATIONS):
            return True

        # If location doesn't match any known pattern, keep it (don't over-filter)
        return True

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

        # Location bonus - Paris or London get highest bonus
        location_lower = (offer.location or "").lower()
        if "paris" in location_lower or "london" in location_lower:
            score += 0.1
        elif any(loc in location_lower for loc in ["zurich", "geneva", "luxembourg", "frankfurt"]):
            score += 0.08

        # Department match
        dept = (offer.department or "").lower()
        if any(kw in dept for kw in ["global markets", "cib", "capital markets", "markets"]):
            score += 0.05

        return min(round(score, 2), 1.0)

    def is_non_stage(self, offer) -> bool:
        """Reject offers that are clearly NOT stages (CDI, CDD, alternance, VIE, etc.)."""
        job_type_lower = (offer.job_type or "").lower()
        title_lower = offer.title.lower()
        text_lower = f"{offer.title} {offer.description_snippet}".lower()

        # Check job_type field directly
        for non_stage in NON_STAGE_TYPES:
            if non_stage in job_type_lower:
                return True

        # Check if title explicitly says it's NOT a stage
        non_stage_title_markers = [
            "poste", "emploi", "recrutement", "embauche",
            "cdi", "cdd", "full-time", "full time",
            "temps plein", "permanent position",
        ]
        for marker in non_stage_title_markers:
            if marker in title_lower:
                # Exception: "poste de stage" or "poste stagiaire" is fine
                if marker == "poste" and ("stage" in title_lower or "stagiaire" in title_lower):
                    continue
                return True

        return False

    def filter_and_score(self, offers) -> list:
        results = []
        for offer in offers:
            # Step 0: Must be a stage (reject CDI, CDD, alternance, VIE, etc.)
            if self.is_non_stage(offer):
                continue

            # Step 1: Exclude by title/company/duration
            if self.is_excluded(offer):
                continue

            # Step 2: Exclude by location (secondary French cities + UK filtering)
            if self.is_location_excluded(offer):
                continue

            # Step 3: Must match internship OR role keywords
            if not self.is_internship(offer) and not self.matches_keywords(offer):
                continue

            offer.duration = self.detect_duration(offer) or offer.duration
            offer.relevance_score = self.compute_relevance_score(offer)
            results.append(offer)

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
