from mgit.persistence.persistence import Persistence

from abc import abstractmethod

import os
import copy
import configparser

class ConfigFilePersistence(Persistence):

    def __init__(self, configFile):
        self.configPath = os.path.abspath(os.path.expanduser(configFile))

    def read_all(self):
        config = configparser.ConfigParser()
        data = config.read(self.configPath)
        if len(data) == 0:
            raise self.FileNotFoundError("Failed to open/find files")

        return self.config_to_dict(config)

    @abstractmethod
    def config_to_dict(self, config):
        pass

    @abstractmethod
    def dict_to_config(self, config):
        pass

    def write_all(self, remotes_dict):
        config = self.dict_to_config(remotes_dict)
        with open(self.configPath, 'w') as configfile:
            config.write(configfile)

    class FileNotFoundError(Exception):
        pass
