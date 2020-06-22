from mgit.util import *
from mgit.remotes.remote import Remote, HandlerHandler

import json
import copy

class RemotesBuilder:
    def build(self, remote_data):
        self.remotes = dict()
        self.save_as_remotes(remote_data)
        return self.remotes

    def save_as_remotes(self, remote_data):
        for k, v in remote_data.items():
            self.validate_and_add_remote(k, v)

    def validate_and_add_remote(self, key, remote_dict):
        self.remotes[key]  = self.validate_remote(key, remote_dict)

    def validate_remote(self, key, remote_dict):
        self.validate_remote_dict_name(key, remote_dict)
        self.validate_remote_dict_required_fields(key, remote_dict)
        rtype = self.validate_remote_dict_type(key, remote_dict)

        default = remote_dict.get("is_default", False)
        self.validate_remote_dict_default(key, default)

        port = remote_dict.get("port", 22)
        self.validate_remote_dict_port(key, port)

        return Remote(
                name        = remote_dict["name"],
                url         = remote_dict["url"],
                path        = remote_dict["path"],
                remote_type = rtype,
                port        = port,
                default     = default,
                base_data = {},
                )

    def validate_remote_dict_name(self, key, remote_dict):
        if "name" not in remote_dict:
            raise self.InvalidConfigError(f"'name' for {key} should exist in dict")
        if key != remote_dict["name"]:
            raise self.InvalidConfigError(f"""'name' for {key} should be equal in dict, found {remote_dict["name"]}""")

    def validate_remote_dict_required_fields(self, key, remote_dict):
        err = None
        try:
            name    = remote_dict["name"]
            url     = remote_dict["url"]
            path    = remote_dict["path"]
        except KeyError as e:
            err = self.InvalidConfigError(f"Dict {key} should contain {e}")
        if err:
            raise err

    def validate_remote_dict_type(self, key, remote_dict):
        rtype    = remote_dict.get("type", "ssh")
        if HandlerHandler().check_type(rtype):
            return rtype
        else:
            raise self.InvalidConfigError(f"Dict {key} has invalid type {rtype}")

    def validate_remote_dict_default(self, key, default):
        if type(default) is not bool:
            raise self.InvalidConfigError(f"'is_default' for {key} should be a boolean, not {default}")

    def validate_remote_dict_port(self, key, port):
        err = None
        try:
            port    = int(port)
        except ValueError:
            err = self.InvalidConfigError(f"'port' for {key} should be an integer, not {port}")
        if err:
            raise err

    class InvalidConfigError(Exception):
        pass
