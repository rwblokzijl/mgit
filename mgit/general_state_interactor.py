from mgit.state import Conflict, RepoState

from typing import List, Optional, Tuple, Dict

class GeneralStateInteractor:

    def __init__(self, config_state_interactor, system_state_interactor, local_system_interactor, remote_interactor):
        self.config_state_interactor = config_state_interactor
        self.system_state_interactor = system_state_interactor
        self.local_system_interactor = local_system_interactor
        self.remote_interactor       = remote_interactor

    def get_both_from_name_or_path(self, name_or_path):
        config_state = self.config_state_interactor.get_state(name=name_or_path)
        if not config_state:
            system_state = self.system_state_interactor.get_state(path=name_or_path)
            if not system_state:
                raise ValueError(f"'{name_or_path}' is not a tracked repo nor an existing path")
            config_state = self.get_config_from_system(system_state)
            return config_state, system_state
        system_state = self.get_system_from_config(config_state)
        return config_state, system_state

    def get_system_from_config(self, config_state) -> RepoState:
        if not config_state.path:
            raise ValueError(f"'{config_state.name}'' doesn't specify a path")
        system_state = self.system_state_interactor.get_state(path=config_state.path)
        if not system_state:
            raise ValueError(f"Local repo '{config_state.name}' does not exist in '{config_state.path}'")
        return system_state

    def get_config_from_system(self, system_state) -> RepoState:
        config_state = None
        if system_state.repo_id:
            config_state = self.config_state_interactor.get_state(repo_id=system_state.repo_id)
        if not config_state:
            config_state = self.config_state_interactor.get_state(path=system_state.path)
        if not config_state:
            raise ValueError(f"Repo in '{system_state.path}', cannot be found in config")
        return config_state

    def get_both_from_path(self, path) -> Tuple[RepoState, RepoState]:
        system_state = self.system_state_interactor.get_state(path=path)
        if not system_state:
            raise ValueError(f"No repo found in {path}")
        config_state = self.get_config_from_system(system_state)
        return config_state, system_state

    def get_both_from_name(self, name) -> Tuple[RepoState, RepoState]:
        config_state = self.get_config_from_name_or_raise(name)
        system_state= self.get_system_from_config(config_state)
        return config_state, system_state

    def get_config_from_name_or_raise(self, name) -> RepoState:
        config_state = self.config_state_interactor.get_state(name=name)
        if not config_state:
            raise ValueError(f"'{name}' is not known as a tracked repo")
        return config_state

    def get_remote_from_config_or_raise(self, name) -> RepoState:
        remote = self.config_state_interactor.get_remote(name=name)
        if not remote:
            raise ValueError(f"'{name}' is not known as a tracked remote")
        return remote

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

    def get_all_installed(self) -> List[RepoState]:
        installed, _, _ = self.combine_all()
        return installed

    def get_all_by_category(self) -> Dict[str, List[RepoState]]:
        ans: Dict[str, List[RepoState]] = {}
        repo_states = self.config_state_interactor.get_all_repo_state()
        for repo_state in repo_states:
            for category in repo_state.categories or set():
                if category not in ans:
                    ans[category] = list()
                ans[category].append(repo_state)
        return ans


