from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands.remote._remote import CommandRemote

@CommandRemote.register
class CommandRemoteList(AbstractLeafCommand):
    command = "list"
    help="List repos for remotes"

    def build(self, parser):
        parser.add_argument("remotes", help="Name of remote repo", metavar="REMOTE", nargs="*", type=str)

    def run(self, remotes):
        if remotes:
            remotes = [self.config.get_remote(r) for r in remotes]
        else:
            remotes = self.config.get_all_remotes_from_config()

        return {remote.name:self.remote_system.list_remote(remote) for remote in remotes}

