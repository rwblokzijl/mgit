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
                if "categories" in vdict:
                    vdict["categories"] = vdict["categories"].split(" ")
                ans_dict[k] = vdict

        return ans_dict

    def dict_to_config(self, repo_dict):
        for k, v in repo_dict.items():
            vdict = copy.copy(v)
            if "categories" in v:
                vdict["categories"] = " ".join(vdict["categories"])
            repo_dict[k] = vdict
        config = configparser.ConfigParser()
        config.read_dict(repo_dict)
        return config
