from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandFetch(AbstractLeafCommand):
    command = "fetch"
    help="Fetch multiple repos"

    def build(self, parser):
        parser.add_argument("path", help="Recursively fetch in path only", metavar="DIR", nargs="?", const=".", default=None, type=str)
        parser.add_argument("-r", "--remotes", metavar=["REMOTE"], nargs="*", help="List of repos to fetch from", default=None, type=str)

    def run(self, **args):
        raise NotImplementedError()
