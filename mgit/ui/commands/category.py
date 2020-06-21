from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

class CommandCategory(AbstractNodeCommand):
    command = "category"
    def get_sub_commands(self):
        return [
                CommandCategoryList(),
                CommandCategoryShow()
                ]

class CommandCategoryList(AbstractLeafCommand):
    command = "list"
    def build(self, parser):
        pass
        # parser.add_argument("-p", "--path", help="Path to local repo(s)", metavar="DIR", type=str)
        # parser.add_argument("-n", "--name", help="Name of repo to fix", type=str)

    def run_command(self, args):
        return self.command

class CommandCategoryShow(AbstractLeafCommand):
    command = "show"

    def build(self, parser):
        pass
        # parser.add_argument("-p", "--path", help="Path to local repo(s)", metavar="DIR", type=str)
        # parser.add_argument("-n", "--name", help="Name of repo to fix", type=str)

    def run_command(self, args):
        return self.command

