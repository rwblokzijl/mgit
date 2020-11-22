from mgit.persistence.persistence import Persistence

from abc import abstractmethod

import os
import configparser
from copy import deepcopy

class ConfigFilePersistence(Persistence):

    def __init__(self, configFile):
        self.configPath = os.path.abspath(os.path.expanduser(configFile))
        # if not os.path.exists(configFile):
        #     os.tou
        self.read_all()

    def read_all(self):
        config = configparser.ConfigParser()
        self.data = config.read(self.configPath)
        self.remotes_dict = self.config_to_dict(config)
        # if len(self.data) == 0:
        #     raise self.FileNotFoundError("Failed to open/find files")
        return self.remotes_dict

    def read(self):
        return self.remotes_dict

    def __getitem__(self, item):
        return self.remotes_dict[item]

    def __setitem__(self, key, item):
        self.remotes_dict[key] = item

    def remove(self, key):
        if key in self.remotes_dict:
            del(self.remotes_dict[key])

    def items(self):
        return self.remotes_dict.items()

    def __contains__(self, key):
        return key in self.remotes_dict

    @abstractmethod
    def config_to_dict(self, config):
        pass

    @abstractmethod
    def dict_to_config(self, config):
        pass

    def clear_nulls(self, data):
        for name, base_data in deepcopy(dict(data)).items():
            for key, value in base_data.items():
                if value == "" or value is None or value == []:
                    del(data[name][key])
        return data

    def write_all(self):
        config = self.clear_nulls( self.dict_to_config( self.remotes_dict))
        with open(self.configPath, 'w') as configfile:
            config.write(configfile)

    class FileNotFoundError(Exception):
        pass
