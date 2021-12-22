from mgit.ui.base_commands  import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.ui.cli_utils      import query_yes_no

from mgit.util.merging import StateMerger

from mgit.local.state import *

from pathlib import Path

from typing import *

T = TypeVar('T')

@MgitCommand.register
class CommandUpdate(MultiRepoCommand):
    command = "update"
    help="Updates the config based on the system or vice versa"

    combine = False

    def build(self, parser):
        parser.add_argument("-c", "--config", help="Update the config based on the system", action="store_true")
        parser.add_argument("-s", "--system", help="Update the system based on the config", action="store_true")

        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')

    def run(self, repo_states, config, system, y):
        for config_state, system_state in repo_states:
            if not config_state.compare(system_state):
                continue
            state_merger = StateMerger(self.config)
            if not (config or system): # if none then both
                config = True
                system = True
            repo_state = state_merger.merge(config_state, system_state)
            if not y:
                if config:
                    yield f"old config={config_state.represent()}"
                if system:
                    yield f"old system={system_state.represent()}"
                if not query_yes_no(
                        "Do you want to update with the following values: \n" +
                        f"name={repo_state.represent()}"):
                    return f"Doing nothing for {repo_state.name}"

            if config and system:
                self.config.set_state(repo_state)
                self.system.set_state(repo_state)
            elif system:
                self.system.set_state(repo_state)
            elif config:
                self.config.set_state(repo_state)
            yield repo_state

