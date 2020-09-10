from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.cli_utils import query_yes_no

import argparse
import os
import json


class CommandRemote(AbstractNodeCommand):
    command = "remote"
    help="Commands concerning the remotes"
    def get_sub_commands(self):
        return [
                CommandRemoteList(self.interactor),
                ]

class CommandRemoteList(AbstractLeafCommand):
    command = "list"
    help="List repos for remotes"

    def build(self, parser):
        parser.add_argument("remotes", help="Name of remote repo", metavar="REMOTE", nargs="*", type=str)

    def run_command(self, args):
        return self.interactor.remotes_list_repos(**args)

