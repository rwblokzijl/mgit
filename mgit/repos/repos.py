import json
import configparser
import os

from mgit.util import *
# from mgit.remotes import MissingRepoException, EmptyRepoException

class Repo:

    def __init__(self, name, path, parent, origin, categories, remotes, archived, repo_id, base_data):
        self.base_data  = base_data
        self.name       = name
        self.path       = path
        self.origin     = origin
        self.parent     = parent
        self.categories = categories
        self.remotes    = remotes
        self.archived   = archived
        self.repo_id    = repo_id

        self.children = []

    def get_auto_key(self, key):
        return self.base_data.get(key, None)

    def as_dict(self):
        d = {
                "name": self.name,
                "path": self.path,
                # "children": [x.as_dict() for x in self.children.values()],
                "categories": self.categories,
                "remotes": {k : v.as_dict() for k, v in self.remotes.items()},
                "archived": self.archived,
                "repo_id": self.repo_id,
                # "remotes": [remote.as_dict() for remote in self.remotes],
                }
        if self.origin:
            d["origin"] = self.origin.as_dict()
        if self.parent:
            d["parent"] = self.parent.name
        return d
