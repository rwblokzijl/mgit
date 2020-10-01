from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.cli_utils import query_yes_no

import argparse
from pathlib import Path
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
        was_abs = Path(args["path"]).is_absolute()
        path = Path(args["path"]).absolute()
        if args["name"] is None:
            args["name"] = path.name

        if not was_abs:
            args["path"] = str(path).replace(str(Path.home()), "~")

        args["remotes"] = dict(args["remotes"] or (
                [] if args["no_default"]
                else [(remote.name, None) for remote in self.interactor.get_default_remotes()]
                ))

        del(args["no_default"])

        if args["origin"]:
            if args["origin"][0] not in args["remotes"]:
                args["remotes"][args["origin"][0]] = args["origin"][1] or args["name"]
            else:
                assert (
                        not args["origin"][1] or
                        args["origin"][1] == args["remotes"][args["origin"][0]]
                        )
            args["origin"] = args["origin"][0]
        else:
            del(args["origin"])

        args["remotes"] = { k:v or args["name"] for k,v in args["remotes"].items() }

        if args.pop('y') or self.interactor.test_mode or query_yes_no("Do you want to init with the following values:" + json.dumps(args, indent = 1)):
            return self.interactor.repo_init(**args)
        else:
            return "Doing nothing"

class CommandSingleRepoInstall(AbstractLeafCommand):
    command = "install"
    help="Install a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of the project", type=str)
        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')
        parser.add_argument("--remote", help="Name of remote to install repo from", metavar="REMOTE", type=str)

    def run_command(self, args):
        repo_info = self.interactor.get_repo_install_info(args["name"], args["remote"])
        if args.pop('y') or self.interactor.test_mode or query_yes_no("Do you want to install a repo with following values:" + json.dumps(repo_info, indent = 1)):
            return self.interactor.repo_install(**args)
        else:
            return "Doing nothing"
