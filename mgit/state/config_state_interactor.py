from mgit.state.state import RepoState, RemoteRepo, NamedRemoteRepo, UnnamedRemoteRepo, Remote, AutoCommand, RemoteBranch, LocalBranch, RemoteType

from typing import Optional, Union
from pathlib import Path

import configparser
import os
import dataclasses

class ConfigStateInteractor:

    """
    Reads config state and returns a RepoState object

    Holds the config as a dict, reads the dict based on queries

    [Example]
    repo_id = 42f590dc08f39a8a19a8364fbed2fa317108abe6
    path = ~/devel/example/path
    categories = school devel
    home-repo = CS4200-B/2018-2019/student-rblokzijl.git
    archived = 1
    parent = some_other_section
    ignore = 1
    """

    def get_state(self, repo_id: Optional[str]=None, name: Optional[str]=None, path: Union[Path, str, None]=None) -> Optional[RepoState]:
        if repo_id:
            ans = self._get_state_by_id(repo_id)
            if ans:
                return ans
        if name:
            ans = self._get_state_by_name(name)
            if ans:
                return ans
        if path:
            ans = self._get_state_by_path(path)
            if ans:
                return ans
        return None

    def remove_state(self, repo_state: RepoState):
        old_state = self._get_state_from_state(repo_state)
        if old_state is None:
            return
        del(self._repos_config[old_state.name])
        self._write_configs()

    def set_state(self, repo_state: RepoState, force=False) -> Optional[RepoState]:
        """
        Updates an existing config with the values in the config
        force: also deletes keys that are missing from the RepoState
        """
        repo_keys = list(dataclasses.asdict(repo_state).keys())
        old_state = self._get_state_from_state(repo_state)
        if old_state is None:
            if not force:
                # Create new
                if not repo_state.name:
                    raise ValueError(f"New repo_state should have a name")
                self._repos_config.add_section(repo_state.name)
            else:
                return None
        repo_keys.remove("source")
        repo_keys.remove("name")
        section = self._repos_config[repo_state.name]

        # self._write_repo_id(section, repo_id, force)
        if repo_state.repo_id is not None:
            section["repo_id"] = repo_state.repo_id
        elif force and "repo_id" in section:
            del(section["repo_id"])
        repo_keys.remove("repo_id")

        if repo_state.path is not None:
            if not repo_state.path.is_absolute:
                raise ValueError(f"Path {repo_state.path} for {repo_state.name} is not valid")
            if repo_state.parent:
                if repo_state.parent.path is not None:
                    section["path"] = str(repo_state.path.relative_to(repo_state.parent.path)).strip("/")
            else:
                section["path"] = str(repo_state.path)
        elif force and "path" in section:
            del(section["path"])
        repo_keys.remove("path")

        if force:
            for key in section.keys():
                if key.endswith("-repo") or key.endswith("-remote"):
                    del(section[key])
        for remote_repo in repo_state.remotes:
            if isinstance(remote_repo, NamedRemoteRepo):
                # remote_repo: NamedRemoteRepo = remote_repo
                key = remote_repo.remote.name + '-repo'
                value = remote_repo.project_name
            elif isinstance(remote_repo, UnnamedRemoteRepo): #TODO attempt resolve to named?
                # remote_repo: UnnamedRemoteRepo = remote_repo
                key = remote_repo.remote_name + '-remote'
                value = remote_repo.get_url()
            else:
                raise NotImplementedError("Unknown remote type")
            section[key] = value
        repo_keys.remove("remotes")

        # origin=self._get_origin(remotes, name, section),

        # auto_commands = None, #TODO
        repo_keys.remove("auto_commands")

        if repo_state.categories is not None:
            if force or old_state is None:
                section["categories"] = " ".join(sorted(list(repo_state.categories)))
            else:
                section["categories"] = " ".join(sorted(list(repo_state.categories | (old_state.categories or set()))))
        elif force and "categories" in section:
            del(section["categories"])
        repo_keys.remove("categories")

        if repo_state.parent is not None:
            section["parent"] = repo_state.parent.name
        elif "parent" in section: # also if not force
                del(section["parent"])
        repo_keys.remove("parent")

        if repo_state.archived == True:
            section["archived"] = "1"
        elif repo_state.archived == False or (force and repo_state.archived is None):
            if "archived" in section:
                del(section["archived"])
        repo_keys.remove("archived")

        assert not repo_keys, repo_keys
        self._write_configs()
        return repo_state

    def _get_state_from_state(self, repo_state: RepoState) -> Optional[RepoState]:
        return self.get_state(repo_id=repo_state.repo_id, name=repo_state.name, path=repo_state.path)

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

    def _write_configs(self):
        with open(self._repos_file, 'w') as configfile:
            self._repos_config.write(configfile)
        with open(self._remotes_file, 'w') as configfile:
            self._remotes_config.write(configfile)

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

    # def _get_origin(self, remotes, name, section):
    #     if "origin" not in section:
    #         return None
    #     origin = section["origin"]
    #     for remote_repo in remotes:
    #         if type(remote_repo) == NamedRemoteRepo and remote_repo.remote.name == origin:
    #             return remote_repo
    #     raise ReferenceError(f"Listed origin {origin} for {name} doesn't exist")

    def _get_categories(self, section):
        return set(section.get("categories", "").split())

    def _config_section_to_repo(self, name: str, section):
        if section.get("ignore"):
            return None

        parent = self._get_parent(name, section)

        sub_path = section.get("path")
        if not sub_path:
            raise ValueError(f"Config section {name}, doesn't have a path")

        if parent:
            path = os.path.join(parent.path, sub_path)
        else:
            path = sub_path

        if path and not Path(path).expanduser().is_absolute():
            raise ValueError(f"Path {path} for {name} in config is not valid")

        remotes = self._get_remotes(name, section)

        return RepoState(
                source="config",
                repo_id=section.get("repo_id"),
                path=Path(path),
                remotes=remotes,
                name=name,
                # origin=self._get_origin(remotes, name, section),
                auto_commands = None, #TODO
                categories=self._get_categories(section),
                parent=parent,
                archived=bool(section.get("archived"))
                )

    def _get_state_by_name(self, name: str) -> Optional[RepoState]:
        if name in self._repos_config:
            return self._config_section_to_repo(name, self._repos_config[name])
        return None

    def _get_state_by_path(self, path: Union[str, Path]) -> Optional[RepoState]:
        def clean(path):
            return str(Path(path).expanduser()).strip().rstrip('/')
        for name, section in self._repos_config.items():
            if clean(path).endswith(clean(section.get('path', "")) or " "):
                repo = self._config_section_to_repo(name, section)
                if clean(repo.path) == clean(path):
                    return repo
        return None

    def _get_state_by_id(self, repo_id) -> Optional[RepoState]:
        for name, repo in self._repos_config.items():
            if repo.get("repo_id") == repo_id:
                return self._config_section_to_repo(name, repo)
        return None

    def get_all_repo_state(self):
        for name, section in self._repos_config.items():
            if name != "DEFAULT":
                yield self._config_section_to_repo(name, section)

    def get_all_repo_names(self):
        for name, section in self._repos_config.items():
            if name != "DEFAULT":
                yield name
