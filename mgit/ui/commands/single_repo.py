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
        parser.add_argument("-d", "--no-default", help="Do not add any default remtes", action='store_true')
        parser.add_argument("--name", help="Name of the project", type=str)
        parser.add_argument("--path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("--remotes", help="Name of remote repo", metavar="REMOTE[:REPO]", nargs="+", type=lambda x: self.remote_repo(x))
        parser.add_argument("--origin", help="Name of remote to be default push", metavar="REMOTE", type=lambda x: self.remote_repo(x))

    def run_command(self, args):
        args["path"] = os.path.abspath(os.path.expanduser(args["path"]))
        if args["name"] is None:
            args["name"] = os.path.basename(args["path"])

        if args["no_default"]:
            defaults = []
        else:
            defaults = [(remote.name, None) for remote in self.interactor.get_default_remotes()]
        del(args["no_default"])

        args["remotes"] = dict(args["remotes"] or defaults)

        if args["origin"]:
            args["remotes"][args["origin"][0]] = args["origin"][1] or args["name"]
            args["origin"] = args["origin"][0]
        else:
            del(args["origin"])

        args["remotes"] = { k:v or args["name"] for k,v in args["remotes"].items() }

        if args.pop('y') or self.interactor.test_mode or query_yes_no("Do you want to init with the following values:" + json.dumps(args, indent = 1)):
            return self.interactor.repo_init(**args)
        else:
            print("Doing nothing")

