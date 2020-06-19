from mgit.persistence.config_persistence import ConfigFilePersistence

from abc import abstractmethod

import configparser
import copy
import json
import os

class ReposConfigFilePersistence(ConfigFilePersistence):

    def config_to_dict(self, config):
        ans_dict = dict()

        for k, v in config.items():
            if k == "DEFAULT":
                continue
            else:
                vdict = dict(v)
                vdict["name"] = k
                ans_dict[k] = vdict

        return ans_dict

    def dict_to_config(self, remotes_dict):
        config = configparser.ConfigParser()
        config.read_dict(remotes_dict)
        return config
