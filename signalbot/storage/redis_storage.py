from signalbot.errors import StorageError
from signalbot.storage.base_storage import BaseStorage

import redis
import json
from typing import Any


class RedisStorage(BaseStorage):
    def __init__(self, host, port):
        self._redis = redis.Redis(host=host, port=port, db=0)

    def exists(self, key: str) -> bool:
        return self._redis.exists(key)

    def read(self, key: str) -> Any:
        try:
            result_bytes = self._redis.get(key)
            result_str = result_bytes.decode('utf-8')
            result_dict = json.loads(result_str)
            return result_dict
        except Exception as e:
            raise StorageError(f'Redis load failed: {e}')

    def save(self, key: str, object: Any):
        try:
            object_str = json.dumps(object)
            self._redis.set(key, object_str)
        except Exception as e:
            raise StorageError(f'Redis save failed: {e}')
