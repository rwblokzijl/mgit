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
        parser.add_argument("--remote", help="Name of remote to install repo from", metavar="REMOTE", type=str)

    def install_repo(self, state, remote):
        return self.system_state_interactor.set_state(state, remote=remote)

    def find_remote_in_repo_state(self, remote_name, repo_state):
        for remote_repo in repo_state.remotes:
            if remote_repo.remote.name == remote_name:
                return remote_repo
        return None

    def run(self, name, y, remote):
        config_state = self.general_state_interactor.get_config_from_name_or_raise(name)

        target_remote = self.find_remote_in_repo_state(remote, config_state)

        if not y and not query_yes_no(f"Do you want to install the following repo: \n{config_state.represent()}"):
            return "Doing nothing"

        self.install_repo(config_state, target_remote)

