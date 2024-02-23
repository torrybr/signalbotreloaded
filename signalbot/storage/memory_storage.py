import json
from typing import Any

from signalbot.errors import StorageError
from signalbot.storage.base_storage import BaseStorage


class InMemoryStorage(BaseStorage):
    def __init__(self):
        self._storage = {}

    def exists(self, key: str) -> bool:
        return key in self._storage

    def find(self, key: str) -> Any:
        try:
            result_str = self._storage[key]
            result_dict = json.loads(result_str)
            return result_dict
        except Exception as e:
            raise StorageError(f'InMemory load failed: {e}')

    def save(self, key: str, object: Any):
        try:
            object_str = json.dumps(object)
            self._storage[key] = object_str
        except Exception as e:
            raise StorageError(f'InMemory save failed: {e}')
