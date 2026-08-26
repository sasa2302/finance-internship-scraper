# Parametres HTTP
MIN_DELAY = 1.5  # secondes entre deux requetes
MAX_DELAY = 3.0
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Parametres de scraping
MAX_RESULTS_PER_QUERY = 50
MAX_PAGES = 5

# ---------------------------------------------------------------------------
# BUDGET DE TEMPS
# ---------------------------------------------------------------------------
# Duree maximale de la phase de collecte. Le workflow GitHub Actions a un
# timeout de 45 min : en s'arretant a 30, on garantit qu'un rapport est ecrit.
MAX_RUNTIME_MINUTES = 30

# Part du budget reservee aux sites carriere (le reste va aux agregateurs)
COMPANIES_BUDGET_SHARE = 0.55

# ---------------------------------------------------------------------------
# FRAICHEUR
# ---------------------------------------------------------------------------
# On ne garde que les offres publiees recemment. Une offre sans date de
# publication exploitable est conservee (la deduplication fait le tri).
MAX_OFFER_AGE_DAYS = 30

# Agregateurs
AGGREGATOR_RESULTS_WANTED = 30   # par mot-cle et par site
AGGREGATOR_HOURS_OLD = 72        # offres publiees dans les 72 dernieres heures
AGGREGATOR_MAX_QUERIES = 16      # garde-fou anti rate-limit

# ---------------------------------------------------------------------------
# CAMPAGNE VISEE  (a mettre a jour chaque annee)
# ---------------------------------------------------------------------------
# Summer : uniquement l'ete 2027
TARGET_SUMMER_YEARS = [2027]

# Off-cycle : stages de 6 mois demarrant a partir de janvier 2027
OFF_CYCLE_START_MIN = (2027, 1)   # (annee, mois)

# Une offre dont la periode n'est pas identifiable est CONSERVEE et signalee
# dans la colonne "Periode" du rapport, plutot que jetee en silence.

# Sorties
CSV_DIR = "data"
HASHES_PATH = "data/seen_hashes.json"
RUN_LOG_PATH = "data/run_log.json"

# La geographie ciblee est definie dans config/locations.py
# (AGGREGATOR_SEARCH_LOCATIONS pour les requetes agregateurs)
