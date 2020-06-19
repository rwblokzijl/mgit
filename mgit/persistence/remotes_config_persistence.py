from mgit.persistence.config_persistence import ConfigFilePersistence

from abc import abstractmethod

import os
import copy
import configparser

class RemotesConfigFilePersistence(ConfigFilePersistence):

    def config_to_dict(self, config):
        ans_dict = dict()
        last = list()

        for k, v in config.items():
            if k == "DEFAULT":
                continue
            elif k.lower() == "defaults":
                last.append(k)
            else:
                vdict = dict(v)
                vdict["name"] = k
                vdict["is_default"] = False
                ans_dict[k] = vdict

        for defaults in last:
            for c in config[defaults]:
                if c in ans_dict:
                    ans_dict[c]["is_default"] = True

        return ans_dict

    def dict_to_config(self, remotes_dict):
        write_dict = copy.deepcopy(remotes_dict)
        write_dict["defaults"] = {}
        for k, v in remotes_dict.items():
            if "is_default" in v and v["is_default"]:
                write_dict["defaults"][k] = 1
            write_dict[k].pop("is_default")

        config = configparser.ConfigParser()
        config.read_dict(write_dict)
        return config
