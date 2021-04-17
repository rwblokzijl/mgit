from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.commands.category    import CommandCategory
from mgit.ui.commands.remote import CommandRemote
from mgit.ui.commands.auto import CommandAuto

from mgit.ui.commands.single_repo import *
from mgit.ui.commands.multi_repo  import *

import argparse

class MgitCommand(AbstractNodeCommand):
    command = "mgit"
    def get_sub_commands(self):
        return [
                CommandCategory,
                CommandRemote,
                CommandAuto,

                CommandSingleRepoInit,
                CommandSingleRepoInstall,
                CommandSingleRepoRename,
                CommandSingleRepoShow,
                CommandSingleRepoCheck,

                CommandMultiRepoList,
                CommandMultiRepoStatus,
                CommandMultiRepoDirty,
                CommandMultiRepoFetch,
                ]

    def run(self, args):
        parser = argparse.ArgumentParser()
        self.build(parser)
        pargs = parser.parse_args(args)
        return self.run_command(dict(vars(pargs)))
