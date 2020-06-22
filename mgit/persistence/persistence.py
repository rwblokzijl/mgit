
from abc import ABC, abstractmethod, abstractproperty

class Persistence(ABC):
    @abstractmethod
    def read_all(self):
        pass

    @abstractmethod
    def write_all(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __setitem__(self, key, item):
        pass

    @abstractmethod
    def remove(self, key):
        pass

    @abstractmethod
    def __contains__(self, key):
        pass

    class ItemExistsError(Exception):
        pass

