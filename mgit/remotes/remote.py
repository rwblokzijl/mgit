# from mgit.util import *

from pathlib import Path
from fabric import Connection

from git import Repo

import json
import copy
import os

class Remote:
    def __init__(self, name, url, path, remote_type, default, port, base_data):

        self.base_data  = base_data

        self.name       = name
        self.url        = url
        self.path       = path
        self.type       = remote_type
        self.port       = port
        self.is_default = default

        if "@" in self.url:
            username, nurl = self.url.split("@")
        else:
            self.type = "local"
            username = ""
            nurl = self.url

        self.handler = HandlerHandler().get_handler( username, nurl, self.path, self.type, self.port)# .get_handler(self.vals["type"])

    def as_dict(self):
        return {
                "name" : self.name,
                "url" : self.url,
                "path" : self.path,
                "type" : self.type,
                "port" : self.port,
                "is_default" : self.is_default
                }

    def get_url(self):
        return f"{self.url}:{self.path}"

    def get_url_with_repo(self, repo_path):
        return f"{self.url}:{os.path.join(self.path, repo_path)}"

    def init(self, name):
        self.handler.init_repo(name)

    def __str__(self):
        return json.dumps(self.as_dict(), indent=4)

    def __contains__(self, repo):
        try:
            self.handler.get_remote_repo_id(repo)
            return True
        except RemoteHandler.MissingRepoException:
            return False
        except RemoteHandler.EmptyRepoException:
            return True

    # def get_remote_repo_id(self, name):
    #     return self.handler.get_remote_repo_id(name)

    # def get_remote_repo_id_map(self):
    #     return self.handler.get_remote_repo_id_map()

    def list(self):
        return self.handler.list()

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

    class MissingRepoException(Exception):
        "Git repo doesn't exist"

    class EmptyRepoException(Exception):
        "Git repo is empty"

class SSHHandler(RemoteHandler):

    def run_ssh(self, *args, username, remote, port=22, **kwargs):
        with Connection(remote, user=username, port=port) as ssh:
            return ssh.run(*args, warn=True, **kwargs)

    def exists_remote(self, remote_path):
        ans = self.run_ssh('[ -d "'+remote_path+'" ]', username=self.username, remote=self.url)
        if ans.return_code == 0:
            return True
        else:
            return False

    def init_repo(self, project_name):
        remote_path = os.path.join(self.path, project_name)
        remote_url = self.username+"@"+self.url+":"+remote_path
        if self.exists_remote(remote_path):
            print("WARNING: Remote folder already exists, not creating remote repo")
            return remote_url
        # print("Creating remote: " + remote_url)
        if not self.run_ssh('mkdir ' + remote_path, username=self.username, remote=self.url):
            log_error("Couldn't create folder, check permissions")
            raise
        if not self.run_ssh('git init --bare ' + remote_path, username=self.username, remote=self.url, hide=True):
            log_error("Created folder but could not init repo, manual action required")
            raise
        return remote_url

    def list(self):
        command = f"ls {self.path}"
        return self.run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()

    def get_remote_repo_id_map(self):
        if self.repo_id_map_all:
            return self.repo_id_map
        names = self.list()#[0:2]
        command = ""
        for name in names:
            path = os.path.join(self.path, name)
            command += f"echo {name}; cd {path} && (git rev-list --parents HEAD || echo false) | tail -1;"
        result = self.run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()
        clean = [ str(x.strip()) for x in result ]
        self.repo_id_map = {name : rid for name, rid in pairwise(clean) if rid != "false"}
        self.repo_id_map_all = True
        return self.repo_id_map

    def get_remote_repo_id(self, name):
        if name in self.repo_id_map:
            return self.repo_id_map[name]
        path = os.path.join(self.path, name)
        if not self.exists_remote(path):
            # print("Remote folder already exists, not creating remote repo")
            raise self.MissingRepoException
        command = f"cd {path} && (git rev-list --parents HEAD || echo false) | tail -1"
        git_id, = [str(x.strip()) for x in self.run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()]
        # print(git_id)
        if git_id == "false": #Git repo doesn't exist, OR Git repo exists, but has no commits yet
            command = f"cd {path} && git tag || echo false"
            result = [str(x.strip()) for x in self.run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()]
            self.repo_id_map[name] = None
            if result == ["false"]:
                raise self.MissingRepoException
            else:
                raise self.EmptyRepoException
        else:
            self.repo_id_map[name] = git_id
        return self.repo_id_map[name]

class GithubHandler(RemoteHandler):
    pass

class LocalRemoteHandler(RemoteHandler):

    def init_repo(self, name):
        path = Path(self.url) / self.path / name
        Repo.init(path)

    def get_remote_repo_id(self, name):
        path = Path(self.url) / self.path / name
        if not os.path.exists(path):
            raise self.MissingRepoException
        if os.listdir(path):
            raise self.EmptyRepoException
        command = f"cd {path} && (git rev-list --parents HEAD || echo false) | tail -1"
        idd = self.run_command(command)
        print(list(idd))

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
                "bitbucket" : BitbucketHandler,
                "local" : LocalRemoteHandler
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

