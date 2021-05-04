from mgit.ui.commands._mgit import MgitCommand
from mgit.ui.base_commands                import SingleRepoCommand

from mgit.ui.cli_utils import query_yes_no

@MgitCommand.register
class CommandSingleRepoInstall(SingleRepoCommand):
    command = "install"
    help="Install a tracked repo"

    config_required = True
    system_required = False

    def build(self, parser):
        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')
        parser.add_argument("--remote", help="Name of remote to install repo from", metavar="REMOTE", type=str)

    def install_repo(self, state, remote):
        return self.system.set_state(state, remote=remote)

    def find_remote_in_repo_state(self, remote_name, repo_state):
        for remote_repo in repo_state.remotes:
            if remote_repo.remote.name == remote_name:
                return remote_repo
        return None

    def run(self, repo_state, y, remote):
        target_remote = self.find_remote_in_repo_state(remote, repo_state)

        if not y and not query_yes_no(
                "Do you want to install the following repo: \n" +
                f"{repo_state.represent()}"):
            return "Doing nothing"

        self.install_repo(repo_state, target_remote)

