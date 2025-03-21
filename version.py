APP_VERSION = 'v3.5.6'

from contextlib import contextmanager
import time
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, Any

class MainDb:
    @contextmanager
    def transaction(self, timeout=30):
        """
        事务上下文管理器
        """
        start_time = time.time()
        try:
            yield self.session
            while True:
                try:
                    self.commit()
                    break
                except Exception as e:
                    if time.time() - start_time > timeout:
                        raise
                    time.sleep(0.1)
        except:
            self.rollback()
            raise
        finally:
            self.session.close()

class TMDBClient:
    def __init__(self):
        self._cache = {}
        self._cache_timeout = timedelta(hours=1)

    @lru_cache(maxsize=1000)
    def get_movie_info(self, movie_id: str) -> Dict[str, Any]:
        return self._fetch_movie_info(movie_id)

    def _is_cache_valid(self, key: str) -> bool:
        if key not in self._cache:
            return False
        return datetime.now() - self._cache[key]['timestamp'] < self._cache_timeout
