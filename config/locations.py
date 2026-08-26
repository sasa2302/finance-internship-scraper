"""Geographie ciblee : places financieres, par ordre de priorite.

Zones acceptees, du plus au moins prioritaire :
  CORE   -> Paris/IDF, Londres, Suisse (Zurich, Geneve, Lausanne), Luxembourg
  EUROPE -> Francfort, Amsterdam, Dublin, Bruxelles, Milan-exclu, Nordiques...
  GLOBAL -> Hong Kong, Singapour, New York, Tokyo, Sydney, Dubai...

Pays explicitement EXCLUS (demande utilisateur) : Espagne, Italie, Portugal.
"""

# ---------------------------------------------------------------------------
# ZONE 1 - COEUR DE CIBLE
# ---------------------------------------------------------------------------
CORE_LOCATIONS = {
    "Paris / IDF": [
        "paris", "la defense", "puteaux", "courbevoie", "nanterre", "levallois",
        "levallois perret", "neuilly", "neuilly sur seine", "issy",
        "issy les moulineaux", "boulogne billancourt", "montrouge", "saint denis",
        "ile de france", "idf", "hauts de seine", "region parisienne",
    ],
    "Londres": [
        "london", "greater london", "city of london", "canary wharf",
        "westminster", "mayfair", "london area",
    ],
    "Suisse": [
        "switzerland", "suisse", "schweiz", "zurich", "zuerich", "geneva",
        "geneve", "genf", "lausanne", "zug", "basel", "bale", "lugano",
        "winterthur", "vaud", "nyon",
    ],
    "Luxembourg": [
        "luxembourg", "luxemburg", "kirchberg",
    ],
}

# ---------------------------------------------------------------------------
# ZONE 2 - RESTE DE L'EUROPE (hors Espagne / Italie / Portugal)
# ---------------------------------------------------------------------------
EUROPE_LOCATIONS = {
    "Allemagne": [
        "germany", "deutschland", "allemagne", "frankfurt", "frankfurt am main",
        "francfort", "munich", "muenchen", "berlin", "hamburg", "duesseldorf",
        "dusseldorf", "stuttgart", "cologne", "koeln", "eschborn",
    ],
    "Irlande": ["ireland", "dublin", "irlande"],
    "Pays-Bas": ["netherlands", "amsterdam", "the hague", "den haag", "rotterdam", "utrecht"],
    "Belgique": ["belgium", "belgique", "brussels", "bruxelles", "brussel", "antwerp", "anvers"],
    "Nordiques": [
        "sweden", "stockholm", "denmark", "copenhagen", "kobenhavn",
        "norway", "oslo", "finland", "helsinki",
    ],
    "Autriche": ["austria", "autriche", "vienna", "wien", "vienne"],
    "Monaco": ["monaco", "monte carlo"],
    "Europe (autre)": [
        "poland", "warsaw", "varsovie", "czech republic", "prague",
        "hungary", "budapest", "malta", "jersey", "guernsey",
        "isle of man", "gibraltar", "liechtenstein", "vaduz",
    ],
}

# ---------------------------------------------------------------------------
# ZONE 3 - PLACES FINANCIERES MONDIALES
# ---------------------------------------------------------------------------
GLOBAL_LOCATIONS = {
    "Hong Kong": ["hong kong", "hongkong", "central hong kong", "kowloon"],
    "Singapour": ["singapore", "singapour", "marina bay"],
    "New York": [
        "new york", "new york city", "nyc", "manhattan", "ny us", "ny usa",
        "wall street", "jersey city", "stamford connecticut",
    ],
    "USA (autre)": ["chicago", "boston", "greenwich connecticut", "stamford"],
    "Japon": ["japan", "japon", "tokyo", "tokio", "marunouchi"],
    "Chine": ["shanghai", "shenzhen", "beijing", "pekin"],
    "Australie": ["australia", "australie", "sydney", "melbourne", "brisbane", "perth"],
    "Moyen-Orient": ["dubai", "difc", "abu dhabi", "doha", "qatar", "riyadh", "saudi arabia"],
    "Canada": ["canada", "toronto", "montreal", "vancouver"],
    # Inde volontairement absente : sites back-office des banques (Mumbai,
    # Pune, Chennai, Noida, Gurugram), hors perimetre front office.
    "Asie (autre)": ["seoul", "south korea", "taipei", "taiwan"],
}

# Poids par zone pour le score de pertinence
ZONE_WEIGHTS = {"CORE": 0.15, "EUROPE": 0.08, "GLOBAL": 0.05, "INCONNU": 0.0}

# ---------------------------------------------------------------------------
# EXCLUSIONS DURES
# ---------------------------------------------------------------------------
# Pays exclus explicitement par l'utilisateur
EXCLUDED_COUNTRIES = {
    "Espagne": [
        "spain", "espagne", "espana", "madrid", "barcelona", "barcelone",
        "valencia", "valence espagne", "bilbao", "seville", "sevilla",
        "malaga", "zaragoza", "murcia", "palma", "alicante", "canary islands",
    ],
    "Italie": [
        "italy", "italie", "italia", "milan", "milano", "rome", "roma",
        "turin", "torino", "naples", "napoli", "bologna", "bologne",
        "florence", "firenze", "venice", "venezia", "genoa", "genova",
        "palermo", "bari", "verona",
    ],
    "Portugal": [
        "portugal", "lisbon", "lisbonne", "lisboa", "porto", "oporto",
        "braga", "coimbra", "faro", "madeira",
    ],
}

# Villes francaises secondaires (hors IDF)
EXCLUDED_FR_CITIES = [
    "toulouse", "lyon", "marseille", "aix en provence", "nantes", "bordeaux",
    "lille", "strasbourg", "montpellier", "rennes", "grenoble", "nice",
    "toulon", "dijon", "clermont ferrand", "saint etienne", "reims", "rouen",
    "metz", "nancy", "orleans", "caen", "angers", "brest", "le mans",
    "amiens", "limoges", "perpignan", "poitiers", "pau", "tours", "besancon",
    "avignon", "cergy", "evry", "melun", "chartres", "le havre", "mulhouse",
]

# Villes UK/IE hors Londres & Dublin
EXCLUDED_UK_CITIES = [
    "edinburgh", "manchester", "birmingham", "glasgow", "leeds", "liverpool",
    "bristol", "cardiff", "belfast", "newcastle", "sheffield", "nottingham",
    "cambridge", "oxford", "southampton", "brighton", "reading", "bournemouth",
    "aberdeen", "coventry", "leicester", "milton keynes", "swindon", "chester",
    "chippenham", "solihull", "kirkcaldy", "hamilton", "bath",
    "weston super mare", "woodham ferrers", "cork", "galway", "limerick",
]

# Indicateurs "pays UK" sans ville (codes LinkedIn/Indeed)
UK_COUNTRY_MARKERS = [
    "united kingdom", "great britain", "england", "scotland", "wales",
    "northern ireland", "eng gb", "sct gb", "wls gb", "nir gb", "gb",
]
UK_ACCEPTED = ["london", "greater london", "city of london", "canary wharf", "london area"]

FRANCE_COUNTRY_MARKERS = ["france", "francais", "francaise"]

# Localisations generiques : on les garde (a trier manuellement)
GENERIC_LOCATIONS = [
    "emea", "europe", "worldwide", "global", "multiple locations",
    "various locations", "locations", "remote", "hybrid", "flexible",
    "teletravail", "plusieurs sites", "international",
]


def _flatten(mapping):
    out = []
    for names in mapping.values():
        out.extend(names)
    return out


ALL_CORE = _flatten(CORE_LOCATIONS)
ALL_EUROPE = _flatten(EUROPE_LOCATIONS)
ALL_GLOBAL = _flatten(GLOBAL_LOCATIONS)
ALL_EXCLUDED_COUNTRY = _flatten(EXCLUDED_COUNTRIES)

# Requetes envoyees aux agregateurs (libelle, code pays Indeed)
AGGREGATOR_SEARCH_LOCATIONS = [
    ("Paris, France", "france"),
    ("London, United Kingdom", "uk"),
    ("Switzerland", "switzerland"),
    ("Luxembourg", "luxembourg"),
    ("Frankfurt, Germany", "germany"),
    ("Amsterdam, Netherlands", "netherlands"),
    ("Dublin, Ireland", "ireland"),
    ("Brussels, Belgium", "belgium"),
    ("Hong Kong", "hong kong"),
    ("Singapore", "singapore"),
    ("New York, NY", "usa"),
    ("Tokyo, Japan", "japan"),
    ("Sydney, Australia", "australia"),
    ("Dubai, United Arab Emirates", "uae"),
]
