from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.cli_utils import query_yes_no

import argparse
import os
import json

class CommandSingleRepoInit(AbstractLeafCommand):
    command = "init"
    help="Create a new local/remote repo pair"

    def remote_repo(self, s):
        if ":" in s:
            return s.split(":", 1)
        else:
            return s, None

    def build(self, parser):
        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')
        parser.add_argument("--name", help="Name of the project", type=str)
        parser.add_argument("--path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("--remotes", help="Name of remote repo", metavar="REMOTE[:REPO]", nargs="+", type=lambda x: self.remote_repo(x))

    def run_command(self, args):
        args["path"] = os.path.abspath(os.path.expanduser(args["path"]))
        if args["name"] is None:
            args["name"] = os.path.basename(args["path"])
        args["remotes"] = dict(args["remotes"] or [])

        args["remotes"] = { k:v or args["name"] for k,v in args["remotes"].items() }

        if args.pop('y') or self.interactor.test_mode or query_yes_no("Do you want to init with the following values:" + json.dumps(args, indent = 1)):
            return self.interactor.repo_init(**args)
        else:
            print("Doing nothing")

