# Parametres HTTP
MIN_DELAY = 1.5  # secondes entre deux requetes
MAX_DELAY = 3.0
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Parametres de scraping
MAX_RESULTS_PER_QUERY = 50
MAX_PAGES = 5

# Agregateurs
AGGREGATOR_RESULTS_WANTED = 30   # par mot-cle et par site
AGGREGATOR_HOURS_OLD = 72        # offres publiees dans les 72 dernieres heures
AGGREGATOR_MAX_QUERIES = 16      # garde-fou anti rate-limit

# Sorties
CSV_DIR = "data"
HASHES_PATH = "data/seen_hashes.json"
RUN_LOG_PATH = "data/run_log.json"

# La geographie ciblee est definie dans config/locations.py
# (AGGREGATOR_SEARCH_LOCATIONS pour les requetes agregateurs)
