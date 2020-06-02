from util import *

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

    def remote_or_none(self, name, url, path, rtype, default):
        if rtype is None:
            rtype = get_type_from_url(url)
        if rtype is None:
            return None
        return Remote(vals={
            'name': name,
            'url': url,
            'path': path,
            'type': rtype,
            'is_default': default
            })

    def remote_or_none_from_vals(self, vals):
        if "name"       not in vals:
            print("Missing name in " + json.dumps(vals))
            return None
        if "path"       not in vals:
            print(f"""Missing path for '{vals["name"]}'""")
            return None
        if "url"        not in vals:
            print(f"""Missing url for '{vals["name"]}'""")
            return None
        if "is_default" not in vals:
            print(f"""Missing is_default for '{vals["name"]}'""")
            return None

        if "type" in vals:
            rtype = vals["type"]
        else:
            rtype = None
        return remote_or_none(vals["name"], vals["url"], vals["path"], rtype, vals["is_default"])

    def remote_or_none_from_config(self, remote, configObj):
        try:
            rtype = configObj[remote]['type']
        except:
            rtype = None
        return self.remote_or_none( remote, configObj[remote]['url'], configObj[remote]['path'], rtype, remote in configObj['defaults'] )

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
    def __init__(self, vals=None, name=None, url=None, path=None, remote_type=None, default=False):
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
                    "is_default" : vals['is_default']
                    }
        else:
            self.vals = {
                    "name" : name,
                    "url" : url,
                    "path" : path,
                    "type" : remote_type,
                    "is_default" : default
                    }

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

class RemoteHandler:
    def __init__(self, username, url, path):
        self.username = username
        self.url = url
        self.path = path

    def __str__(self):
        return f"{self.username}@{self.url}:{self.path}"

    def list(self):
        pass

    def init_repo(self):
        pass

class SSHHandler(RemoteHandler):
    def init_repo(self, name, remote_name):
        pass

    def list():
        command = f"ls {self.path}"
        return run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()

class GithubHandler(RemoteHandler):
    pass

class GitlabHandler(RemoteHandler):
    pass

class BitbucketHandler(RemoteHandler):
    pass
