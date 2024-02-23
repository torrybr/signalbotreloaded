from abc import abstractmethod


class BaseStorage:
    """
    This is the BaseStorage class which serves as an abstract base class (ABC)
    for storage classes. It defines the basic methods that any storage
    class should implement.

    Methods
    -------
    exists(key: str) -> bool:
        Abstract method that checks if a given key exists in the storage.

    read(key: str):
        Abstract method that reads data associated with a given key from the storage.

    save(key: str, data: dict):
        Abstract method that saves data with a given key to the storage.
    """

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def find(self, key: str):
        pass

    @abstractmethod
    def save(self, key: str, data: dict):
        pass
