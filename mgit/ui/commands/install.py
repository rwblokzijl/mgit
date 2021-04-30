from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

from mgit.ui.cli_utils import query_yes_no

from pathlib import Path
import json

@MgitCommand.register
class CommandSingleRepoInstall(AbstractLeafCommand):
    command = "install"
    help="Install a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of the project", type=str)
        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')
        parser.add_argument("--remote", help="Name of remote to install repo from", metavar="REMOTE", type=str) # TODO: install from this remote

    def install_repo(self, state):
        return self.system_state_interactor.set_state(state)

    def run(self, name, y, remote):
        config_state = self.general_state_interactor.get_config_from_name_or_raise(name)
        config_state.source = ""
        if y or query_yes_no(f"Do you want to install the following repo: \n{config_state.represent()}"):
            self.install_repo(config_state)
            return "Installed"
        else:
            return "Doing nothing"

