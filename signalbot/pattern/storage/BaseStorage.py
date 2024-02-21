class BaseStorage:

    def save(self, data):
        raise NotImplementedError

    def find(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def update(self, key) -> bool:
        raise NotImplementedError
