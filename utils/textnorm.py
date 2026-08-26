"""Normalisation de texte partagee par les filtres (accents, casse, suffixes juridiques)."""

import re
import unicodedata

# Suffixes juridiques / corporatifs a retirer d'un nom d'entreprise
_LEGAL_SUFFIXES = [
    "sa", "sas", "sasu", "sarl", "snc", "scs", "sca", "plc", "ltd", "limited",
    "llc", "llp", "lp", "inc", "incorporated", "corp", "corporation", "co",
    "gmbh", "ag", "nv", "bv", "ab", "as", "oy", "spa", "srl", "pte", "pty",
    "kk", "holding", "holdings", "group", "groupe", "international",
    "france", "uk", "europe", "emea", "global", "company",
]

_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WS_RE = re.compile(r"\s+")


def strip_accents(text: str) -> str:
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def norm_text(text: str) -> str:
    """Minuscules, sans accents, ponctuation -> espace, espaces normalises."""
    if not text:
        return ""
    text = strip_accents(str(text)).lower()
    text = _PUNCT_RE.sub(" ", text)
    return _WS_RE.sub(" ", text).strip()


def norm_company(name: str) -> str:
    """Nom d'entreprise normalise, suffixes juridiques retires."""
    base = norm_text(name)
    if not base:
        return ""
    tokens = [t for t in base.split() if t not in _LEGAL_SUFFIXES]
    # Ne jamais tout vider (ex: "ING Group" -> "ing")
    return " ".join(tokens) if tokens else base


def has_phrase(haystack_norm: str, phrase: str) -> bool:
    """Recherche d'une expression avec frontieres de mots.

    Evite les faux positifs du `in` brut : "roma" ne matche plus "romania",
    "75" ne matche plus "1975", "ey" ne matche plus "money".
    """
    p = norm_text(phrase)
    if not p:
        return False
    pattern = r"(?<![a-z0-9])" + r"\s+".join(re.escape(w) for w in p.split()) + r"(?![a-z0-9])"
    return re.search(pattern, haystack_norm) is not None


def has_any(haystack_norm: str, phrases) -> bool:
    return any(has_phrase(haystack_norm, p) for p in phrases)


def first_match(haystack_norm: str, phrases):
    for p in phrases:
        if has_phrase(haystack_norm, p):
            return p
    return None
