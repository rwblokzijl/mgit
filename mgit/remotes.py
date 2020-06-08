from mgit.util import *

import json

class MissingRepoException(Exception):
    "Git repo doesn't exist"

class EmptyRepoException(Exception):
    "Git repo doesn't exist"

class Remotes:
    def __init__(self, remotes_config, default=False):
        self.changed = False
        self.configPath = os.path.abspath(os.path.expanduser(remotes_config))
        self.default = default
        self.config = configparser.ConfigParser()

        self.config.read(self.configPath)

        # self.remotes

        if default:
            rlist =  [self.remote_or_none_from_config(x, self.config) for x in self.config['defaults'] if self.remote_in_config(x, self.config)]
        else:
            rlist =  [self.remote_or_none_from_config(x, self.config) for x in self.config if self.remote_in_config(x, self.config)]

        self.remotes = {r["name"]: r for r in rlist if r}

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

    def remote_or_none_from_config(self, remote, configObj):
        try:
            rtype = configObj[remote]['type']
        except:
            rtype = None
        return self.remote_or_none( remote, configObj[remote]['url'], configObj[remote]['path'], rtype, remote in configObj['defaults'], section_get(remote, "port") )

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

    def __setitem__(self, key, item):
        assert isinstance(item, dict)
        assert item["name"] == key, f"Key '{key}' does not match remote name '" + item["name"] + "'"

        r = self.remote_or_none_from_vals(vals=item)
        if r:
            self.remotes[key] = r
            self.config[key] = r.as_config()
            if self.default:
                self.config['defaults'][key] = 1
            print(f'Added remote {key} at {item["url"]}:{item["path"]}')
            self.changed = True
        else:
            print(f"Missing values for {key}")

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
        self.handler = get_handler( username, nurl, self.vals["path"], self.vals["type"], self.vals["port"])# .get_handler(self.vals["type"])

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

class GithubHandler(RemoteHandler):
    pass

class GitlabHandler(RemoteHandler):
    pass

class BitbucketHandler(RemoteHandler):
    pass

# Helper
def get_handler(username, url, path, htype, port=22):
    type_map = {
            "ssh" : SSHHandler,
            "github" : GithubHandler,
            "gitlab" : GitlabHandler,
            "bitbucket" : BitbucketHandler
            }
    return type_map.get(htype, None)(username, url, path, htype, port)

