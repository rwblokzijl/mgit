from git import Repo
from git.exc import InvalidGitRepositoryError

import os

class LocalSystem:

    def path_available(self, path):
        if self.is_git_repo(path):
            return False
        return True

    def is_git_repo(self, path):
        if not os.path.exists(path):
            return False
        try:
            _ = Repo(path).git_dir
            return True
        except InvalidGitRepositoryError:
            return False

    def ensure_directory(self, path):
        os.makedirs(path, exist_ok=True)

    def add_remotes(self, repo, remotes):
        for remote, url in remotes.items():
            repo.create_remote(remote, url)

    def add_origin(self, repo, origin, remotes):
        if origin in remotes:
            repo.create_remote("origin", remotes[origin])
        else:
            raise self.MissingRemoteError()

    def validate_origin(self, origin, remotes):
        if origin and origin not in remotes:
            raise self.MissingRemoteError()

    def init(self, path, remotes={}, origin=None):
        self.validate_origin(origin, remotes)
        self.ensure_directory(path)

        repo = Repo.init(path)

        self.add_remotes(repo, remotes)
        if origin:
            self.add_origin(repo, origin, remotes)

    class MissingRemoteError(Exception):
        pass
