from mgit.state.state import RepoState, RemoteRepo, NamedRemoteRepo, UnnamedRemoteRepo, Remote, AutoCommand, RemoteBranch, LocalBranch, RemoteType

from typing import Optional
from pathlib import Path

import configparser
import os

class ConfigStateInteractor:

    """
    Reads config state and returns a RepoState object

    Holds the config as a dict, reads the dict based on queries

    [Example]
    repo_id = 42f590dc08f39a8a19a8364fbed2fa317108abe6
    path = ~/devel/example/path
    origin = home
    categories = school devel
    home-repo = CS4200-B/2018-2019/student-rblokzijl.git
    archived = 1
    parent = some_other_section
    ignore = 1
    """

    def get_state(self, repo_id: Optional[str]=None, name: Optional[str]=None):
        assert not (repo_id and name), "Only please specify only 1 arg"
        assert      repo_id or  name,  "Please specify 1 arg"
        if repo_id:
            return self._get_state_by_id(repo_id)
        if name:
            return self._get_state_by_name(name)
        return None

    def set_state(self, path):
        raise NotImplementedError("Not yet implemented")

    def __init__(self,
            remotes_file="~/.config/mgit/remotes.ini",
            repos_file="~/.config/mgit/repos.ini"):

        self._remotes_file = os.path.abspath(os.path.expanduser(remotes_file))
        self._repos_file = os.path.abspath(os.path.expanduser(repos_file))

        self._remotes_config, self._repos_config = self._read_configs()
        self._remote_type_map = {
                "ssh" : RemoteType.SSH,
                "github" : RemoteType.GITHUB,
                "gitlab" : RemoteType.GITLAB,
                }

    def _read_configs(self):
        repos = configparser.ConfigParser()
        if not repos.read(self._repos_file):
            raise FileNotFoundError(f"Failed to open {self._repos_file}")

        remotes = configparser.ConfigParser()
        if not remotes.read(self._remotes_file):
            raise FileNotFoundError(f"Failed to open {self._remotes_file}")

        return remotes, repos

    def _get_parent(self, name, section):
        parent_name = section.get("parent")

        if not parent_name:
            return None
        if parent_name not in self._repos_config:
            raise ReferenceError(f"Listed parent {parent_name} for {name} doesn't exist")

        parent_section = self._repos_config[parent_name]
        return self._config_section_to_repo(parent_name, parent_section)

    def _config_section_to_remote(self, name):
        if name not in self._remotes_config:
            return None
        section = self._remotes_config[name]

        return Remote(
                name=name,
                url=section.get("url"),
                path=section.get("path"),
                remote_type=self._remote_type_map.get(section.get("type"))
                )

    def _get_remote(self, repo_name, remote_name):
        remote_repo = self._config_section_to_remote(remote_name)
        if not remote_repo:
            return None
        return NamedRemoteRepo(remote_repo, repo_name)

    def _get_remotes(self, name, section):
        remotes = set()
        for key in section:
            if key.endswith("-repo"):
                name        = section.get(key)
                remote_name = key[:-5]
                remote_repo = self._get_remote(name, remote_name)
                if not remote_repo:
                    raise ReferenceError(f"Listed remote {name} for {name} doesn't exist")
                remotes.add(remote_repo)
        return remotes

    def _get_origin(self, remotes, name, section):
        if "origin" not in section:
            return None
        origin = section["origin"]
        for remote_repo in remotes:
            if type(remote_repo) == NamedRemoteRepo and remote_repo.remote.name == origin:
                return remote_repo
        raise ReferenceError(f"Listed origin {origin} for {name} doesn't exist")

    def _get_categories(self, section):
        return set(section.get("categories", "").split())

    def _config_section_to_repo(self, name, section):
        if section.get("ignore"):
            return None

        parent = self._get_parent(name, section)

        sub_path = section.get("path")
        if sub_path:
            if parent:
                path = os.path.join(parent.path, sub_path)
            else:
                path = sub_path
        else:
            path = None

        remotes = self._get_remotes(name, section)

        return RepoState(
                source="config",
                repo_id=section.get("repo_id"),
                path=Path(path).expanduser(),
                remotes=remotes,
                name=name,
                origin=self._get_origin(remotes, name, section),
                auto_commands = None, #TODO
                categories=self._get_categories(section),
                parent=parent,
                archived=bool(section.get("archived"))
                )

    def _get_state_by_name(self, name):
        if name in self._repos_config:
            return self._config_section_to_repo(name, self._repos_config[name])

    def _get_state_by_id(self, repo_id):
        for name, repo in self._repos_config.items():
            if repo.get("repo_id") == repo_id:
                return self._config_section_to_repo(name, repo)
