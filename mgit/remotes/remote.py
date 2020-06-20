from mgit.util import *

import json
import copy

class Remote:
    def __init__(self, name, url, path, remote_type, default, port):

        self.repo_map = None # init None, not dict, if we accidentally use it witout settign later, we get an active error

        self.name       = name
        self.url        = url
        self.path       = path
        self.type       = remote_type
        self.port       = port
        self.is_default = default

        # username, nurl = self.url.split("@")
        # self.handler = HandlerHandler().get_handler( username, nurl, self.path, self.type, self.port)# .get_handler(self.vals["type"])

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

    def __str__(self):
        return json.dumps(self.as_dict(), indent=4)

    # def get_remote_repo_id(self, name):
    #     return self.handler.get_remote_repo_id(name)

    # def get_remote_repo_id_map(self):
    #     return self.handler.get_remote_repo_id_map()

    # def list(self):
    #     installed = list()
    #     missing = list()
    #     archived = list()
    #     untracked = list()
    #     all_repos = self.handler.list()
    #     for repo_name in all_repos:
    #         if repo_name in self.repo_map:
    #             repo = self.repo_map[repo_name]
    #             if not repo.missing:
    #                 installed.append(repo)
    #             else:
    #                 if repo.archived:
    #                     archived.append(repo)
    #                 else:
    #                     missing.append(repo)
    #         else:
    #             untracked.append(repo_name)
    #     return installed, missing, archived, untracked

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
