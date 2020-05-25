from util import *
from config import RemotesConfig, RepoTree

from git import Repo as GitRepo
"""
Think: having seperate handlers is a good enough idea, but
Should remote and remote config be merged?
pros:
    simpler
    can always split later
cons:
    do we want remotes from a non default source
        we would require: url -> user, url, path, no problem git does this too
        we also need the type (sometimes), type can be inferred from a github,
        gitlab bitbucket url
"""

class Remotes:
    def __init__(self, remote_dict_list, remotes_config):
        """
        remote_dict_list = [{
            "url" : url,
            "path": path
            "type" : type,
        }, ]
        """

        # create a remote for each entry in config

        self.remotes = [
                Remote(None, r_dict["url"], r_dict["path"], r_dict["type"], None)
                for r_dict in self.remote_dict_list.items()
                ]

        self.remote += [
                Remote(remote['name'], remote['url'], remote['path'], remote['type'], config=remote)
                for remote in remotes_config:
                ]


class Remote():
    def __init__(self, name, url, path, remote_type, config=None):

        self.name               = name
        self.username, self.url = url.split("@")
        self.path               = path
        self.config             = config

        handler_map = {
                'ssh'       : SSHHandler,
                'github'    : GithubHandler,
                'gitlab'    : GitlabHandler,
                'bitbucket' : BitbucketHandler,
                }

        self.handler = self.handler_map[remote_type](self.username, self.url, self.path)

    def init_repo(self, repo):
        return self.handler.init_repo()

    def list(self):
        return self.handler.list()


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
