import json
import configparser
import copy
import os

from abc import ABC, abstractmethod

from mgit.util import *
# from mgit.remotes import MissingRepoException, EmptyRepoException

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

class ReposBuilder:
    """
    "example2" : {
        "name" : "example2",
        "path" : "example2",
        "originurl" : "bloodyfool2@git.bloodyfool.family",
        "origin" : "home",
        "categories" : "config",
        # "ignore" : "1",
        "home-repo" : "example-name-in-home",
        "ewi-gitlab-repo" : "different-example-name",
        }
    """

    def build(self, repo_data, remotes={}):
        self.repos = dict()
        self.remotes = remotes

        self.save_as_repos(repo_data)

        return self.repos

    def save_as_repos(self, repo_data):
        for key, repo_dict in repo_data.items():
            self.validate_and_add_repo(key, repo_dict)

    def validate_and_add_repo(self, key, repo_dict):
        if self.should_ignore_dict(repo_dict):
            return

        name       = self.validate_repo_dict_name(       key, repo_dict)
        path       = self.validate_repo_dict_path(       key, repo_dict)
        categories = self.validate_repo_dict_categories( key, repo_dict)
        remotes    = self.validate_repo_dict_remotes(    key, repo_dict)
        origin     = self.validate_repo_dict_origin(     key, repo_dict, remotes)

        self.repos[key] = Repo(
                name       = name,
                path       = path,
                origin     = origin,
                categories = categories,
                remotes    = remotes,
                )

    def validate_repo_dict_name(self, key, repo_dict):
        if "name" not in repo_dict:
            raise self.InvalidConfigError(f"'name' for {key} should exist in dict")
        if key != repo_dict["name"]:
            raise self.InvalidConfigError(f"""'name' for {key} should be equal in dict, found {repo_dict["name"]}""")
        return repo_dict["name"]

    def validate_repo_dict_path(self, key, repo_dict):
        if "path" not in repo_dict:
            raise self.InvalidConfigError(f"'path' for {key} should exist in dict")
        return repo_dict["path"]

    def validate_repo_dict_categories(self, key, repo_dict):
        if "categories" in repo_dict:
            return repo_dict["categories"].split(" ")

    def validate_repo_dict_remotes(self, key, repo_dict):
        remotes_dict = dict()
        for key, repo_name in repo_dict.items():
            if not key.endswith("-repo"):
                continue
            remote_name      = key[:-5]
            remote = self.validate_remote(key, remote_name, repo_name)
            if remote is not None:
                remotes_dict[remote_name] = remote
        return remotes_dict

    def validate_remote(self, key, remote_name, repo_name):
        # if remote_name in self.remotes:
        #     self.remotes[remote_name] = self.Remote(remote_repo_name, remotes[remote_name])
        # else:
        #     log_warning(f"Remote '{remote_name}', listed in '{self.name}', doesn't exist, skipping")
        if remote_name in self.remotes:
            return DerivedRepoRemote(self.remotes[remote_name], repo_name)
        else:
            raise self.MissingRemoteReferenceError(f"Missing referenced remote '{remote_name}' for repo '{key}'")

    def validate_repo_dict_origin(self, key, repo_dict, remotes):
        if "origin" in repo_dict:
            origin_name = repo_dict["origin"]
            if origin_name in remotes:
                return remotes[repo_dict["origin"]]
            else:
                raise self.MissingOriginReferenceError(f"Missing origin referenced remote '{origin_name}' for repo '{key}'")
        if "originurl" in repo_dict:
            return UnnamedRepoOrigin(repo_dict["originurl"])
        raise self.MissingOriginError(f"Missing origin and originurl for repo '{key}'")

    def should_ignore_dict(self, repo_dict):
        return "ignore" in repo_dict and repo_dict["ignore"]

    class InvalidConfigError(Exception):
        pass

    class MissingRemoteReferenceError(Exception):
        pass

    class MissingOriginReferenceError(Exception):
        pass

    class MissingOriginError(Exception):
        pass

class RepoRemote(ABC):
    @abstractmethod
    def get_url(self):
        pass

class DerivedRepoRemote(RepoRemote):
    def __init__(self, remote, repo_name):
        self.remote = remote.get_url()
        self.repo_name = repo_name

    def get_url(self):
        if self.remote.endswith(":"):
                return self.remote + self.repo_name
        else:
            if self.repo_name.startswith("/"):
                raise self.InvalidPathError("Cannot append absolute path to relative URL not ending in ':', ")
            return os.path.join(self.remote, self.repo_name)

    class InvalidPathError(Exception):
        pass

class UnnamedRepoOrigin(RepoRemote):
    def __init__(self, url):
        self.url = url

    def get_url(self):
        return self.url

class Repo:
    def __init__(self, name, path, origin, categories, remotes):
        self.name       = name
        self.path       = path
        self.origin     = origin
        self.categories = categories
        self.remotes    = remotes

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

        for section, rt in self.repotrees.items():
            parent      = section_get(self.config[section], "parent")
            if parent:
                if parent in self.repotrees:
                    rt.add_parent(self.repotrees[parent])
                else:
                    print("WARNING: Parent for {section}: {parent} doesn't exist" )
            else:
                self.children[section] = rt

        # 3. update paths according to parent
        for section, rt in self.repotrees.items():
            rt.final_update()

        # 4.1 Generate loopup maps (categories)
        self.categories = dict()
        uncategorized = list()
        for section, rt in self.repotrees.items():
            categories    = (section_get(self.config[section], "categories") or "").split()
            for category in categories:
                self.add_to_cat(category, rt)
            if not categories:
                uncategorized.append(rt)

        for rt in uncategorized:
            self.add_to_cat("uncategorized", rt)

        # 4.2 Generate loopup maps (remotes)
        self.remote_repo_map = dict()
        for name, rt in self.repotrees.items():
            for remote in rt.remotes.values():
                self.add_to_remote_map(remote.name, remote.repo, rt)

        # Set in remotes
        for remote, repo_map in self.remote_repo_map.items():
            if remote in remotes:
                remotes[remote].set_repo_map(repo_map)
            else:
                log_warning(f"Remote '{remote}' doesn't exist, listed for projects:")
                for repo in repo_map:
                    print(" ", repo.name)

    def add_to_remote_map(self, remote_name, repo_name, rt):
        if remote_name not in self.remote_repo_map:
            self.remote_repo_map[remote_name] = dict()

        self.remote_repo_map[remote_name][repo_name] = rt

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
        config_dict["categories"] = categories
        if name in self.config.sections():
            print(f"{name} is already used")
            print(self.config.sections())
            return False
        try:
            repo = Repo(path)
        except:
            log_error(f"{path} is not a git repo")
            return
        _, parent = self.get_best_parent(self, path)
        if parent == None:
            log_error(f"Only paths in the home directoy are currently supported")
            return
        if path == parent.path:
            log_error(f"Path {path} used by {parent.name}")
            return False
        config_dict["parent"] = parent.name or ""
        # print(f"Best parent for {path} is {parent.path} with {val}")
        if parent.name != None:
            config_dict["path"] = os.path.relpath(path, parent.path)
        else:
            config_dict["path"] = "~/" +os.path.relpath(path, parent.path)
        # print(f"Adding {path} to {parent.path}/")
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

    def print_cats(self, cats=[]):
        if cats == list():
            cats = self.categories.keys()
        for cat in cats:
            if cat in self.categories:
                print(f"{cat}:")
                for name in [rep.name for rep in self.categories[cat]]:
                    print(" ", name)
            else:
                log_warning(f"'{cat}' is not a category")
        return 0

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

    class Remote:
        def __init__(self, repo, remote):
            self.name = remote["name"]
            self.repo = repo
            self.remote = remote

        # def __getitem__(self, item):
        #     return self.remote[item]

        def get_url(self):
            return (f'{self.remote["url"]}:{os.path.join(self.remote["path"], self.repo)}')

        def equals_url(self, url):
            return url == self.get_url()

        def get_remote_repo_id(self):
            return self.remote.get_remote_repo_id(self.repo)

        def as_dict(self):
            dic =  self.remote.as_dict()
            dic["remote-repo"] = self.repo
            return dic

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
        self.categories    = (section_get(section, "categories") or "").split()

        self.remotes = dict()

        for remote_repo in section:
            remote_name      = remote_repo[:-5]
            remote_repo_name = section[remote_repo]
            if remote_repo.endswith("-repo"):
                if remote_name in remotes:
                    self.remotes[remote_name] = self.Remote(remote_repo_name, remotes[remote_name])
                    # remote = add_remote( remotes[remote_name], section[remote_repo] )
                    # self.remotes[remote_name] = remote
                else:
                    log_warning(f"Remote '{remote_name}', listed in '{self.name}', doesn't exist, skipping")

        self.children = dict()

    def check_rid(self, fix=False):
        if not self.rid:
            if fix:
                self.set_id()
                if not self.rid:
                    log_warning(f"{self.rid} is missing and couldn't be fixed")
                    return 1
        else:
            return

    def check_origin(self, context, fix=False):
        if not self.origin:
            if self.originUrl and self.originPath:
                return 0
            else:
                log_error(f"Repo '{self.name}' should have origin or (originPath and originUrl)")
                return 1
        if self.origin not in self.remotes:
            if self.origin in context['remotes']:
                log_error(f"Origin '{self.origin}' for Repo '{self.name}' should have a -repo")
            else:
                log_error(f"Origin '{self.origin}' for Repo '{self.name}' does not exist")
            return 1

    def check_config_remotes(self, fix=False):
        "Checks if remotes in config exist in the repo"
        actual_remotes = {x.name : list(x.urls)[0] for x in list(self.repo.remotes)}
        for rname, remote in self.remotes.items():
            if rname not in actual_remotes:
                if fix:
                    self.add_remote(remote)
                    actual_remotes = {x.name : list(x.urls)[0] for x in list(self.repo.remotes)}
                    if rname not in actual_remotes:
                        log_error(f"Repo '{self.name}' is missing remote '{rname}', and couldn't be fixed")
                        return 1
                    print(f"Added remote '{rname}' to repo '{self.name}'")
                else:
                    log_warning(f"Repo '{self.name}' is missing remote {rname}")
                    return 1
            if not remote.equals_url(actual_remotes[rname]):
                if fix:
                    self.fix_remote(remote)
                    if not remote.equals_url(actual_remotes[rname]):
                        log_error(f"Repo '{self.name}' has INCORRECT remote {rname}, and couldn't be fixed")
                        return 1
                    print(f"Fixed incorrect remote '{rname}' for '{self.name}'")
                else:
                    log_error(f"Repo '{self.name}' has INCORRECT remote {rname}")

    def check_remote_repo_existence(self, fix=False):
        def check(rname, remote, fix=False):
            try:
                remote_id = remote.get_remote_repo_id()
                if remote_id == self.rid:
                    return 0
                else:
                    log_error(f"Remote '{rname}' for '{self.name}' is a different repo! Fix manual")
                    return 1
            except MissingRepoException:
                if fix:
                    self.add_to_remote(rname)
                    check(rname, remote, fix=False)
                else:
                    log_error(f"Repo '{remote.repo}' in '{rname}' for '{self.name}' is missing")
                    return 1
            except EmptyRepoException:
                log_warning(f"Remote '{rname}' for '{self.name}' exists but is empty")
                return 1

        for rname, remote in self.remotes.items():
            check(rname, remote, fix)

    def check_disk_path(self, context, fix=False):
        paths = [k for k, v in context["local_repos"].items() if v == self.rid]
        if not self.rid:
            return 0
        if self.path in paths:
            if len(paths) > 1:
                log_warning(f"Repo '{self.name}' exists in more than one place:")
                for path in paths:
                    if path == self.path:
                        print("", "(configured)", path)
                    else:
                        print("", path)
                    return 0
            else:
                return 0
        else:
            if len(paths) > 1:
                log_error(f"Repo '{self.name}' exists in more than one place but not the confgured one, cannot auto-fix")
                return 1
            else:
                if fix:
                    # move directory
                    print(f"CAN FIX, but not implemented")
                else:
                    log_warning(f"Repo '{self.name}' exists in {paths[0]} instead of configured {self.path}")
                    return 1

    def do_sanity_checks(self, context, fix=False):
        if self.missing:
            return
        # run checks
        self.check_rid(fix)
        self.check_config_remotes(fix)
        self.check_remote_repo_existence(fix)
        self.check_disk_path(context, fix)
        self.check_origin(fix)

    def fix_remote(self, remote):
        "Change the remote url to match the config"

    def add_remote(self, remote):
        "Add remote to the repo"
        self.repo.create_remote(remote.name, remote.get_url())

    def add_to_remote(self, remote):
        "Add repo to the remote and vv"
        print("adding repo to", type(remote))

    def add_parent(self, parent):
        parent.add_child(self)
        self.parent = parent

    def add_child(self, child):
        self.children[child.name] = child

    def install(self):
        # print(self.remotes)
        origin = self.remotes[self.origin]
        command = f"git clone {origin.get_url()} {self.path}"
        os.system(f"mkdir -p {self.path}")
        os.system(command)
        self.repo = Repo(self.path)
        for remote in self.remotes.values():
            self.add_remote(remote)

    def final_update(self):
        if self.parent:
            self.path = os.path.realpath(os.path.join(self.parent.path, self.relative_path))
        else:
            self.path = os.path.realpath(os.path.abspath(os.path.expanduser(self.relative_path)))
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
                "remotes": [r.as_dict() for r in self.remotes.values()],
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
                rid = remote.get_remote_repo_id()
                if rid:
                    break
        if rid:
            self.rid = rid
            self.section["repo_id"] = rid
            self.root.changed = True
        else:
            if self.missing:
                log_error(f"Couldn't set id for missing {self.path}")
            else:
                log_error(f"Couldn't set id for local {self.path}")
            return 1

    def status(self, root="~", recursive=False, dirty=False, missing=True, indent=0):
        if self.missing:
            if self.parent:
                path = os.path.relpath(self.path, self.parent.path)
            else:
                if root == "~":
                    path = "~/" + os.path.relpath(self.path, os.path.expanduser(root)) + str(self.parent) + "asdf"
                else:
                    path = os.path.relpath(self.path, os.path.expanduser(root))
            if missing:
                print("missing", " "*indent + path)
            return

        if self.parent:
            path = "/" + os.path.relpath(self.repo.working_dir, self.parent.path)
        else:
            if root == "~":
                path = "~/" + os.path.relpath(self.repo.working_dir, os.path.expanduser(root))
            else:
                path = os.path.relpath(self.repo.working_dir, os.path.expanduser(root))
        if self.repo.is_dirty():
            print("dirty  ", " "*indent + path)
        else:
            try:
                commits_behind = len(list(self.repo.iter_commits('master..origin/master')))
            except:
                commits_behind = 0
            try:
                commits_ahead  = len(list(self.repo.iter_commits('origin/master..master')))
            except:
                commits_ahead  = 0

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
            self.section["categories"] = " ".join(self.categories)
            self.root.changed=True

    def remove_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
            self.section["categories"] = " ".join(self.categories)
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
