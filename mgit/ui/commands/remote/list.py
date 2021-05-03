from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands.remote._remote import CommandRemote

from mgit.ui.cli_utils import query_yes_no

@CommandRemote.register
class CommandRemoteList(AbstractLeafCommand):
    command = "list"
    help="List repos for remotes"

    def build(self, parser):
        parser.add_argument("remotes", help="Name of remote repo", metavar="REMOTE", nargs="*", type=str)

    def run(self, **args):
        if args['remotes']:
            remotes = [self.general_state_interactor.get_remote_from_config_or_raise(remote_name) for remote_name in args['remotes']]
        else:
            remotes = self.config.get_all_remotes_from_config()

        return {remote.name:self.remote_system.list_remote(remote) for remote in remotes}

