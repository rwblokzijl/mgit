from mgit.ui.base_commands  import SingleRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.ui.cli_utils      import query_yes_no

from mgit.util.merging import StateMerger

from mgit.local.state import *

from pathlib import Path

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

    def run(self, config_state, system_state, config, system, y):
        state_merger = StateMerger(self.config)
        if not (config or system): # if none then both
            config = True
            system = True
        repo_state = state_merger.merge(config_state, system_state)
        if config:
            print(f"old config={config_state.represent()}")
        if system:
            print(f"old system={system_state.represent()}")
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

