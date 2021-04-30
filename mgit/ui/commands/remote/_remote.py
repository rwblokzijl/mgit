from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandRemote(AbstractNodeCommand):
    command = "remote"
    help="Commands concerning the remotes"

