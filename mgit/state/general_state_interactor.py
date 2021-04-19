from mgit.state.state import Conflict, RepoState

from typing import List, Optional, Tuple

class GeneralStateInteractor:

    def __init__(self, config_state_interactor, system_state_interactor):
        self.config_state_interactor = config_state_interactor
        self.system_state_interactor = system_state_interactor

    def get_both_from_path(self, path) -> Tuple[RepoState, RepoState]:
        system_state = self.system_state_interactor.get_state(path=path)
        if not system_state:
            raise ValueError(f"No repo found in {path}")
        config_state = None
        if system_state.repo_id:
            config_state = self.config_state_interactor.get_state(repo_id=system_state.repo_id)
        if not config_state:
            config_state = self.config_state_interactor.get_state(path=system_state.path)
            if not config_state:
                raise ValueError(f"Repo in '{path}', cannot be found in config")
        return config_state, system_state

    def get_both_from_name(self, name) -> Tuple[RepoState, RepoState]:
        config_state = self.config_state_interactor.get_state(name=name)
        if not config_state:
            raise ValueError(f"'{name}' is not knows as a tracked repo")
        if not config_state.path:
            raise ValueError(f"'{name}'' doesn't specify a path")
        system_state = self.system_state_interactor.get_state(path=config_state.path)
        if not system_state:
            raise ValueError(f"Local repo '{name}' does not exist in '{config_state.path}'")
        return config_state, system_state

    def compare_on_name(self, name) -> List[Conflict]:
        config_state, system_state = self.get_both_from_name(name)
        return system_state.compare(config_state)

    def compare_on_path(self, path) -> List[Conflict]:
        config_state, system_state = self.get_both_from_path(path)
        return system_state.compare(config_state)

    def combine_on_name(self, name):
        config_state, system_state = self.get_both_from_name(name)
        return system_state + config_state

    def combine_on_path(self, path):
        config_state, system_state = self.get_both_from_path(path)
        return (system_state + config_state)

    def compare_all(self) -> List[Conflict]:
        ans: List[Conflict] = []
        for config_state in self.config_state_interactor.get_all_repo_state():
            system_state = self.system_state_interactor.get_state(path=config_state.path)
            if system_state:
                ans += system_state.compare(config_state)
        return ans

    def combine_all(self) -> Tuple[List[RepoState], List[Tuple[RepoState, RepoState]], List[RepoState]]:
        installed: List[RepoState]                     = []
        conflicting: List[Tuple[RepoState, RepoState]] = []
        missing: List[RepoState]                       = []
        for config_state in sorted(self.config_state_interactor.get_all_repo_state()):
            system_state = self.system_state_interactor.get_state(path=config_state.path)
            if system_state:
                combined = system_state + config_state
                if combined:
                    installed.append(combined)
                else:
                    conflicting.append((config_state, system_state))
            else:
                missing.append(config_state)
        return installed, conflicting, missing

