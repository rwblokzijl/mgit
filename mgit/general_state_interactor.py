from mgit.state import Conflict, RepoState

from pathlib import Path

from typing import List, Optional, Tuple, Dict

class GeneralStateInteractor:

    def __init__(self, config, system, local_system, remote_system):
        self.config = config
        self.system = system
        self.local_system = local_system
        self.remote_system       = remote_system

    def get_both_from_name_or_path(self, name_or_path, raise_if_missing):
        config_state = self.config.get_state(name=name_or_path)
        if not config_state:
            system_state = self.system.get_state(path=name_or_path or Path("."))
            if not system_state:
                return self._raise_or_none(f"'{name_or_path}' is not a tracked repo nor an existing path", raise_if_missing)
            config_state = self._get_config_from_system(system_state, raise_if_missing)
            return config_state, system_state
        system_state = self._get_system_from_config(config_state, raise_if_missing)
        return config_state, system_state

    def get_both_from_path(self, path, raise_if_missing) -> Tuple[Optional[RepoState], Optional[RepoState]]:
        system_state = self.system.get_state(path=path)
        if not system_state:
            self._raise_or_none(f"No repo found in {path}", raise_if_missing)
        config_state = self._get_config_from_system(system_state, raise_if_missing)
        return config_state, system_state

    def get_both_from_name(self, name, raise_if_missing) -> Tuple[Optional[RepoState], Optional[RepoState]]:
        config_state = self.config.get_state(name=name)
        if not config_state:
            return self._raise_or_none(f"'{name}' is not known as a tracked repo", raise_if_missing)
        system_state= self._get_system_from_config(config_state, raise_if_missing)
        return config_state, system_state

    def combine_all(self) -> Tuple[List[RepoState], List[Tuple[RepoState, RepoState]], List[RepoState]]:
        installed: List[RepoState]                     = []
        conflicting: List[Tuple[RepoState, RepoState]] = []
        missing: List[RepoState]                       = []
        for config_state in sorted(self.config.get_all_repo_state()):
            system_state = self.system.get_state(path=config_state.path)
            if system_state:
                combined = system_state + config_state
                if combined:
                    installed.append(combined)
                else:
                    conflicting.append((config_state, system_state))
            else:
                missing.append(config_state)
        return installed, conflicting, missing

    def get_all_installed(self) -> List[RepoState]:
        installed, _, _ = self.combine_all()
        return installed

    def get_all_by_category(self) -> Dict[str, List[RepoState]]:
        ans: Dict[str, List[RepoState]] = {}
        repo_states = self.config.get_all_repo_state()
        for repo_state in repo_states:
            for category in repo_state.categories or set():
                if category not in ans:
                    ans[category] = list()
                ans[category].append(repo_state)
        return ans

    def get_config_from_name_or_raise(self, name) -> RepoState:
        config_state = self.config.get_state(name=name)
        if not config_state:
            raise ValueError(f"'{name}' is not known as a tracked repo")
        return config_state



    def _get_system_from_config(self, config_state, raise_if_missing) -> Optional[RepoState]:
        if not config_state.path:
            return self._raise_or_none(f"'{config_state.name}'' doesn't specify a path", raise_if_missing)
        system_state = self.system.get_state(path=config_state.path)
        if not system_state:
            self._raise_or_none(f"Local repo '{config_state.name}' does not exist in '{config_state.path}'",
                    raise_if_missing)
        return system_state

    def _get_config_from_system(self, system_state, raise_if_missing) -> RepoState:
        config_state = None
        if system_state.repo_id:
            config_state = self.config.get_state(repo_id=system_state.repo_id)
        if not config_state:
            config_state = self.config.get_state(path=system_state.path)
        if not config_state:
            return self._raise_or_none(f"Repo in '{system_state.path}', cannot be found in config", raise_if_missing)
        return config_state

    def _raise_or_none(self, message, should_raise):
        if should_raise:
            raise ValueError(message)
        return None

