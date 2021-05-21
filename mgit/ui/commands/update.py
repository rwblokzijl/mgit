from mgit.ui.base_commands import SingleRepoCommand
from mgit.ui.commands._mgit import MgitCommand

from mgit.local.state import *

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

    @classmethod
    def merge_vals(cls, config: Optional[T], system: Optional[T]) -> Optional[T]:
        if config is None or system is None:
            # One is missing
            if config is None:
                return system
            return config

        # Both exist
        if config != system:
            raise ValueError(f"{config} != {system}")
        return config

    @classmethod
    def merge(cls, config_state: RepoState, system_state: RepoState):
        return RepoState(
                source        = "",
                name          = cls.merge_vals(config_state.name, system_state.name),
                repo_id       = cls.merge_vals(config_state.repo_id, system_state.repo_id),
                path          = cls.merge_vals(config_state.path, system_state.path),
                parent        = None,#cls.merge(config_state.parent, system_state.parent),
                remotes       = set(),#cls.merge_remotes()
                auto_commands = None, #
                archived      = None, #
                categories    = None #
                )

    def run(self, config_state, system_state, config, system):
        repo_state = self.merge(config_state, system_state)
        return repo_state
        # if config and system:
        #     self.config.set_state(repo_state)
        #     self.system.set_state(repo_state)
        # elif system:
        #     self.system.set_state(repo_state)
        # elif config:
        #     self.config.set_state(repo_state)
        # return repo_state

