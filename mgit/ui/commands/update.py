from mgit.ui.base_commands import SingleRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.ui.cli_utils      import query_yes_no

from mgit.local.state import *

from copy import deepcopy

from typing import *

T = TypeVar('T')

@MgitCommand.register
class CommandUpdate(SingleRepoCommand):
    command = "update"
    help="Updates the config based on the system or vice versa"

    combine = False

    def build(self, parser):
        parser.add_argument("-c", "--config", help="Update the config based on the system", action="store_true")
        parser.add_argument("-s", "--system", help="Update the system based on the config", action="store_true")

        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')

    def one_or_other(self, config, system):
        # One is missing
        if config is None:
            return system
        return config

    def merge_vals(self, config: Optional[T], system: Optional[T]) -> Optional[T]:
        if config is None or system is None:
            return self.one_or_other(config, system)
        # Both exist
        if config != system:
            raise ValueError(f"{config} != {system}")
        return config

    def merge_parents(self, config: Optional[RepoState], system: Optional[RepoState]):
        if config is None or system is None:
            return self.one_or_other(config, system)
        # Both exist
        return self.merge(config, system)

    def _merge_same_remotes(self, config: Set[RemoteRepo], system: Set[RemoteRepo]):
        result = set()
        for rr in list(config):
            if rr in system:
                print("s", rr)
                result.add(rr)
                config.remove(rr)
                system.remove(rr)
        return result

    def _merge_same_urls(self, config: Set[RemoteRepo], system: Set[RemoteRepo]):
        result = set()
        for con_r in list(config):
            for sys_r in list(system):
                if con_r.url == sys_r.url:
                    print("su", con_r)
                    print("su", sys_r)
                    result.add(con_r) # use the config url
                    config.remove(con_r)
                    system.remove(sys_r)
        return result

    def _merge_same_names(self, config: Set[RemoteRepo], system: Set[RemoteRepo]):
        result = set()
        for con_r in list(config):
            for sys_r in list(system):
                if con_r.name == sys_r.name:
                    print(f"WARNING: Two remotes with the same name: {sys_r}, {con_r}")
                    result.add(sys_r) # use the system url
                    config.remove(con_r)
                    system.remove(sys_r)
        return result

    def merge_remotes(self, config: Set[RemoteRepo], system: Set[RemoteRepo]):
        config = deepcopy(config)
        system = deepcopy(system)
        result: Set[RemoteRepo] = set()

        system = {self.config.resolve_remote(r) for r in system}

        result  = self._merge_same_remotes(config, system)
        result |= self._merge_same_urls(config, system)
        result |= self._merge_same_names(config, system)
        result |= config #leftovers
        result |= system #leftovers

        return result

    def merge(self, config_state: RepoState, system_state: RepoState):
        return RepoState(
                source        = "",
                name          = self.merge_vals(config_state.name, system_state.name),
                repo_id       = self.merge_vals(config_state.repo_id, system_state.repo_id),
                path          = self.merge_vals(config_state.path, system_state.path),
                parent        = self.merge_parents(config_state.parent, system_state.parent),
                remotes       = self.merge_remotes(config_state.remotes, system_state.remotes),
                auto_commands = None, # TODO
                archived      = self.merge_vals(config_state.archived, system_state.archived),
                categories    = (config_state.categories or set()) | (system_state.categories or set())
                )

    def run(self, config_state, system_state, config, system, y):
        repo_state = self.merge(config_state, system_state)
        if not y and not query_yes_no(
                "Do you want to update with the following values: \n" +
                f"name={repo_state.represent()}"):
            return "Doing nothing"

        if config and system:
            self.config.set_state(repo_state)
            self.system.set_state(repo_state)
        elif system:
            self.system.set_state(repo_state)
        elif config:
            self.config.set_state(repo_state)
        return repo_state

