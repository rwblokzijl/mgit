from mgit.local.state import NamedRemoteRepo

from mgit.util.exceptions import InputError

from typing import Set

class RemoteParser:
    def __init__(self, config):
        self.config = config

    def _split_remote_and_repo(self, default_name:str, remote_repo_name:str):
        if ':' in remote_repo_name:
            return remote_repo_name.split(":")
        else:
            return remote_repo_name, default_name

    def _parse_remote_input(self, default_name: str, remote_repo_name: str) -> NamedRemoteRepo:
        remote_name, name = self._split_remote_and_repo(default_name, remote_repo_name)
        remote = self.config.get_remote(remote_name)
        if not remote:
            raise InputError(f"'{remote_name}' is not a known remote")
        return NamedRemoteRepo(remote=remote, project_name=name)

    def _get_default_remote_repos(self, name: str) -> Set[NamedRemoteRepo]:
        remotes = self.config.get_default_remotes()
        remote_repos = {NamedRemoteRepo(remote=remote, project_name=name) for remote in remotes}
        return remote_repos

    def parse(self, default_name, remote_names) -> Set[NamedRemoteRepo]:
        # TODO: Allow UnnamedRemoteRepo?
        if remote_names is None:
            return self._get_default_remote_repos(default_name)
        return {self._parse_remote_input(default_name, remote) for remote in remote_names}

class RepoStateParser:
    pass

class RepoStateOrAllParser:
    pass
