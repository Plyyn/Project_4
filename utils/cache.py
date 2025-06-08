from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading


class ApiCache:
    """Потокобезопасный кэш для данных API с TTL."""

    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(seconds=ttl)
        self.max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Получить данные из кэша если они актуальны."""
        with self._lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < self.ttl:
                return entry['data']

            # Автоматически удаляем просроченные записи
            del self.cache[key]
            return None

    def set(self, key: str, data: Any) -> None:
        """Добавить данные в кэш."""
        with self._lock:
            if len(self.cache) >= self.max_size:
                self._remove_oldest()

            self.cache[key] = {
                'data': data,
                'timestamp': datetime.now()
            }

    def _remove_oldest(self) -> None:
        """Удалить самые старые записи при достижении лимита."""
        oldest_key = min(self.cache.keys(),
                         key=lambda k: self.cache[k]['timestamp'])
        del self.cache[oldest_key]

    def clear(self) -> None:
        """Очистить весь кэш."""
        with self._lock:
            self.cache.clear()