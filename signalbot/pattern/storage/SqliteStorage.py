from signalbot.pattern.storage.BaseStorage import BaseStorage


class SqliteStorage(BaseStorage):
    def __init__(self, db_path):
        self.db_path = db_path

    def save(self, value):
        pass

    def find(self, key):
        pass

    def delete(self, key):
        pass

    def update(self, key) -> bool:
        pass

