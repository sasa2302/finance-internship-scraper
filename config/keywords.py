"""Mots-cles metier et exclusions d'intitules.

NB : les listes d'employeurs vivent dans config/employers.py (whitelist) et les
listes geographiques dans config/locations.py. Ce fichier ne traite que le
METIER et le TYPE DE CONTRAT.

Tous les tests sont faits avec frontieres de mots (utils.textnorm.has_phrase),
donc plus de faux positifs du type "sea" qui matchait "reSEArch".
"""

# ---------------------------------------------------------------------------
# METIERS DE FINANCE DE MARCHE
# ---------------------------------------------------------------------------
ROLE_KEYWORDS = [
    # Trading / Sales / Structuration
    "trading", "trader", "sales", "sales trading", "structuration", "structuring",
    "derivatives", "derives", "fixed income", "taux", "credit", "equity",
    "equity derivatives", "flow trading", "exotic", "exotics", "global markets",
    "capital markets", "commodities", "matieres premieres", "fx", "forex",
    "change", "interest rate", "rates", "volatility", "volatilite", "pricing",
    "front office", "middle office", "market making", "market maker",
    "electronic trading", "algo trading", "algorithmic trading", "delta one",
    "securitisation", "securitization", "titrisation", "repo",
    "securities financing", "prime brokerage", "prime services",
    "structured products", "produits structures", "cash equity", "etf",
    "salle des marches", "execution", "syndication", "primary markets",
    # Quant / Risque
    "quant", "quantitative", "quantitative analyst", "quantitative research",
    "quant research", "quant trading", "quantitative developer", "xva",
    "risk management", "market risk", "risque de marche", "counterparty risk",
    "risque de contrepartie", "credit risk", "risk quant", "model validation",
    "validation de modeles", "alm", "asset liability management",
    # Gestion / Buy-side
    "portfolio management", "gestion de portefeuille", "asset allocation",
    "fund management", "hedge fund", "alternative investments", "absolute return",
    "long short", "systematic", "macro trading", "global macro",
    "multi strategy", "multi-strategy", "fund of funds", "overlay",
    # Recherche
    "equity research", "credit research", "macro research", "strategist",
    "strategie de marche", "economic research",
]

# ---------------------------------------------------------------------------
# TYPE DE CONTRAT
# ---------------------------------------------------------------------------
INTERNSHIP_PREFIXES_FR = ["stage", "stagiaire", "cesure", "cesure"]
INTERNSHIP_PREFIXES_EN = [
    "internship", "intern", "summer analyst", "summer associate",
    "industrial placement", "placement year", "placement programme",
    "summer placement",
    "off cycle", "off-cycle", "industrial placement", "insight programme",
    "spring week", "trainee",
]

# Ce qui n'est PAS un stage (teste sur le champ job_type)
NON_STAGE_TYPES = [
    "full time", "fulltime", "permanent", "cdi", "cdd", "alternance",
    "apprenticeship", "contrat pro", "freelance", "contractor", "temporary",
    "interim", "vie",
]

# Durees a exclure : 12 mois et plus, alternance
EXCLUDE_DURATION_PATTERNS = [
    r"\b12\s*mois\b", r"\b12\s*months?\b", r"\btwelve\s*months?\b",
    r"\b(18|24|36)\s*mois\b", r"\b(18|24|36)\s*months?\b",
    r"\b1\s*an\b", r"\b(1|one)\s*year\s*(contract|programme|program)\b",
    r"\balternance\b", r"\bapprenti", r"\bcontrat\s*pro",
    r"\bcontrat\s*d.apprentissage\b",
]

# ---------------------------------------------------------------------------
# INTITULES A EXCLURE
# ---------------------------------------------------------------------------
# Seniorite / contrat / experience requise
EXCLUDE_KEYWORDS = [
    "cdi", "cdd", "permanent", "experienced hire", "senior", "director",
    "vp", "vice president", "head of", "managing director", "executive",
    "principal", "full time", "temps plein", "freelance", "contractor",
    "interimaire", "interim",
    "1 3 ans", "1 3 years", "2 5 years", "3 years experience",
    "5 years experience", "10 years experience", "experience requise",
    "experience souhaitee", "years of experience", "ans d experience",
    # Alternance / VIE
    "alternance", "alternant", "apprenti", "contrat pro",
    "contrat d apprentissage", "professionnalisation",
    "v i e", "vie", "volontariat international",
]

# Metiers hors finance de marche
EXCLUDE_TITLE_KEYWORDS = [
    # Corporate finance / M&A / PE -- pas de la finance de marche
    "m a", "mergers", "acquisitions", "private equity", "venture capital",
    "leveraged finance", "corporate finance", "corporate banking",
    "investment banking", "ibd", "advisory", "ecm", "dcm",
    "debt capital markets", "equity capital markets", "origination",
    "restructuring advisory",
    "transaction services", "due diligence", "project finance",
    "real estate", "immobilier", "infrastructure finance",
    "private investments", "private credit", "private debt",
    "direct lending", "growth equity", "buyout",
    # Gestion privee / patrimoine / ESG -- hors perimetre
    "gestion privee", "private banking", "wealth management", "patrimoine",
    "patrimonial", "banque privee", "conseiller clientele", "esg", "isr",
    "sustainable finance", "impact investing", "responsable investissement",
    "developpement gestion",
    # Retail / commerce
    "retail sales", "sales assistant", "sales negotiator", "sales coordinator",
    "sales office", "trading assistant", "trading store", "business development",
    "account manager", "vente", "vendeur", "vendeuse", "chef de rayon",
    "responsable magasin", "store manager", "merchandiser", "monetisation",
    "monetization", "telesales", "inside sales", "field sales",
    # Fonctions support
    "marketing", "communication", "ressources humaines", "human resources",
    "recruitment", "talent acquisition", "supply chain", "logistics",
    "logistique", "it support", "helpdesk", "comptabilite", "accounting",
    "controle de gestion", "audit", "compliance", "conformite", "legal",
    "juridique", "fiscalite", "tax", "relation client", "customer service",
    "after sales", "facilities", "procurement", "achats",
    # Tech generique (hors quant)
    "data engineer", "data scientist", "software engineer", "developpeur",
    "developer", "devops", "cloud engineer", "cybersecurity", "mechanical engineer",
    "support engineer", "platform engineer", "infrastructure engineer",
    "site reliability", "qa engineer", "fpga", "hardware", "asic",
    "network engineer", "systems engineer", "linux", "web scraping",
    # Fonctions internes des salles de marche, hors metier
    "leadership rotation", "campus recruiter", "recruiting", "recruiter",
    "people team", "office experience",
    "go to market", "founder s associate", "founder associate",
    # Projet / design / contenu
    "chef de projet", "project manager", "product manager", "product owner",
    "scrum master", "ux designer", "ui designer", "graphiste", "graphic design",
    "content manager", "community manager", "social media", "seo", "sea",
    "journalist", "videographer", "copywriter",
    # Social / associatif / sante
    "social worker", "educateur", "infirmier", "aide soignant", "animateur",
    "benevole", "volunteer", "charity", "humanitarian", "humanitaire",
    "associatif", "travailleur social",
    # Divers
    "strategy operations", "business operations", "office manager",
]
