# Primary role keywords
ROLE_KEYWORDS = [
    "trading",
    "sales",
    "structuration",
    "structuring",
    "derivatives",
    "fixed income",
    "quantitative analyst",
    "quant",
    "risk management",
    "market risk",
    "structured products",
    "rates",
    "credit",
    "equity derivatives",
    "flow trading",
    "exotic",
    "global markets",
    "capital markets",
]

# Internship-type identifiers
INTERNSHIP_PREFIXES_FR = ["stage", "stagiaire", "alternance", "cesure", "césure"]
INTERNSHIP_PREFIXES_EN = ["internship", "intern", "placement", "graduate program", "summer analyst"]

# Duration filter patterns (regex)
DURATION_PATTERNS = [
    r"6\s*mois",
    r"6\s*months?",
    r"six\s*months?",
    r"six\s*mois",
    r"cesure",
    r"césure",
    r"gap\s*year",
    r"ann[ée]e\s*de\s*c[ée]sure",
    r"long\s*internship",
    r"4\s*to\s*6\s*months?",
    r"4\s*[àa]\s*6\s*mois",
    r"5\s*[àa]\s*6\s*mois",
]

# Negative keywords (filter out irrelevant results)
EXCLUDE_KEYWORDS = [
    "CDI",
    "permanent",
    "experienced",
    "senior",
    "manager",
    "director",
    "VP",
    "vice president",
    "head of",
    "managing director",
    "executive",
    "principal",
]
