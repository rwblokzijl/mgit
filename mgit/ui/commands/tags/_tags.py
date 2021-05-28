from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandTags(AbstractNodeCommand):
    command = "tags"
    help="Manage tags"
