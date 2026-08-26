"""Classification d'une offre en OFF-CYCLE / SUMMER.

Off-cycle : stage long (>= 4 mois), cesure, stage de fin d'etudes, demarrage
hors juin-aout. C'est le format francais classique (6 mois) et le "off-cycle
internship" anglo-saxon.

Summer : programme d'ete court (8-12 semaines), "Summer Analyst",
"Summer Internship", "stage d'ete".
"""

import re

from utils.textnorm import norm_text, has_phrase, has_any

OFF_CYCLE = "off_cycle"
SUMMER = "summer"
UNKNOWN = "unknown"

LABELS = {
    OFF_CYCLE: "Off-Cycle",
    SUMMER: "Summer",
    UNKNOWN: "A trier",
}

# --- Signaux SUMMER -------------------------------------------------------
SUMMER_PHRASES = [
    "summer internship", "summer intern", "summer analyst", "summer associate",
    "summer programme", "summer program", "summer placement", "summer scheme",
    "summer insight", "stage d ete", "stage ete", "programme d ete",
    "summer 2026", "summer 2027", "summer 2028",
    "sophomore program", "spring week", "spring insight", "insight programme",
]

# 8 a 12 semaines / 2-3 mois => programme d'ete
SUMMER_DURATION_RE = [
    r"\b(8|9|10|11|12)\s*(weeks?|semaines?)\b",
    r"\bten\s*weeks?\b",
    r"\beight\s*weeks?\b",
    r"\b(2|3|two|three)\s*(months?|mois)\b",
]

# --- Signaux OFF-CYCLE ----------------------------------------------------
OFF_CYCLE_PHRASES = [
    "off cycle", "off-cycle", "offcycle", "hors cycle",
    "cesure", "annee de cesure", "gap year", "year in industry",
    "industrial placement", "placement year", "long internship",
    "long term internship", "long term intern", "stage long terme",
    "stage de fin d etudes", "stage fin d etudes", "stage cesure",
    "stage de cesure", "stage long", "internship 6 months",
    "6 month internship", "6 months internship", "winter internship",
    "spring internship", "autumn internship", "fall internship",
]

# 4 mois et plus => off-cycle
OFF_CYCLE_DURATION_RE = [
    r"\b(4|5|6|7|8|9|10|11)\s*(months?|mois)\b",
    r"\b(four|five|six|seven|huit|six|quatre|cinq)\s*(months?|mois)\b",
    r"\b(4|5|6)\s*[aà]\s*(6|7|8|9|12)\s*mois\b",
    r"\b(4|5|6)\s*to\s*(6|7|8|9|12)\s*months?\b",
    r"\b(16|20|24|26|28)\s*(weeks?|semaines?)\b",
]

# Mois de demarrage : juin/juillet/aout => plutot summer ; le reste => off-cycle
SUMMER_START_MONTHS = ["june", "juin", "july", "juillet", "august", "aout"]
OFF_CYCLE_START_MONTHS = [
    "january", "janvier", "february", "fevrier", "march", "mars",
    "april", "avril", "september", "septembre", "october", "octobre",
    "november", "novembre", "december", "decembre",
]

_DUR_MONTHS_RE = re.compile(r"\b(\d{1,2})\s*(months?|mois)\b")
_DUR_WEEKS_RE = re.compile(r"\b(\d{1,2})\s*(weeks?|semaines?)\b")


def extract_duration(text_norm: str) -> str:
    """Renvoie la duree trouvee sous forme lisible, ou ''. """
    m = re.search(r"\b(\d{1,2})\s*[aà]\s*(\d{1,2})\s*mois\b", text_norm)
    if m:
        return f"{m.group(1)}-{m.group(2)} mois"
    m = re.search(r"\b(\d{1,2})\s*to\s*(\d{1,2})\s*months?\b", text_norm)
    if m:
        return f"{m.group(1)}-{m.group(2)} months"
    m = _DUR_MONTHS_RE.search(text_norm)
    if m:
        return f"{m.group(1)} mois"
    m = _DUR_WEEKS_RE.search(text_norm)
    if m:
        return f"{m.group(1)} semaines"
    if has_phrase(text_norm, "cesure"):
        return "cesure (6 mois)"
    return ""


def classify(offer) -> tuple:
    """Renvoie (categorie, motif) pour une offre.

    L'intitule pese plus lourd que la description : une description peut
    mentionner d'autres programmes de la banque.
    """
    title = norm_text(offer.title)
    desc = norm_text(offer.description_snippet or "")
    full = f"{title} {desc} {norm_text(offer.duration or '')}"

    # 1. Signal explicite dans l'intitule (le plus fiable)
    if has_any(title, SUMMER_PHRASES):
        return SUMMER, "intitule: programme d'ete"
    if has_any(title, OFF_CYCLE_PHRASES):
        return OFF_CYCLE, "intitule: off-cycle / cesure"

    # 2. Signal explicite dans la description
    if has_any(desc, SUMMER_PHRASES):
        return SUMMER, "description: programme d'ete"
    if has_any(desc, OFF_CYCLE_PHRASES):
        return OFF_CYCLE, "description: off-cycle / cesure"

    # 3. Duree
    for pattern in OFF_CYCLE_DURATION_RE:
        if re.search(pattern, full):
            return OFF_CYCLE, "duree >= 4 mois"
    for pattern in SUMMER_DURATION_RE:
        if re.search(pattern, full):
            return SUMMER, "duree <= 12 semaines"

    # 4. Un "stage" francais sans mention explicite d'ete est un stage long.
    #    Attention : "Stage ... Juillet 2026" en France = 6 mois demarrant en
    #    juillet, PAS un summer programme. Ce test passe donc avant les mois.
    if has_any(title, ["stage", "stagiaire"]):
        return OFF_CYCLE, "stage FR (defaut 6 mois)"

    # 5. Mois de demarrage annonce dans un intitule anglophone
    if has_any(title, SUMMER_START_MONTHS):
        return SUMMER, "demarrage juin-aout"
    if has_any(title, OFF_CYCLE_START_MONTHS):
        return OFF_CYCLE, "demarrage hors juin-aout"

    return UNKNOWN, "aucun signal de calendrier"
