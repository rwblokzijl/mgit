from mgit.util import *

import json
import copy

class RemotesCreator:

    def __init__(self, remotePersistence):
        self.changed = False
        remote_data = remotePersistence.read_all()
        self.save_as_remotes(remote_data)

    def save_as_remotes(self, remote_data):
        self.remotes = dict()
        for k, v in remote_data.items():
            self.validate_and_add_remote(k, v)

    def validate_and_add_remote(self, key, remote_dict):
        if self.should_ignore_dict(remote_dict):
            return
        self.validate_remote_dict_name(key, remote_dict)
        self.validate_remote_dict_required_fields(key, remote_dict)
        self.validate_remote_dict_type(key, remote_dict)

        default = remote_dict.get("is_default", False)
        self.validate_remote_dict_default(key, default)

        port = remote_dict.get("port", 22)
        self.validate_remote_dict_port(key, port)

        # self.remotes[name]  = Remote(vals={
        self.remotes[key]  = {
            'name': remote_dict["name"],
            'url': remote_dict["url"],
            'path': remote_dict["path"],
            'type': remote_dict["type"],
            'port': port,
            'is_default': default
            }#)

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
        rtype    = remote_dict.get("type", None)
        if rtype is None:
            return
        else:
            if HandlerHandler().check_type(rtype):
                return
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

    def should_ignore_dict(self, remote_dict):
        return "ignore" in remote_dict and remote_dict["ignore"]

    def remote_or_none(self, name, url, path, rtype, default, port=22):
        if rtype is None:
            rtype = get_type_from_url(url)
        if rtype is None:
            log_warning(f"Could not infer type for remote '{name}'")
            return None
        return Remote(vals={
            'name': name,
            'url': url,
            'path': path,
            'type': rtype,
            'port': port,
            'is_default': default
            })

    def remote_or_none_from_vals(self, vals):
        if "name"       not in vals:
            log_error("Missing name in " + json.dumps(vals))
            return None
        if "path"       not in vals:
            log_error(f"""Missing path for '{vals["name"]}'""")
            return None
        if "url"        not in vals:
            log_error(f"""Missing url for '{vals["name"]}'""")
            return None
        if "is_default" not in vals:
            log_error(f"""Missing is_default for '{vals["name"]}'""")
            return None

        if "type" in vals:
            rtype = vals["type"]
        else:
            rtype = None
        return self.remote_or_none(vals["name"], vals["url"], vals["path"], rtype, vals["is_default"], vals.get("port", 22))

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
        return [ v.as_dict() for k,v in self.remotes.items() ]

    def __str__(self):
        return json.dumps(self.as_dict(), indent=4)

    def add(self, name, url, type, is_default=False):
        # assert name not in self, f"'{name}' already exists"
        to_add = dict()
        to_add["name"] = name
        to_add["url"], to_add["path"] = url.split(":")
        to_add["type"] = type
        to_add["is_default"] = is_default
        self.__setitem__(name, to_add)

    def __setitem__(self, key, item):
        assert isinstance(item, dict)
        assert item["name"] == key, f"Key '{key}' does not match remote name '" + item["name"] + "'"

        r = self.remote_or_none_from_vals(vals=item)
        if r:
            self.remotes[key] = r
            self.config[key] = r.as_config()
            if item["is_default"]:
                self.config['defaults'][key] = 1
            # print(f'Added remote {key} at {item["url"]}:{item["path"]}')
            self.changed = True
        else:
            raise
            # print(f"Missing values for {key}")

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

    class InvalidConfigError(Exception):
        pass

class Remotes(RemotesCreator):
    def __init__(self, path):
        persistence = RemoteConfigFilePersistence(path)
        super().__init__(persistence)

class Remote:
    def __init__(self, vals=None, name=None, url=None, path=None, remote_type=None, default=False, port=22):
        self.repo_map = None # init None, not dict, if we accidentally use it witout settign later, we get an active error
        assert (
                vals or
                (name and url and path and remote_type)
                ), "Either set vals, or name and url and path"
        if vals:
            self.vals = {
                    "name" : vals['name'],
                    "url" : vals['url'],
                    "path" : vals['path'],
                    "type" : vals['type'],
                    "port" : vals['port'],
                    "is_default" : vals['is_default']
                    }
        else:
            self.vals = {
                    "name" : name,
                    "url" : url,
                    "path" : path,
                    "type" : remote_type,
                    "port" : port,
                    "is_default" : default
                    }

        username, nurl = self.vals["url"].split("@")
        self.handler = HandlerHandler().get_handler( username, nurl, self.vals["path"], self.vals["type"], self.vals["port"])# .get_handler(self.vals["type"])

    def set_repo_map(self, repo_map):
        self.repo_map = repo_map

    def __getitem__(self, key):
        return self.vals[key]

    def __setitem__(self, key, value):
        assert False, "Do not set the remote directly, all interaction should happen through the Remotes class"

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

    def get_remote_repo_id(self, name):
        return self.handler.get_remote_repo_id(name)

    def get_remote_repo_id_map(self):
        return self.handler.get_remote_repo_id_map()

    def list(self):
        installed = list()
        missing = list()
        archived = list()
        untracked = list()
        all_repos = self.handler.list()
        for repo_name in all_repos:
            if repo_name in self.repo_map:
                repo = self.repo_map[repo_name]
                if not repo.missing:
                    installed.append(repo)
                else:
                    if repo.archived:
                        archived.append(repo)
                    else:
                        missing.append(repo)
            else:
                untracked.append(repo_name)

        return installed, missing, archived, untracked

class RemoteHandler:
    def __init__(self, username, url, path, htype, port=22):
        self.username = username
        self.url = url
        self.path = path
        self.type = htype
        self.port=port

        self.repo_id_map = dict()
        self.repo_id_map_all = False

    def __str__(self):
        return f"{self.username}@{self.url}:{self.path}"

    def list(self):
        pass

    def init_repo(self):
        pass

    def get_remote_repo_id(self, name):
        log_error(f"Cannot get ids for {self.type}")

    def get_remote_repo_id_map(self):
        log_error(f"Cannot get ids for {self.type}")

class SSHHandler(RemoteHandler):
    def init_repo(self, name, remote_name):
        pass

    def list(self):
        command = f"ls {self.path}"
        return run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()

    def get_remote_repo_id_map(self):
        if self.repo_id_map_all:
            return self.repo_id_map
        names = self.list()#[0:2]
        command = ""
        for name in names:
            path = os.path.join(self.path, name)
            command += f"echo {name}; cd {path} && (git rev-list --parents HEAD || echo false) | tail -1;"
        result = run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()
        clean = [ str(x.strip()) for x in result ]
        self.repo_id_map = {name : rid for name, rid in pairwise(clean) if rid != "false"}
        self.repo_id_map_all = True
        return self.repo_id_map

    def get_remote_repo_id(self, name):
        if name in self.repo_id_map:
            return self.repo_id_map[name]
        path = os.path.join(self.path, name)
        command = f"cd {path} && (git rev-list --parents HEAD || echo false) | tail -1"
        git_id, = [str(x.strip()) for x in run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()]
        # print(git_id)
        if git_id == "false": #Git repo doesn't exist, OR Git repo exists, but has no commits yet
            command = f"cd {path} && git tag || echo false"
            result = [str(x.strip()) for x in run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()]
            self.repo_id_map[name] = None
            if result == ["false"]:
                raise MissingRepoException
            else:
                raise EmptyRepoException
        else:
            self.repo_id_map[name] = git_id
        return self.repo_id_map[name]

    class MissingRepoException(Exception):
        "Git repo doesn't exist"

    class EmptyRepoException(Exception):
        "Git repo is empty"

class GithubHandler(RemoteHandler):
    pass

class GitlabHandler(RemoteHandler):
    pass

class BitbucketHandler(RemoteHandler):
    pass

# Helper
class HandlerHandler:
    def __init__(self):
        self.type_map = {
                "ssh" : SSHHandler,
                "github" : GithubHandler,
                "gitlab" : GitlabHandler,
                "bitbucket" : BitbucketHandler
                }

    def check_type(self, type):
        if type in self.type_map:
            return True
        else:
            return False

    def get_handler(self, username, url, path, htype, port=22):
        handler = self.type_map.get(htype, None)
        if self.type_map is None:
            raise TypeError("Invalid type {htype}")
        return handler(username, url, path, htype, port)

