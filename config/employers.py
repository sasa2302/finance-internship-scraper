"""Whitelist des employeurs de FINANCE DE MARCHE.

Remplace l'ancienne blacklist (qui laissait passer supermarches, hotels, retail,
tech...). Principe : une offre n'est retenue que si l'employeur appartient a
l'univers finance de marche -- banques (BFI / global markets), hedge funds,
prop trading / market makers, brokers, asset managers, bourses & infrastructure.
"""

# ---------------------------------------------------------------------------
# BANQUES (BFI / salle des marches)
# ---------------------------------------------------------------------------
BANKS = [
    # US
    "goldman sachs", "morgan stanley", "jp morgan", "jpmorgan", "j p morgan",
    "bank of america", "merrill lynch", "bofa", "citi", "citigroup", "citibank",
    "wells fargo", "jefferies", "cantor fitzgerald", "evercore", "houlihan",
    "raymond james", "stifel", "piper sandler", "bny mellon", "bank of new york",
    "state street", "northern trust",
    # UK / Irlande
    "barclays", "hsbc", "natwest", "natwest markets", "lloyds", "standard chartered",
    "schroders", "investec", "close brothers", "peel hunt", "numis",
    # France
    "bnp paribas", "societe generale", "sg cib", "natixis", "credit agricole",
    "ca cib", "cacib", "credit agricole cib", "exane", "kepler cheuvreux",
    "oddo bhf", "credit mutuel", "cic", "cic market solutions", "arkea",
    "bred", "banque populaire", "caisse d epargne", "la banque postale", "bpce",
    "banque de france",
    "caisse des depots", "cdc", "bpifrance", "coface", "portzamparc",
    "lazard", "rothschild",
    # Allemagne / Autriche / Suisse
    "deutsche bank", "commerzbank", "berenberg", "dz bank", "landesbank",
    "helaba", "lbbw", "bayernlb", "pfandbriefbank", "erste group", "raiffeisen",
    "ubs", "credit suisse", "julius baer", "pictet", "lombard odier", "vontobel",
    "mirabaud", "union bancaire privee", "ubp", "syz", "reyl", "bordier",
    "safra sarasin", "edmond de rothschild", "banque cantonale", "zkb",
    "zuercher kantonalbank", "efg international",
    # Benelux / Nordics
    "ing", "abn amro", "rabobank", "kbc", "belfius", "degroof petercam",
    "van lanschot", "nordea", "seb", "skandinaviska", "danske bank", "dnb",
    "svenska handelsbanken", "handelsbanken", "swedbank",
    # Asie / Japon
    "nomura", "mizuho", "smbc", "sumitomo mitsui", "mufg", "mitsubishi ufj",
    "daiwa", "bank of china", "icbc", "china merchants securities",
    "citic securities", "haitong", "cicc", "china international capital",
    "dbs bank", "ocbc", "uob", "united overseas bank", "nomura securities",
    # Canada / Australie
    "macquarie", "rbc capital markets", "royal bank of canada", "bmo capital markets",
    "scotiabank", "td securities", "cibc", "national bank financial",
    "anz", "westpac", "commonwealth bank", "nab", "national australia bank",
    # Autres europeens presents a Londres/Paris
    "unicredit", "mediobanca", "santander", "bbva", "generali",
]

# ---------------------------------------------------------------------------
# HEDGE FUNDS
# ---------------------------------------------------------------------------
HEDGE_FUNDS = [
    "millennium management", "millennium capital", "citadel", "point72",
    "balyasny", "brevan howard", "capula", "marshall wace", "eisler capital",
    "squarepoint", "winton", "capital fund management", "cfm",
    "exoduspoint", "aspect capital", "bridgewater", "aqr capital", "worldquant",
    "man group", "man ahl", "two sigma", "de shaw", "d e shaw",
    "renaissance technologies", "elliott management", "elliott investment",
    "davidson kempner", "baupost", "third point", "pershing square",
    "tci fund", "lansdowne partners", "egerton capital", "cheyne capital",
    "chenavari", "syquant", "h2o asset management", "boussard gavaudan",
    "laffitte capital", "metori capital", "gsa capital", "systematica",
    "verition", "schonfeld", "hudson bay capital", "garda capital",
    "qube research", "qrt", "tudor investment", "moore capital",
    "caxton associates", "rokos capital", "astaris", "kite lake",
    "sandbar asset", "florin court", "quadrature capital", "silex investment",
    "tikehau capital", "amiral gestion", "eleva capital", "melqart",
]

# ---------------------------------------------------------------------------
# PROP TRADING / MARKET MAKERS
# ---------------------------------------------------------------------------
PROP_FIRMS = [
    "jane street", "jump trading", "optiver", "imc trading", "imc financial",
    "flow traders", "susquehanna", "sig susquehanna", "drw", "drw trading",
    "tower research", "hudson river trading", "xtx markets",
    "citadel securities", "virtu financial", "five rings", "headlands technologies",
    "akuna capital", "maven securities", "da vinci derivatives", "wolverine trading",
    "belvedere trading", "old mission capital", "cutler group", "mako trading",
    "quantlab", "radix trading", "tibra", "eclipse trading", "grasshopper",
    "vatic labs", "transmarket", "group one trading", "vivienne court",
    "ampersand trading", "liquid capital", "cheshire trading", "arrowstreet capital",
    # Market makers crypto / actifs numeriques
    "wintermute", "gsr markets", "gsr", "b2c2", "cumberland drw", "galaxy digital",
    "falconx", "amber group", "keyrock", "flowdesk", "talos global", "talos",
]

# ---------------------------------------------------------------------------
# BROKERS / INTERDEALER / EXECUTION
# ---------------------------------------------------------------------------
BROKERS = [
    "tp icap", "icap", "tullett prebon", "tradition", "compagnie financiere tradition",
    "tsaf", "bgc partners", "aurel bgc", "gfi group", "viel", "hpc sa",
    "market securities", "louis capital markets", "octo finances",
    "sucden financial", "marex", "stonex", "ed f man capital", "otc flow",
    "ig group", "cmc markets", "saxo bank", "interactive brokers",
    "plus500", "xtb", "oddo securities", "magen financial", "feefty",
]

# ---------------------------------------------------------------------------
# ASSET MANAGERS orientes marches
# ---------------------------------------------------------------------------
ASSET_MANAGERS = [
    "amundi", "blackrock", "vanguard", "pimco", "fidelity international",
    "fidelity investments", "aviva investors", "axa investment managers", "axa im",
    "allianz global investors", "dws", "invesco", "janus henderson",
    "columbia threadneedle", "m g investments", "abrdn", "legal general investment",
    "lgim", "robeco", "candriam", "carmignac", "comgest",
    "la financiere de l echiquier", "lazard asset management", "ostrum",
    "cpr asset management", "sycomore", "dnca", "groupama asset management",
    "la francaise", "bnp paribas asset management", "natixis investment managers",
    "generali investments", "state street global advisors", "ssga",
    "wellington management", "t rowe price", "capital group", "franklin templeton",
    "nuveen", "neuberger berman", "alliancebernstein",
    "goldman sachs asset management", "pgim", "mfs investment",
    "first eagle", "eurizon", "swiss life asset managers", "unigestion",
    "rothschild asset management", "edmond de rothschild asset management",
    "montpensier", "moneta asset management", "varenne capital",
]

# ---------------------------------------------------------------------------
# BOURSES / INFRASTRUCTURE / DATA / EDITEURS SALLE DES MARCHES
# ---------------------------------------------------------------------------
EXCHANGES_INFRA = [
    "euronext", "lseg", "london stock exchange", "deutsche boerse", "eurex",
    "cme group", "intercontinental exchange", "ice futures", "nasdaq", "cboe",
    "hkex", "hong kong exchanges", "sgx", "singapore exchange", "six group",
    "six swiss exchange", "tradeweb", "marketaxess", "bloomberg", "refinitiv",
    "msci", "s p global", "moody s", "ftse russell", "clearstream", "euroclear",
    "lch", "dtcc", "murex", "finastra", "ion trading", "calypso technology",
    "numerix", "quantifi", "opensee", "kaiko", "acadia", "osttra",
]

# ---------------------------------------------------------------------------
# INSTITUTIONS / REGULATEURS avec activite de marche
# ---------------------------------------------------------------------------
INSTITUTIONS = [
    "banque de france", "european central bank", "banque centrale europeenne",
    "bce", "esma", "amf", "autorite des marches financiers",
    "bank for international settlements", "bis", "european investment bank",
    "eib", "european stability mechanism", "esm", "agence france tresor",
    "inter american development bank", "asian development bank",
    "african development bank", "international finance corporation",
    "international monetary fund", "imf",
    "world bank treasury", "ebrd", "swiss national bank", "bank of england",
]

# Categorie affichee dans le rapport -> liste de noms
EMPLOYER_CATEGORIES = {
    "Banque / BFI": BANKS,
    "Hedge Fund": HEDGE_FUNDS,
    "Prop Trading / Market Maker": PROP_FIRMS,
    "Broker": BROKERS,
    "Asset Manager": ASSET_MANAGERS,
    "Bourse / Infrastructure": EXCHANGES_INFRA,
    "Institution": INSTITUTIONS,
}

# ---------------------------------------------------------------------------
# Signaux "forts" de finance de marche dans un intitule de poste.
# Servent de porte de secours pour une societe legitime absente de la whitelist
# (petit fonds, boutique de trading, filiale peu connue).
# ---------------------------------------------------------------------------
STRONG_MARKET_SIGNALS = [
    "sales trader", "trading desk", "salle des marches", "front office markets",
    "global markets", "capital markets", "equity derivatives", "derives actions",
    "fixed income", "taux et credit", "rates trading", "credit trading",
    "fx trading", "commodities trading", "energy trading", "power trading",
    "structuring", "structuration", "produits structures", "structured products",
    "market making", "market maker", "tenue de marche", "delta one",
    "quantitative trading", "quantitative research", "quantitative analyst",
    "quant trader", "quant researcher", "quantitative strategist",
    "derivatives pricing", "pricing derives", "exotic derivatives", "exotics desk",
    "flow trading", "prime brokerage", "prime services", "securities financing",
    "repo trading", "volatility trading", "vol trading", "xva", "counterparty risk",
    "market risk", "risque de marche", "portfolio manager", "gestion de portefeuille",
    "hedge fund", "proprietary trading", "systematic trading", "algorithmic trading",
    "trading algorithmique", "electronic trading", "execution trading",
    "asset liability management", "alm trading", "middle office marches",
]

# Secteurs a rejeter meme si un signal fort apparait (retail, hotellerie, tech...).
HARD_NON_FINANCE = [
    # Grande distribution / retail
    "sainsbury", "tesco", "asda", "waitrose", "morrisons", "aldi", "lidl",
    "carrefour", "auchan", "leclerc", "intermarche", "monoprix", "franprix",
    "casino guichard", "marks spencer", "john lewis", "boots", "argos",
    "primark", "zara", "h m", "uniqlo", "decathlon", "ikea", "leroy merlin",
    "castorama", "action", "b m stores", "poundland",
    # Luxe / mode / cosmetique
    "lvmh", "kering", "hermes", "chanel", "dior", "gucci", "sephora",
    "l oreal", "louis vuitton", "balenciaga", "saint laurent", "bottega veneta",
    "cartier", "tiffany", "burberry", "prada", "richemont", "swatch",
    "nike", "adidas", "puma", "asos", "zalando", "shein", "temu",
    # FMCG / agro
    "danone", "nestle", "unilever", "procter gamble", "mondelez", "kraft",
    "coca cola", "pepsico", "ferrero", "mars incorporated", "colgate",
    "henkel", "reckitt", "heineken", "ab inbev", "pernod ricard",
    # Tech grand public
    "amazon", "apple", "google", "microsoft", "meta platforms", "facebook",
    "tiktok", "bytedance", "uber", "airbnb", "booking com", "spotify",
    "netflix", "tesla", "salesforce", "sap se", "shopify", "snap inc",
    # Conseil / audit
    "accenture", "capgemini", "deloitte", "pwc", "pricewaterhouse", "kpmg",
    "ernst young", "mckinsey", "bain company", "boston consulting",
    "oliver wyman", "roland berger", "simon kucher", "wavestone", "sia partners",
    "alvarez marsal", "mazars", "grant thornton", "bdo",
    # Immobilier / hotellerie / tourisme
    "allsopp", "kew green", "accor", "marriott", "hilton", "hyatt",
    "trivago", "aviareps", "century 21", "foncia", "nexity", "orpi",
    "knight frank", "savills", "jll", "cbre",
    # Energie / industrie / transport / sante / telecom / medias
    "edf", "engie", "totalenergies", "veolia", "suez", "sncf", "ratp",
    "air france", "airbus", "renault", "stellantis", "michelin", "valeo",
    "sanofi", "pfizer", "novartis", "roche holding", "astrazeneca", "bayer",
    "orange", "bouygues", "sfr", "iliad", "vivendi", "tf1", "canal",
    # Restauration
    "mcdonald", "burger king", "starbucks", "subway", "domino s pizza", "flunch",
    # ONG / associatif / social
    "croix rouge", "red cross", "medecins sans frontieres", "unicef",
    "amnesty", "oxfam", "secours populaire", "secours catholique", "emmaus",
    "restos du coeur", "apprentis d auteuil", "oeuvre de secours",
    # Assurance non-marches
    "maif", "matmut", "macif", "groupama assurances", "mma", "mutuelle",
    # Divers vus dans les anciens scrapes
    "red bird enterprises", "shared humanity", "jobster", "flogas",
    "negu enterprises", "kartaca", "aviareps india",
]
