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

class Remote():
    def __init__(self, name, username, url, path, remote_type):
        self.name = username
        self.url = url
        self.path = path

        handler_map = {
                'ssh'       : SSHRemote,
                'github'    : GithubHandler,
                'gitlab'    : GitlabHandler,
                'bitbucket' : BitbucketHandler,
                }

        self.handler = self.handler_map[remote_type]()


class RemoteHandler:
    def __init__(self, url):
        self.url = url

    def list(self):
        pass

    def init_repo(self):
        pass

class SSHRemote(RemoteHandler):
    pass

class GithubHandler(RemoteHandler):
    pass

class GitlabHandler(RemoteHandler):
    pass

class BitbucketHandler(RemoteHandler):
    pass
