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
        parser.add_argument("path", help="Name of remote repo", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("-i",   "--installed", help="Include installed repos", default=False, action="store_true")
        parser.add_argument("-m",   "--missing",   help="Include missing repos",   default=False, action="store_true")
        parser.add_argument("-a",   "--archived",  help="Include archived repos",  default=False, action="store_true")
        parser.add_argument("-u",   "--untracked", help="Include untracked repos", default=False, action="store_true")
        parser.add_argument("-c",   "--conflict",  help="Include untracked repos", default=False, action="store_true")
        parser.add_argument("-g",   "--ignored",   help="Include ignored repos",   default=False, action="store_true")

    def run_command(self, args):
        flags = dict(args)
        del(flags["path"])
        if not any(flags.values()):
            args["installed"] = True
            args["missing"] = True
            args["conflict"] = True
        return self.interactor.repos_list_repos(**args)

class CommandMultiRepoFetch(AbstractLeafCommand):
    command = "fetch"
    help="Fetch multiple repos"

    def build(self, parser):
        parser.add_argument("path", help="Recursively fetch in path only", metavar="DIR", nargs="?", const=".", default=None, type=str)
        parser.add_argument("-r", "--remotes", metavar=["REMOTE"], nargs="*", help="List of repos to fetch from", default=None, type=str)

    def run_command(self, args):
        # print(args)
        return self.interactor.fetch_all_repos(**args)

class CommandMultiRepoStatus(AbstractLeafCommand):
    command = "status"
    help="Show the git status for all "

    def build(self, parser):
        parser.add_argument(        "name",        help="Name of the project", nargs="*", type=str)
        parser.add_argument("-l",   "--local",     help="Path to recursively explore", metavar="DIR", nargs="?", const=".", type=str)

        parser.add_argument("-u",   "--untracked", help="List directories with untracked files as dirty", default=False, action="store_true")
        parser.add_argument("-m",   "--missing",   help="Include missing repos", default=False, action="store_true")
        parser.add_argument("-r",   "--recursive", help="Include subrepos", default=False, action="store_true")

        parser.add_argument("-d",   "--dirty",     help="Only show dirty repos", action='store_true')
        parser.add_argument("-p",   "--remotes",   help="Include unpushed/pulled in dirty", default=False, action="store_true")

    def run_command(self, args):
        return self.interactor.repos_status(**args)


class CommandMultiRepoDirty(AbstractLeafCommand):
    command = "dirty"
    help="Succeeds if any repo is dirty"

    def build(self, parser):
        parser.add_argument(        "name",        help="Name of the project", nargs="*", type=str)
        parser.add_argument("-l",   "--local",     help="Path to recursively explore", metavar="DIR", nargs="?", const=".", type=str)
        parser.add_argument("-u",   "--untracked", help="List directories with untracked files as dirty", default=False, action="store_true")
        parser.add_argument("-p",   "--remotes",   help="Include unpushed/pulled in dirty", default=False, action="store_true")

    def run_command(self, args):
        return self.interactor.repos_dirty(**args)

