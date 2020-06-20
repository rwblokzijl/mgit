import os

from abc import ABC, abstractmethod

class RepoRemote(ABC):
    @abstractmethod
    def get_url(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    def as_dict(self):
        return {
                "name" : self.get_name(),
                "url" : self.get_url(),
                }

class DerivedRepoRemote(RepoRemote):
    def __init__(self, remote, repo_name):
        self.remote = remote
        self.repo_name = repo_name
        self.validate_url()

    def validate_url(self):
        url = self.remote.get_url()
        if not url.endswith(":") and self.repo_name.startswith("/"):
            raise self.InvalidPathError("Cannot append absolute path to relative URL not ending in ':', ")

    def get_url(self):
        url = self.remote.get_url()
        if url.endswith(":"):
            return url + self.repo_name
        else:
            return os.path.join(url, self.repo_name)

    def get_name(self):
        return self.remote.name

    class InvalidPathError(Exception):
        pass

class UnnamedRepoOrigin(RepoRemote):
    def __init__(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def get_name(self):
        return "origin"
