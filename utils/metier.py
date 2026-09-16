"""Metier d'une offre, deduit de l'intitule.

Sert a deux choses :
  - ecarter les postes quant / tech (profil non vise) ;
  - afficher une colonne "Metier" et classer le front office en tete.
"""

from config.keywords import QUANT_TECH_TERMS
from utils.textnorm import norm_text, has_any

FRONT = {
    "Sales": ["sales", "vente", "coverage", "distribution", "marketer"],
    "Trading": ["trading", "trader", "execution", "market making", "market maker", "delta one"],
    "Structuration": ["structuring", "structuration", "structurer", "structured products",
                      "produits structures", "solutions"],
}
OTHERS = [
    # Ordre voulu : un "Middle Office Fixed Income" est un poste de support,
    # pas un poste Global Markets generique.
    ("Risque / Controle", ["risk", "risque", "control", "controls", "controle", "credit analyst",
                           "middle office", "back office", "valuation", "product control",
                           "operations", "business management", "chief operating office"]),
    ("Recherche / Strategie", ["research", "strategy", "strategist", "economist",
                               "analyste financier"]),
    ("Global Markets", ["global markets", "markets", "salle des marches", "fixed income",
                        "equities", "derivatives", "fx", "rates", "commodities", "credit",
                        "prime brokerage", "prime services", "securities financing", "xva",
                        "securitisation", "securitization", "alm", "treasury"]),
    ("Gestion (buy-side)", ["portfolio management", "fund management", "gestion",
                            "hedge fund", "equity analyst", "investment analyst"]),
]
PRIORITY = {"Sales": 0, "Trading": 0, "Structuration": 0, "Global Markets": 1,
            "Gestion (buy-side)": 2, "Recherche / Strategie": 2,
            "Risque / Controle": 3, "Autre": 4}


def is_quant_or_tech(title: str) -> bool:
    return has_any(norm_text(title), QUANT_TECH_TERMS)


def classify_metier(title: str) -> str:
    t = norm_text(title)
    front = [label for label, terms in FRONT.items() if has_any(t, terms)]
    if front:
        return " / ".join(front)
    for label, terms in OTHERS:
        if has_any(t, terms):
            return label
    return "Autre"


def metier_priority(label: str) -> int:
    first = (label or "Autre").split(" / ")[0]
    return PRIORITY.get(first, 4)
