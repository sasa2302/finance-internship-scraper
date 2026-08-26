"""Filtrage geographique : places financieres ciblees.

Renvoie une zone (CORE / EUROPE / GLOBAL / INCONNU) et un libelle lisible
("Paris / IDF", "Londres", "Hong Kong"...) utilise dans le rapport Excel.
"""

from config.locations import (
    CORE_LOCATIONS, EUROPE_LOCATIONS, GLOBAL_LOCATIONS,
    EXCLUDED_COUNTRIES, EXCLUDED_FR_CITIES, EXCLUDED_UK_CITIES,
    UK_COUNTRY_MARKERS, UK_ACCEPTED, FRANCE_COUNTRY_MARKERS,
    GENERIC_LOCATIONS, ZONE_WEIGHTS,
)
from utils.textnorm import norm_text, has_phrase, has_any

CORE, EUROPE, GLOBAL, INCONNU = "CORE", "EUROPE", "GLOBAL", "INCONNU"

# (zone, libelle, phrases) trie du plus specifique au plus general
_ZONES = (
    [(CORE, label, names) for label, names in CORE_LOCATIONS.items()]
    + [(EUROPE, label, names) for label, names in EUROPE_LOCATIONS.items()]
    + [(GLOBAL, label, names) for label, names in GLOBAL_LOCATIONS.items()]
)


def match_zone(loc_norm: str):
    """Renvoie (zone, libelle) pour une localisation deja normalisee."""
    if not loc_norm:
        return INCONNU, "Non precise"
    for zone, label, names in _ZONES:
        if has_any(loc_norm, names):
            return zone, label
    return INCONNU, "Non reconnu"


def evaluate(location: str):
    """Renvoie (accepte, zone, libelle, motif).

    L'ordre compte : une ville explicitement acceptee l'emporte sur les
    marqueurs pays. Sans cela "Sydney, New South Wales" etait rejete comme
    britannique a cause du mot "Wales".
    """
    loc = norm_text(location)
    if not loc:
        return True, INCONNU, "Non precise", "localisation a confirmer"

    # 1. Pays exclus explicitement (Espagne / Italie / Portugal)
    for country, cities in EXCLUDED_COUNTRIES.items():
        if has_any(loc, cities):
            return False, "", "", f"pays exclu ({country})"

    # 2. Villes explicitement hors perimetre (France hors IDF, UK hors Londres)
    if has_any(loc, EXCLUDED_FR_CITIES) and not has_any(loc, CORE_LOCATIONS["Paris / IDF"]):
        return False, "", "", "ville francaise hors IDF"
    if has_any(loc, EXCLUDED_UK_CITIES) and not has_any(loc, UK_ACCEPTED):
        return False, "", "", "UK/IE hors Londres-Dublin"

    # 3. Place financiere ciblee reconnue -> on garde
    zone, label = match_zone(loc)
    if zone != INCONNU:
        return True, zone, label, ""

    # 4. Marqueur pays sans ville reconnue : les villes hors perimetre ont deja
    #    ete ecartees a l'etape 2, donc on garde en signalant l'imprecision.
    if has_any(loc, UK_COUNTRY_MARKERS):
        return True, INCONNU, "UK (a preciser)", "localisation a confirmer"
    if has_any(loc, FRANCE_COUNTRY_MARKERS):
        return True, INCONNU, "France (a preciser)", "localisation a confirmer"

    # 5. Libelle generique (EMEA, remote, multi-sites)
    if has_any(loc, GENERIC_LOCATIONS):
        return True, INCONNU, "Generique (EMEA/remote)", "localisation a confirmer"

    return False, "", "", "hors places financieres ciblees"


def zone_bonus(zone: str) -> float:
    return ZONE_WEIGHTS.get(zone or INCONNU, 0.0)
