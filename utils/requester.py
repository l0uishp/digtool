# utils/requester.py
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional
from threading import Lock

logger = logging.getLogger(__name__)

class Requester:
    def __init__(self, user_agent: str, timeout: int = 10, rate_limit: float = 1.0, max_retries: int = 2):
        self.headers = {"User-Agent": user_agent}
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self._last_request_time = 0.0
        self._lock = Lock()

    def _throttle(self):
        with self._lock:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.rate_limit:
                wait = self.rate_limit - elapsed
                logger.debug("Throttling: sleeping %.2fs", wait)
                time.sleep(wait)
            # update timestamp only when caller actually makes request

    def get(self, url: str, params=None, headers=None, allow_redirects=True) -> Optional[requests.Response]:
        merged_headers = self.headers.copy()
        if headers:
            merged_headers.update(headers)

        for attempt in range(self.max_retries + 1):
            try:
                self._throttle()
                resp = requests.get(url, params=params, headers=merged_headers, timeout=self.timeout, allow_redirects=allow_redirects)
                with self._lock:
                    self._last_request_time = time.time()
                logger.debug("GET %s -> %s", url, resp.status_code)
                return resp
            except requests.RequestException as e:
                logger.warning("GET error on %s: %s", url, e)
                time.sleep(1 + attempt)
        return None

    def post(self, url: str, data=None, json=None, headers=None, allow_redirects=True) -> Optional[requests.Response]:
        merged_headers = self.headers.copy()
        if headers:
            merged_headers.update(headers)

        for attempt in range(self.max_retries + 1):
            try:
                self._throttle()
                resp = requests.post(url, data=data, json=json, headers=merged_headers, timeout=self.timeout, allow_redirects=allow_redirects)
                with self._lock:
                    self._last_request_time = time.time()
                logger.debug("POST %s -> %s", url, resp.status_code)
                return resp
            except requests.RequestException as e:
                logger.warning("POST error on %s: %s", url, e)
                time.sleep(1 + attempt)
        return None

    @staticmethod
    def soup_from_response(resp):
        if resp is None:
            return None
        try:
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            logger.debug("BeautifulSoup parse error: %s", e)
            return None
