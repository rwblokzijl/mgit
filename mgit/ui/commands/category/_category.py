from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandCategory(AbstractNodeCommand):
    command = "category"
    help="Manage categories"
