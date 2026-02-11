import time
import logging
import random
import requests
from functools import wraps
from app.core.config import settings

logger = logging.getLogger("confluence")

def with_retry(max_retries=5, backoff_factor=1.5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    status = getattr(e.response, 'status_code', None)
                    
                    # Handle 429 (Rate Limit) Explicitly
                    if status == 429:
                        wait = int(e.response.headers.get("Retry-After", 60))
                        logger.warning(f"⚠️ 429 Too Many Requests. Waiting {wait}s...")
                        time.sleep(wait + 1)
                        continue
                    
                    # Handle Server Errors (5xx)
                    if status and status >= 500:
                        if retries >= max_retries: raise
                        
                        sleep_time = backoff_factor * (2 ** retries) + random.uniform(0, 1)
                        logger.warning(f"⚠️ Error {status}. Retrying in {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                        retries += 1
                        continue
                    
                    raise e
        return wrapper
    return decorator

class ConfluenceClient:
    def __init__(self, url, user, token):
        self.base_url = url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (user, token)
        self.session.headers.update({"Accept": "application/json"})
        self.last_req = 0

    @with_retry()
    def get_page_with_children(self, page_id):
        """
        The Critical 'Single API Call' Method.
        Fetches body AND children in one request using 'expand'.
        """
        self._throttle()
        url = f"{self.base_url}/rest/api/content/{page_id}"
        # STRICTLY following test.py: expand=body.storage,children.page,space
        params = {"expand": "body.storage,children.page,space"}
        
        resp = self.session.get(url, params=params, timeout=20)
        resp.raise_for_status()
        
        self.last_req = time.time()
        return resp.json()

    @with_retry(max_retries=3)
    def download_image(self, url, save_path):
        self._throttle()
        resp = self.session.get(url, stream=True, timeout=15)
        resp.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
        
        self.last_req = time.time()
        return True

    def _throttle(self):
        elapsed = time.time() - self.last_req
        if elapsed < settings.RATE_LIMIT_DELAY:
            time.sleep(settings.RATE_LIMIT_DELAY - elapsed)