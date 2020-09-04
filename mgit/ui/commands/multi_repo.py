from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.cli_utils import query_yes_no

import argparse
import os
import json

class CommandMultiRepoList(AbstractLeafCommand):
    command = "list"
    help="Create a new local/remote repo pair"

    def build(self, parser):
        parser.add_argument("remotes", help="Name of remote repo", metavar="REMOTE", nargs="*", type=str)

    def run_command(self, args):
        return self.interactor.repos_list_repos(**args)

