from mgit.local.state import *
from typing     import *

from pathlib import Path

import configparser
import os
import dataclasses

class Config:
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

    def get_state(self, repo_state: RepoState=None,
            repo_id: Optional[str]=None,
            name: Optional[str]=None,
            path: Union[Path, str, None]=None,) -> RepoState:
        if repo_state:
            repo_id = repo_state.repo_id
            name = repo_state.name
            path = repo_state.path
        if repo_id:
            ans = self._get_state_by_id(repo_id)
            if ans:
                return ans
        if name:
            ans = self._get_state_by_name(name)
            if ans:
                return ans
        if path:
            ans = self._get_state_by_path(Path(path))
            if ans:
                return ans
        raise self.ConfigError(f"No tracked repo found for: {repo_id} {name} {path})")

    def remove_state(self, repo_state: RepoState):
        old_state = self.get_state(repo_state)
        if old_state is None:
            return
        del(self._repos_config[old_state.name])
        self._write_configs(True, False)

    def set_state(self, repo_state: RepoState) -> Optional[RepoState]:
        """
        Updates an existing config with the values in the config
        """
        if not repo_state.name:
            raise ValueError("Repo_state must have a name")
        repo_keys = list(dataclasses.asdict(repo_state).keys())
        if repo_state.name in self._repos_config:
            del self._repos_config[repo_state.name]
        self._repos_config.add_section(repo_state.name)
        repo_keys.remove("source")
        repo_keys.remove("name")
        section = self._repos_config[repo_state.name]

        # self._write_repo_id(section, repo_id, force)
        if repo_state.repo_id is not None:
            section["repo_id"] = repo_state.repo_id
        repo_keys.remove("repo_id")

        if repo_state.path is not None:
            if not repo_state.path.is_absolute:
                raise ValueError(f"Path {repo_state.path} for {repo_state.name} is not valid")
            if repo_state.parent:
                if repo_state.parent.path is not None:
                    section["path"] = str(repo_state.path.relative_to(repo_state.parent.path)).strip("/")
            else:
                section["path"] = str(repo_state.path)
        repo_keys.remove("path")

        for remote_repo in repo_state.remotes:
            written_remotes: Dict[str, Remote]={}
            if isinstance(remote_repo, NamedRemoteRepo):
                # remote_repo: NamedRemoteRepo = remote_repo
                key = remote_repo.remote.name + '-repo'
                value = remote_repo.project_name
                if remote_repo.remote.name in written_remotes:
                    if written_remotes[remote_repo.remote.name] != remote_repo.remote:
                        raise ValueError(f"Repo to save specifies 2 non-equal remotes with the same name: {written_remotes[remote_repo.remote.name]} and {remote_repo.remote}")
                written_remotes[remote_repo.remote.name] = remote_repo.remote
                self.set_remote(remote_repo.remote, write=False) # dont write until rest of function succeeds
            elif isinstance(remote_repo, UnnamedRemoteRepo):
                # remote_repo: UnnamedRemoteRepo = remote_repo
                key = remote_repo.remote_name + '-remote'
                value = remote_repo.get_url()
            else:
                raise NotImplementedError("Unknown remote type")
            section[key] = value
        repo_keys.remove("remotes")

        # auto_commands = None, #TODO
        repo_keys.remove("auto_commands")

        if repo_state.categories is not None:
            section["categories"] = " ".join(sorted(list(repo_state.categories)))
        repo_keys.remove("categories")

        if repo_state.parent is not None:
            section["parent"] = repo_state.parent.name
        repo_keys.remove("parent")

        if repo_state.archived == True:
            section["archived"] = "1"
        repo_keys.remove("archived")

        assert not repo_keys, repo_keys
        self._write_configs()
        return repo_state

    def resolve_unnamed_remote(self, unnamed_remote: UnnamedRemoteRepo, ignore_name=True) -> RemoteRepo:
        for remote in self.get_all_remotes_from_config():
            if not ignore_name and remote.name != unnamed_remote.remote_name:
                continue
            sub_path: Optional[str] = remote.get_subpath(unnamed_remote)
            if sub_path:
                return NamedRemoteRepo(remote=remote, project_name=sub_path)
        return unnamed_remote

    def get_remote(self, name: str) -> Remote:
        if name in self._remotes_config:
            return self._config_section_to_remote(name, self._remotes_config[name])
        raise self.ConfigError("No remote named 'name' in config")

    def get_default_remotes(self) -> List[Remote]:
        if "defaults" not in self._remotes_config:
            return []

        return [remote for name, is_default in self._remotes_config["defaults"].items() if is_default and (remote := self.get_remote(name))]

    def set_remote(self, remote: Remote, write=True):
        if remote.name in self._remotes_config:
            del(self._remotes_config[remote.name])
        self._remotes_config.add_section(remote.name)
        section = self._remotes_config[remote.name]

        section["name"] = remote.name
        section["url"] = remote.url
        section["path"] = remote.path
        section["type"] = self._inverse_remote_type_map[remote.type]

        if write:
            self._write_configs(False, True)

    def remove_remote(self, remote: Remote):
        if remote.name not in self._remotes_config:
            return None
        del(self._remotes_config[remote.name])
        self._write_configs(False, True)

    def _is_special_section(self, name):
        if name.lower() == "defaults":
            return True
        if name == "DEFAULT":
            return True
        return False

    def get_all_remotes_from_config(self) -> Iterator[Remote]:
        for name, section in self._remotes_config.items():
            if not self._is_special_section(name):
                yield self._config_section_to_remote(name, section)

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
                "local" : RemoteType.LOCAL,
                }
        self._inverse_remote_type_map = {v: k for k, v in self._remote_type_map.items()}

    def _read_configs(self):
        repos = configparser.ConfigParser()
        if not repos.read(self._repos_file):
            raise FileNotFoundError(f"Failed to open {self._repos_file}")

        remotes = configparser.ConfigParser()
        if not remotes.read(self._remotes_file):
            raise FileNotFoundError(f"Failed to open {self._remotes_file}")

        return remotes, repos

    def _write_configs(self, repos=True, remotes=True):
        if repos:
            with open(self._repos_file, 'w') as configfile:
                self._repos_config.write(configfile)
        if remotes:
            with open(self._remotes_file, 'w') as configfile:
                self._remotes_config.write(configfile)

    def _get_parent(self, name: str, section: configparser.SectionProxy):
        parent_name = section.get("parent")

        if not parent_name:
            return None
        if parent_name not in self._repos_config:
            raise ReferenceError(f"Listed parent {parent_name} for {name} doesn't exist")

        parent_section = self._repos_config[parent_name]
        return self._config_section_to_repo(parent_name, parent_section)

    def _config_section_to_remote(self, name: str, section: configparser.SectionProxy) -> Remote:
        return Remote(
                name=name,
                url=section.get("url", ""),
                path=section.get("path"),
                type=self._remote_type_map.get(section.get("type"))
                )

    def _get_remote_repo(self, repo_name: str, remote_name: str):
        remote = self.get_remote(remote_name)
        if not remote:
            raise ReferenceError(f"Listed remote {remote_name} for {repo_name} doesn't exist")
        return NamedRemoteRepo(remote, repo_name)

    def _get_remotes(self, name: str, section: configparser.SectionProxy):
        remotes = set()
        for key in section:
            if key.endswith("-repo"):
                name        = section.get(key)
                remote_name = key[:-5]
                remote_repo = self._get_remote_repo(name, remote_name)
                remotes.add(remote_repo)
        return remotes

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
                repo_id=section.get("repo_id") or None,
                path=Path(path) or None,
                remotes=remotes,
                name=name,
                # origin=self._get_origin(remotes, name, section),
                auto_commands=None, #TODO
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
            if not self._is_special_section(name):
                ans = self._config_section_to_repo(name, section)
                if not ans:
                    continue
                yield ans

    def get_all_repo_names(self):
        for name in self._repos_config.keys():
            if not self._is_special_section(name):
                yield name

    class ConfigError(Exception):
        pass

