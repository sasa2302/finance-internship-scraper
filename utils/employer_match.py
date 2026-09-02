"""Reconnaissance de l'employeur : est-ce bien de la finance de marche ?

Logique (whitelist d'abord, contrairement a l'ancienne blacklist) :
  1. Nom present dans la blacklist dure (retail, hotels, tech, conseil...) -> REJET
  2. Nom present dans la whitelist finance de marche               -> ACCEPTE + categorie
  3. Nom inconnu MAIS intitule portant un signal marche fort       -> ACCEPTE ("A verifier")
  4. Sinon                                                          -> REJET
"""

from config.employers import (
    EMPLOYER_CATEGORIES,
    HARD_NON_FINANCE,
    STRONG_MARKET_SIGNALS,
)
from utils.textnorm import norm_company, norm_text, has_phrase, first_match

UNVERIFIED = "A verifier (signal marche)"

# Index pre-calcule : phrase -> categorie, du plus long au plus court pour que
# "citadel securities" l'emporte sur "citadel".
_INDEX = sorted(
    ((name, category) for category, names in EMPLOYER_CATEGORIES.items() for name in names),
    key=lambda item: -len(item[0]),
)


def match_employer(company: str):
    """Renvoie (categorie, nom_whitelist) ou (None, None).

    On teste DEUX formes du nom : avec et sans les suffixes juridiques.
    Le retrait des suffixes aide pour "Barclays PLC" -> "barclays", mais il
    casse les entrees de whitelist qui contiennent justement ce suffixe :
    "Man Group" devenait "man" et ne matchait plus "man group". Meme probleme
    pour CME Group et Fidelity International.
    """
    stripped = norm_company(company)
    full = norm_text(company)
    if not stripped and not full:
        return None, None
    for name, category in _INDEX:
        if has_phrase(full, name) or has_phrase(stripped, name):
            return category, name
    return None, None


def is_hard_non_finance(company: str) -> bool:
    cnorm = norm_company(company)
    if not cnorm:
        return False
    return first_match(cnorm, HARD_NON_FINANCE) is not None


def strong_market_signal(offer) -> str:
    """Signal marche fort trouve dans l'intitule, sinon ''."""
    return first_match(norm_text(offer.title), STRONG_MARKET_SIGNALS) or ""


def classify_employer(offer):
    """Renvoie (accepte: bool, categorie: str, motif: str)."""
    company = offer.company or ""

    if is_hard_non_finance(company):
        return False, "", "employeur hors finance de marche"

    category, matched = match_employer(company)
    if category:
        return True, category, f"whitelist: {matched}"

    signal = strong_market_signal(offer)
    if signal:
        if not company.strip():
            # Offre issue d'un site carriere de banque : societe deja connue en amont
            return True, UNVERIFIED, f"signal marche: {signal}"
        return True, UNVERIFIED, f"signal marche: {signal}"

    return False, "", "employeur inconnu, aucun signal marche"
