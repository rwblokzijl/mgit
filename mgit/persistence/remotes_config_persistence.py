from mgit.persistence.remotes_persistence import RemotePersistence

import os
import copy
import configparser

class RemotesConfigFilePersistence(RemotePersistence):
    def __init__(self, configFile):
        self.configPath = os.path.abspath(os.path.expanduser(configFile))

    def config_to_dict(self):
        ans_dict = dict()
        last = list()

        for k, v in self.config.items():
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
            for c in self.config[defaults]:
                if c in ans_dict:
                    ans_dict[c]["is_default"] = True

        return ans_dict

    def read_all(self):
        self.config = configparser.ConfigParser()
        data = self.config.read(self.configPath)
        if len(data) == 0:
            raise self.FileNotFoundError("Failed to open/find files")

        return self.config_to_dict()

    def write_all(self, remotes_dict):
        write_dict = copy.deepcopy(remotes_dict)
        write_dict["defaults"] = {}
        for k, v in remotes_dict.items():
            if "is_default" in v and v["is_default"]:
                write_dict["defaults"][k] = 1
            write_dict[k].pop("is_default")

        config = configparser.ConfigParser()
        config.read_dict(write_dict)
        with open(self.configPath, 'w') as configfile:
            config.write(configfile)

    class FileNotFoundError(Exception):
        pass

