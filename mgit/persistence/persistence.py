
from abc import ABC, abstractmethod, abstractproperty

class Persistence(ABC):
    @abstractmethod
    def read_all(self):
        pass

    @abstractmethod
    def write_all(self, remotes):
        pass

