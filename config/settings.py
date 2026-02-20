# HTTP client settings
MIN_DELAY = 1.5  # seconds between requests
MAX_DELAY = 3.0
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30  # seconds

# Scraping settings
MAX_RESULTS_PER_QUERY = 50  # max results to fetch per keyword query
MAX_PAGES = 5  # max pagination pages per query

# Aggregator settings
AGGREGATOR_RESULTS_WANTED = 30  # per keyword per site
AGGREGATOR_HOURS_OLD = 72  # only jobs posted in last 72 hours

# Output settings
CSV_PATH = "data/internships.csv"
HASHES_PATH = "data/seen_hashes.json"
RUN_LOG_PATH = "data/run_log.json"

# Locations to search
LOCATIONS = ["France", "United Kingdom", "Paris", "London"]
