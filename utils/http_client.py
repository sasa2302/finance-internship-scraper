import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import random
import logging

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class HttpClient:
    def __init__(self, min_delay=1.0, max_delay=3.0, max_retries=3, timeout=30):
        self.session = requests.Session()
        retry = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.timeout = timeout

    def _delay(self):
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def _random_ua(self):
        return random.choice(USER_AGENTS)

    def get(self, url, **kwargs):
        self._delay()
        headers = kwargs.pop("headers", {})
        headers.setdefault("User-Agent", self._random_ua())
        headers.setdefault("Accept-Language", "en-US,en;q=0.9,fr;q=0.8")
        timeout = kwargs.pop("timeout", self.timeout)
        return self.session.get(url, headers=headers, timeout=timeout, **kwargs)

    def post(self, url, **kwargs):
        self._delay()
        headers = kwargs.pop("headers", {})
        headers.setdefault("User-Agent", self._random_ua())
        headers.setdefault("Accept-Language", "en-US,en;q=0.9,fr;q=0.8")
        timeout = kwargs.pop("timeout", self.timeout)
        return self.session.post(url, headers=headers, timeout=timeout, **kwargs)
