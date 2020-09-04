from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.cli_utils import query_yes_no

import argparse
import os
import json

class CommandMultiRepoList(AbstractLeafCommand):
    command = "list"
    help="List repos for remotes"

    def build(self, parser):
        parser.add_argument("remotes", help="Name of remote repo", metavar="REMOTE", nargs="*", type=str)

    def run_command(self, args):
        return self.interactor.repos_list_repos(**args)

class CommandMultiRepoStatus(AbstractLeafCommand):
    command = "status"
    help="Show the git status for all "

    def build(self, parser):
        parser.add_argument("path", help="Path to recursively explore", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("-n", "--name", help="Name of the project", nargs="+", type=str)
        parser.add_argument("-d", "--dirty", help="Only show dirty repos", action='store_true')

    def run_command(self, args):
        return self.interactor.repos_status(**args)

