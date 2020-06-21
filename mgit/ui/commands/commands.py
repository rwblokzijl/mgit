from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.commands.category import CommandCategory

import argparse

class MgitCommand(AbstractNodeCommand):
    command = "mgit"
    def get_sub_commands(self):
        return [
                CommandCategory()
                ]

    def run(self, args):
        parser = argparse.ArgumentParser()
        self.build(parser)
        pargs = parser.parse_args(args)
        return self.run_command(dict(vars(pargs)))
