from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.commands.category    import CommandCategory
from mgit.ui.commands.single_repo import *
from mgit.ui.commands.multi_repo  import *

from mgit.ui.commands.remote import CommandRemote

import argparse

class MgitCommand(AbstractNodeCommand):
    command = "mgit"
    def get_sub_commands(self):
        return [
                CommandCategory(self.interactor),
                CommandRemote(self.interactor),

                CommandSingleRepoInit(self.interactor),

                CommandMultiRepoList(self.interactor),
                CommandMultiRepoStatus(self.interactor),
                CommandMultiRepoDirty(self.interactor),
                ]

    def run(self, args):
        parser = argparse.ArgumentParser()
        self.build(parser)
        pargs = parser.parse_args(args)
        return self.run_command(dict(vars(pargs)))
