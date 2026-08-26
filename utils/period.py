"""Detection de la periode visee par une offre (mois + annee de demarrage).

Sert a ne garder que la campagne qui interesse l'utilisatrice :
  - Summer  : ete 2027 uniquement
  - Off-Cycle : stage de 6 mois demarrant a partir de janvier 2027

Les seuils sont dans config/settings.py (TARGET_SUMMER_YEARS,
OFF_CYCLE_START_MIN) pour etre ajustes d'une annee sur l'autre.
"""

import re
from datetime import date

from utils.textnorm import norm_text, strip_accents

MONTHS = {
    "janvier": 1, "january": 1, "jan": 1,
    "fevrier": 2, "february": 2, "feb": 2, "fev": 2,
    "mars": 3, "march": 3, "mar": 3,
    "avril": 4, "april": 4, "apr": 4, "avr": 4,
    "mai": 5, "may": 5,
    "juin": 6, "june": 6, "jun": 6,
    "juillet": 7, "july": 7, "jul": 7, "juil": 7,
    "aout": 8, "august": 8, "aug": 8,
    "septembre": 9, "september": 9, "sep": 9, "sept": 9,
    "octobre": 10, "october": 10, "oct": 10,
    "novembre": 11, "november": 11, "nov": 11,
    "decembre": 12, "december": 12, "dec": 12,
}

_MONTH_ALT = "|".join(sorted(MONTHS, key=len, reverse=True))

# "juillet 2027", "January 2027", "septembre de 2026"
_MONTH_YEAR = re.compile(rf"\b({_MONTH_ALT})\b(?:\s+(?:de|of))?\s+(20\d{{2}})\b")
# "2027 summer", "2027 | EMEA | London"
_YEAR_MONTH = re.compile(rf"\b(20\d{{2}})\s+({_MONTH_ALT})\b")
# 01/2027, 01-2027, 2027-01
_NUM_MY = re.compile(r"\b(0?[1-9]|1[0-2])[/-](20\d{2})\b")
_NUM_YM = re.compile(r"\b(20\d{2})-(0?[1-9]|1[0-2])\b")
_YEAR = re.compile(r"\b(20\d{2})\b")

# Un intitule "Summer 2027" designe l'ete : on l'assimile a juin.
SUMMER_MONTH = 6

# Fenetre d'annees credibles pour une campagne de stage. Sans cette borne, un
# numero de telephone ou une adresse ("2007") etait lu comme une annee de
# demarrage et faisait rejeter l'offre a tort.
_YEAR_MIN = date.today().year - 1
_YEAR_MAX = date.today().year + 5


def _plausible(year) -> bool:
    return _YEAR_MIN <= year <= _YEAR_MAX


def _norm_keep_separators(text: str) -> str:
    """Minuscules sans accents, mais en gardant / et - .

    norm_text remplace toute la ponctuation par des espaces, ce qui detruisait
    les dates numeriques ("01/2027" devenait "01 2027").
    """
    return re.sub(r"\s+", " ", strip_accents(str(text)).lower()).strip()


def extract_period(text: str):
    """Renvoie (annee, mois|None) pour la periode de demarrage, ou None.

    Le mois-annee explicite l'emporte sur l'annee seule.
    """
    if not text:
        return None
    t = norm_text(text)
    raw = _norm_keep_separators(text)
    if not t:
        return None

    m = _MONTH_YEAR.search(t)
    if m and _plausible(int(m.group(2))):
        return int(m.group(2)), MONTHS[m.group(1)]

    m = _YEAR_MONTH.search(t)
    if m and _plausible(int(m.group(1))):
        return int(m.group(1)), MONTHS[m.group(2)]

    m = _NUM_YM.search(raw)
    if m and _plausible(int(m.group(1))):
        return int(m.group(1)), int(m.group(2))

    m = _NUM_MY.search(raw)
    if m and _plausible(int(m.group(2))):
        return int(m.group(2)), int(m.group(1))

    years = [int(y) for y in _YEAR.findall(t) if _plausible(int(y))]
    if years:
        # Plusieurs annees ("campagne 2026 2027") : on retient la plus tardive,
        # qui correspond a la campagne ouverte.
        return max(years), None

    return None


def detect_period(offer):
    """Periode de l'offre : l'intitule prime sur la description."""
    return extract_period(offer.title) or extract_period(offer.description_snippet or "")


def format_period(period) -> str:
    if not period:
        return ""
    year, month = period
    if month is None:
        return str(year)
    names = {v: k for k, v in [("janvier", 1), ("fevrier", 2), ("mars", 3),
                               ("avril", 4), ("mai", 5), ("juin", 6),
                               ("juillet", 7), ("aout", 8), ("septembre", 9),
                               ("octobre", 10), ("novembre", 11), ("decembre", 12)]}
    return f"{names.get(month, month)} {year}"


def summer_ok(period, target_years) -> tuple:
    """Un summer sans annee identifiee est conserve, mais signale."""
    if period is None:
        return True, "annee non identifiee"
    year, _ = period
    if year in target_years:
        return True, ""
    return False, f"summer {year} (cible : {'/'.join(map(str, target_years))})"


def off_cycle_ok(period, minimum) -> tuple:
    """minimum = (annee, mois). Un stage sans date identifiee est conserve."""
    if period is None:
        return True, "date non identifiee"
    year, month = period
    min_year, min_month = minimum
    if year > min_year:
        return True, ""
    if year < min_year:
        return False, f"demarrage {year} (cible : a partir de {min_month:02d}/{min_year})"
    # Meme annee : sans mois precis on garde, le doute profite a l'offre
    if month is None or month >= min_month:
        return True, ""
    return False, f"demarrage {month:02d}/{year} (cible : a partir de {min_month:02d}/{min_year})"
