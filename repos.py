import json
import configparser
import copy
import os

from util import *

"""
All config behaviour is contained in the following 4 classes:
    1. Remotes, contains multiple:
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

class RepoTree:
    def get_repos(self):
        return get_repos_and_missing_from_paths([child.path for child in self.repotrees.values()])

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

    # Setup

    def __init__(self, repos_config, remotes):
        self.remotes = remotes

        self.path = os.path.expanduser("~")

        self.changed=False
        self.name = None

        self.configPath = os.path.abspath(os.path.expanduser(repos_config))
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath)

        # 1. Instantiate all the objects
        self.repotrees= {
                section : RepoNode(section, self.config[section], remotes, self)
                for section in self.config.sections()
                if section_get(self.config[section], "ignore") is None
                }

        # 2. Link all the objects into a tree
        self.children   = dict()
        self.categories = dict()

        # assert False, "Adding to non-categories is allowed, but loading isnt"
        for section, rt in self.repotrees.items():
            parent      = section_get(self.config[section], "parent")
            categories    = (section_get(section, "categories") or "").split()
            if parent:
                if parent in self.repotrees:
                    rt.add_parent(self.repotrees[parent])
                else:
                    print("WARNING: Parent for {section}: {parent} doesn't exist" )
            else:
                self.children[section] = rt
            # else:
            #     print("WARNING:", section, "is neither parent nor top level, ignoring")
            for category in categories:
                self.add_to_cat(category, rt)

        # 3. Finally update paths according to parent
        for section, rt in self.repotrees.items():
            rt.final_update()

    def add_to_cat(self, cat, rt):
        if cat not in self.categories:
            self.categories[cat] = list()

        self.categories[cat].append(rt)

    def get_best_parent(self, parent, path):
        if not path.startswith(parent.path):
            # print(f"Failing {parent.path} for {path}")
            return 0, None
        # print(f"Trying {parent.path} for {path}")
        best_v      = len(os.path.commonprefix([path, parent.path]))
        best_child  = parent
        for child in parent.children.values():
            v, child = self.get_best_parent(child, path)
            if v > best_v:
                best_v = v
                best_child = child
        return best_v, best_child

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.changed:
            with open(self.configPath, 'w') as configfile:
                self.config.write(configfile)
    # Getters

    def __iter__(self):
        return iter(self.repotrees.values())

    def __contains__(self, item):
        return item in self.repotrees

    def status(self, name, category=True, recursive=False, dirty=False, missing=True, indent=0):
        if category:
            if name in self.repotrees:
                self.repotrees[name].status(root="~", recursive=True, dirty=dirty, missing=missing)
            elif name in self.categories:
                for repo in self.categories[name]:
                    repo.status(root="~", recursive=True, dirty=dirty, missing=missing)
        else:
            repos = self.get_repos_in_path(name)
            for repo in repos:
                repo.status(name, recursive, dirty, missing, indent)

    def get_repos_in_path(self, path):
        abspath = os.path.abspath(os.path.expanduser(path))
        return [child for child in self.children.values() if child.path.startswith(abspath)]

    def get_from_path(self, path):
        for rt in self.repotrees.values():
            if path == rt.path:
                return rt
        return None

    def get_from_id(self, rid):
        for rt in self.repotrees.values():
            if rid == rt.rid:
                return rt
        return None

    def add(self, name, path, categories):
        """
        [name]
        path=example
        rid=[HASH]
        origin=home
        originUrl=bloodyfool@git.bloodyfool.family
        originPath=/data/git/projects/
        parent=config
        ex_remote-repo=example-name-in-remote
        """
        config_dict = {}
        config_dict["repo_id"] = get_repo_id_from_path(path) or ""
        config_dict["category"] = categories
        if name in self.config.sections():
            print(f"{name} is already used")
            print(self.config.sections())
            return False
        try:
            repo = Repo(path)
        except:
            log_error(f"{path} is not a git repo")
            return
        val, parent = self.get_best_parent(self, path)
        config_dict["parent"] = parent.name or ""
        if parent == None:
            log_error(f"Only paths in the home directoy are currently supported")
            return
        if path == parent.path:
            log_error(f"Path {path} used by {parent.name}")
            return False
        # print(f"Best parent for {path} is {parent.path} with {val}")
        config_dict["path"] = os.path.relpath(path, parent.path)
        # print(f"Adding {path} to {parent.path}/")
        origin = None
        for r in repo.remotes:
            urls = list(r.urls)
            url, path = urls[0].split(":")
            if len(list(r.urls)) > 1:
                log_error("This tool does not support multiple origins")
                return
            remote = get_remote(urls[0], self.remotes)
            if r.name == "origin":
                if remote is not None:
                    config_dict["origin"] = remote["name"]
                else:
                    config_dict["originUrl"] = url
                    config_dict["originPath"] = path
            if remote is not None:
                config_dict[remote["name"]+"-repo"] = os.path.relpath(path, remote["path"])
        self.config[name]       = config_dict # NOTE: no object is created
        self.changed = True

    def move(self, key, item): #move local path
        if key not in self.config.sections():
            print(f"{key} does not exist")

    def remove(self, name): #remove from config
        if not name in self.children:
            log_error(f"'{name}' is not a project")
            return 1
        del(self.children[name])
        del(self.repotrees[name])
        self.config.remove_section(name)
        self.changed = True

    def print_cat(self, cat):
        if cat in self.categories:
            print(f"{cat}:")
            for name in [rep.name for rep in self.categories[cat]]:
                print(name)
            return 0
        return 1

    def rename(self, old_name, new_name): #remove from config
        if not old_name in self:
            log_error(f"No project called '{old_name}' found")
            return

        if new_name in self:
            log_error(f"'{new_name}' already used")
            return

        # Update config file
        self.config[new_name] = self.config[old_name]
        self.config.remove_section(old_name)

        # Update Object
        self[old_name].name = new_name
        self[old_name].section = self.config[new_name]

        # Update Own references
        if old_name in self.children:
            self.children[new_name] = self.children.pop(old_name)
        if old_name in self.repotrees:
            self.repotrees[new_name] = self.repotrees.pop(old_name)

        self.changed = True

    def rclone(self, name, remote_name): #clone to other remote
        pass

    def hard_edit(self, name): #rename
        pass


    # Visualising

    def as_dict(self):
        return {
                "children": [v.as_dict() for k,v in self.children.items()]
                }


    def __str__(self):
        return json.dumps(self.as_dict(), indent=2)
        # return get_repos(config, remotes)

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

    def __init__(self, name, section, remotes, repotree):
        self.root = repotree
        self.section  = section

        self.parent   = None
        self.path   = None

        self.name          = name
        self.relative_path = section_get(section, "path")
        self.originUrl     = section_get(section, "originUrl")
        self.originPath    = section_get(section, "originPath")
        self.origin        = section_get(section, "origin")
        self.parent_name   = section_get(section, "parent") or None
        self.rid           = section_get(section, "repo_id") or None
        self.archived      = section_get(section, "archived")
        self.categories    = (section_get(section, "category") or "").split()

        def add_remote(remote, name):
            if not remote:
                return None
            return {
                    'name':           remote['name'],
                    'url':            remote['url'],
                    'path':           remote['path'],
                    'repo':           name
                    }

        self.remotes = dict()

        for remote_repo in section:
            remote_name = remote_repo[:-5]
            if remote_repo.endswith("-repo") and remote_name in remotes:
                remote = add_remote( remotes[remote_name], section[remote_repo] )
                self.remotes[remote_name] = remote

        self.children = dict()

    def add_parent(self, parent):
        parent.add_child(self)
        self.parent = parent

    def add_child(self, child):
        self.children[child.name] = child

    def install(self):
        # print(self.remotes)
        remote = self.remotes[self.origin]
        url = f'{remote["url"]}'
        path = os.path.join(remote["path"], remote["repo"])
        command = f"git clone {url}:{path} {self.path}"
        os.system(f"mkdir -p {self.path}")
        os.system(command)

    def final_update(self):
        if self.parent:
            self.path = os.path.join(self.parent.path, self.relative_path)
        else:
            self.path = os.path.abspath(os.path.expanduser(self.relative_path))
        for child in self.children.values():
            child.final_update()
        try:
            self.repo = Repo(self.path)
            self.missing = False
        except:
            self.repo = None
            self.missing = True

    def as_dict(self):
        return {
                "name": self.name,
                "id": self.rid,
                "path": self.path,
                "origin": self.origin,
                "children": [x.as_dict() for x in self.children.values()],
                "categories": self.categories,
                "remotes": self.remotes,
                "archived": bool(self.archived),
                # "remotes": [remote.as_dict() for remote in self.remotes],
                }

    def set_id(self):
        if self.rid:
            return
        if not self.missing:
            rid = get_repo_id_from_path(self.path)
        else:
            for remote in self.remotes.values():
                user, remo = remote["url"].split("@")
                repo_path = os.path.join(remote["path"], remote["repo"])
                rid = get_remote_repo_id(username=user, remote=remo, repo_path=repo_path)
                if rid:
                    break
        if rid:
            self.rid = rid
            self.section["repo_id"] = rid
            self.root.changed = True
        else:
            if self.missing:
                print(f"couldnt get id for missing {self.path}")
            else:
                print(f"couldnt get id for local {self.path}")

    def status(self, root="~", recursive=False, dirty=False, missing=True, indent=0):
        if self.missing:
            if self.parent:
                path = os.path.relpath(self.path, self.parent.path)
            else:
                if root == "~":
                    path = "~/" + os.path.relpath(self.path, os.path.expanduser(root))
                else:
                    path = os.path.relpath(self.path, os.path.expanduser(root))
            if missing:
                print("missing", " "*indent + path)
            return

        if self.parent:
            if root == "~":
                path = "~/" + os.path.relpath(self.repo.working_dir, self.parent.path)
            else:
                path = os.path.relpath(self.repo.working_dir, self.parent.path)
        else:
            if root == "~":
                path = "~/" + os.path.relpath(self.repo.working_dir, os.path.expanduser(root))
            else:
                path = os.path.relpath(self.repo.working_dir, os.path.expanduser(root))
        if self.repo.is_dirty():
            print("dirty  ", " "*indent + path)
        else:
            commits_behind = len(list(self.repo.iter_commits('master..origin/master')))
            commits_ahead  = len(list(self.repo.iter_commits('origin/master..master')))
            if commits_ahead or commits_behind:
                print(f"{commits_ahead}+ {commits_behind}-  ", " "*indent + path)
            else:
                if not dirty:
                    print("clean  ", " "*indent + path)

        for child in self.children.values():
            child.status(root, recursive, dirty, missing, indent+2)

    def add_category(self, category):
        if category not in self.categories:
            self.categories.append(category)
            self.section["category"] = " ".join(self.categories)
            self.root.changed=True

    def remove_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
            self.section["category"] = " ".join(self.categories)
            self.root.changed=True

    def archive(self, archived):
        if archived:
            self.section["archived"] = "1"
            print(f"archiving {self.name}")
        else:
            self.section["archived"] = ""
            print(f"unarchiving {self.name}")
        self.root.changed = True

    def set_path(self, path):
        if self.parent:
            path = os.path.relpath(path, self.parent.path)
        else:
            path = collapse_user(path)
        self.path = path
        self.section["path"] = path
        print(f"Changing path of '{self.name}' to {path} ")
        self.root.changed = True

    def __str__(self):
        return json.dumps(self.as_dict(), indent=4)

# Helpers

def section_get(section, field, default=None):
    if field in section:
        return section[field]
    else:
        return default

def get_remote(url, remotes):
    url, path = url.split(":")
    best_v = 0
    best_remote = None
    for remote in remotes:
        if remote["url"] == url and path.startswith(remote["path"]):
            v = len(os.path.commonprefix([path, remote["path"]]))
            if v > best_v:
                best_v = v
                best_remote = remote
    return best_remote
