from util import *
import json
import configparser
import copy
import os

"""
All config behaviour is contained in the following 4 classes:
    1. RemotesConfig, contains multiple:
        2. Remotes
    3. RepoTree, structures multiple:
        4. RepoNodes, into a tree

    These classes provide all interaction with the config file
    They could possibly eventually be the interfact for interacting with the
    actual repos/remotes.

    The flow of creating the repos is as follows:
    1. The RepoTree inits a number of RepoNodes (using __init__)
    2. When all the RepoNodes are created, they are organised into a tree (using add_parent)
    3. When the tree is created all the relative paths are resolved (using final_update)
    4. TODO Finally all repos that exist are instantiated
"""

# assert False, "Read the last paragraph"


class RemotesConfig:
    def __init__(self, remotes_config, default=False):
        self.changed = False
        self.configPath = os.path.abspath(os.path.expanduser(remotes_config))
        self.default = default
        self.config = configparser.ConfigParser()

        self.config.read(self.configPath)

        def get_remote(remote, configObj=None):
            return {
                    'name': remote,
                    'url': configObj[remote]['url'],
                    'path': configObj[remote]['path'],
                    'is_default': remote in configObj['defaults']
                    }

        if default:
            rlist =  [get_remote(x, self.config) for x in self.config['defaults'] if self.remote_in_config(x, self.config)]
        else:
            rlist =  [get_remote(x, self.config) for x in self.config if self.remote_in_config(x, self.config)]

        self.remotes = {r["name"]: self.Remote(vals=r) for r in rlist}

    def remote_in_config(self, remote, configObj):
        return (remote in configObj and
                "url" in configObj[remote] and
                "path" in configObj[remote] and
                "ignore" not in configObj[remote]
                )

    def __contains__(self, item):
        return item in self.remotes

    def __getitem__(self, key):
        if key in self.remotes:
            return self.remotes[key]
        else:
            return None

    def as_dict(self):
        return [ v for k,v in self.remotes.items() ]

    def __setitem__(self, key, item):
        assert isinstance(item, dict)
        assert item["name"] == key, f"Key '{key}' does not match remote name '" + item["name"] + "'"

        r = self.Remote(vals=item)
        self.remotes[key] = r
        self.config[key] = r.as_config()
        if self.default:
            self.config['defaults'][key] = 1
        print(f'Added remote {key} at {item["url"]}:{item["path"]}')
        self.changed = True

    def remove(self, remotes):
        for remote in remotes:
            self.remotes.pop(remote)
            self.config.remove_section(remote)
        self.changed = True

    def print(self, verbose):
        if verbose:
            if self.default:
                [x.pop("is_default") for x in self.remotes.values()]
                pprint(self, header=["Remote", "Url", "Path"])
            else:
                pprint(self, header=["Remote", "Url", "Path", "Default"])
        else:
            for remote in self.remotes.values():
                print(remote["name"])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.changed:
            with open(self.configPath, 'w') as configfile:
                self.config.write(configfile)

    def __iter__(self):
        return iter(self.remotes.values())

    class Remote:
        def __init__(self, vals=None, name=None, url=None, path=None, default=False):
            assert (
                    vals or
                    (name and url and path)
                    ), "Either set vals, or name and url and path"
            if vals:
                self.vals = {
                        "name" : vals['name'],
                        "url" : vals['url'],
                        "path" : vals['path'],
                        "is_default" : vals['is_default']
                        }
            else:
                self.vals = {
                        "name" : name,
                        "url" : url,
                        "path" : path,
                        "is_default" : default
                        }

        def __getitem__(self, key):
            return self.vals[key]

        def __setitem__(self, key, value):
            assert False, "Do not set the remote directly, all interaction should happen through the RemotesConfig class"

        def as_dict(self):
            return self.vals

        def as_config(self):
            return {
                    "url" : self.vals['url'],
                    "path" : self.vals['path'],
                    }

        def __str__(self):
            return json.dumps(self.vals, indent=4)

        def values(self):
            return self.vals.values()

        def pop(self, *args, **kwargs):
            return self.vals.pop(*args, **kwargs)

class RepoTree:
    def get_repos(self):
        return get_repos_and_missing_from_paths([child.path for child in self.repotrees.values() if not child.is_root])

    """
    [example]
    path            = example
    originUrl       = bloodyfool@git.bloodyfool.family
    originPath      = /data/git/projects/
    origin          = home
    parent          = config
    home-repo       = example-name-in-home
    blank-repo = different-example-name
    ignore          = 1
    """

    def __init__(self, repos_config, remotes):
        "remotes "

        filePath = os.path.abspath(os.path.expanduser(repos_config))
        config = configparser.ConfigParser()
        config.read(filePath)

        # 1. Instantiate all the objects
        self.repotrees= {
                section : RepoNode(section, config[section], remotes)
                for section in config.sections()
                if section_get(config[section], "ignore") is None
                }

        # 2. Link all the objects into a tree
        self.children = dict()

        for section, rt in self.repotrees.items():
            parent      = section_get(config[section], "parent")
            is_category = section_get(config[section], "is_category")
            if parent:
                if parent in self.repotrees:
                    rt.add_parent(self.repotrees[parent])
                else:
                    print("WARNING: Parent for {section}: {parent} doesn't exist" )
            elif is_category:
                self.children[section] = rt
            else:
                print("WARNING:", section, "is neither parent nor top level, ignoring")

        # 3. All objects will
        for section, rt in self.repotrees.items():
            rt.final_update()

    def as_dict(self):
        return {
                "categories": [v.as_dict() for k,v in self.children.items()]
                }

    def __str__(self):
        return json.dumps(self.as_dict(), indent=2)
        # return get_repos(config, remotes)

    def __contains__(self, item):
        return item in self.repotrees

    # def __setitem__(self, key, item):
    #     self.children[key] = item

    def __getitem__(self, key):
        if key in self.repotrees:
            return self.repotrees[key]
        else:
            return None

class RepoNode:
    """
        [example]
        path            = example
        originUrl       = bloodyfool@git.bloodyfool.family
        originPath      = /data/git/projects/
        origin          = home
        parent          = config
        home-repo       = example-name-in-home
        blank-repo = different-example-name
        ignore          = 1
    """

    def __init__(self, name, section, remotes):

        self.section  = section

        self.parent   = None
        self.path   = None

        self.is_root       = bool(section_get(section, "is_category", False))

        self.name          = name
        self.relative_path = section_get(section, "path")
        self.originUrl     = section_get(section, "originUrl")
        self.originPath    = section_get(section, "originPath")
        self.origin        = section_get(section, "origin")
        self.parent_name   = section_get(section, "parent")

        def add_remote(remote, name):
            if not remote:
                return None
            return {
                    'name':           remote['name'],
                    'url':            remote['url'],
                    'path':           remote['path'],
                    'repo':           name
                    }

        self.remotes = [
                add_remote( remotes[remote[:-5]], section[remote] )
                for remote in section
                if remote.endswith("-repo") and remote[:-5] in remotes
                ]

        self.children = list()

    def add_parent(self, parent):
        parent.add_child(self)
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)

    def final_update(self):
        if self.parent:
            self.path = os.path.join(self.parent.path, self.relative_path)
        else:
            self.path = os.path.abspath(os.path.expanduser(self.relative_path))
        for child in self.children:
            child.final_update()

    def as_dict(self):
        if self.is_root:
            return {
                    "name": self.name,
                    "path": self.path,
                    "children": [child.as_dict() for child in self.children],
                    }
        else:
            return {
                    "name": self.name,
                    "path": self.path,
                    "origin": self.origin,
                    "children": [child.as_dict() for child in self.children],
                    "remotes": self.remotes,
                    # "remotes": [remote.as_dict() for remote in self.remotes],
                    }

    def __str__(self):
        return json.dumps(self.as_dict(), indent=4)

# Helpers

def section_get(section, field, default=None):
    if field in section:
        return section[field]
    else:
        return default
