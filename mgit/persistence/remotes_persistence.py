
from abc import ABC, abstractmethod, abstractproperty

class RemotePersistence(ABC):
    @abstractmethod
    def read_all(self):
        pass

    @abstractmethod
    def write_all(self, remotes):
        pass

