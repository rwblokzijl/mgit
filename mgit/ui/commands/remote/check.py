from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands.remote._remote import CommandRemote

from mgit.state.remote_interactor import RemoteInteractor

@CommandRemote.register
class CommandRemoteCheck(AbstractLeafCommand):
    command = "check"
    help="Check repos in remotes"

    def build(self, parser):
        parser.add_argument("remote", help="Name of remote repo", metavar="REMOTE", type=str)

    def run(self, **args):
        remote = self.config_state_interactor.get_remote(args["remote"])
        return self.remote_interactor.get_remote_repo_id_mappings(remote)

