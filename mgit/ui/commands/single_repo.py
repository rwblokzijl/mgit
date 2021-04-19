from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.cli_utils import query_yes_no

import argparse
from pathlib import Path
import json
import os

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
        parser.add_argument("-d", "--no-default", help="Do not add any default remotes", action='store_true')
        parser.add_argument("--name", help="Name of the project", type=str)
        parser.add_argument("--path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("--remotes", help="Name of remote repo", metavar="REMOTE[:REPO]", nargs="+", type=lambda x: self.remote_repo(x))
        parser.add_argument("--origin", help="Name of remote to be default push", metavar="REMOTE", type=lambda x: self.remote_repo(x))

    def run_command(self, args):
        was_abs = Path(args["path"]).is_absolute()
        path = Path(args["path"]).absolute()
        abspath = path
        if args["name"] is None:
            args["name"] = path.name

        if not was_abs:
            args["path"] = str(path).replace(str(Path.home()), "~")

        parent = self.interactor.resolve_best_parent(path)

        if parent:
            args["parent"] = parent.name
            print(path)
            print(self.interactor.abspath(parent.path))
            args["path"] = str(path.relative_to(self.interactor.abspath(parent.path)))

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
            args["abspath"] = str(abspath)
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

class CommandSingleRepoRename(AbstractLeafCommand):
    command = "rename"
    help="Rename a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Old name of the project", type=str)
        parser.add_argument("new_name", help="New name of the project", type=str)

    def run_command(self, args):
        return self.interactor.repo_rename(**args)

class CommandSingleRepoShow(AbstractLeafCommand):
    command = "show"
    help="Show a tracked repo state"

    def build(self, parser):
        self.repo_or_all(parser)

    def run_command(self, args):
        repo = args["repo"]
        if args["name"]:
            config_state, system_state = self.general_state_interactor.get_both_from_name(repo)
        elif args["path"]:
            config_state, system_state = self.general_state_interactor.get_both_from_path(repo)
        elif args["all"]:
            return dict(zip(["installed", "conficting", "missing"], self.general_state_interactor.combine_all()))
        else: #infer
            repo = repo or "."
            config_state = self.config_state_interactor.get_state(name=repo)
            if not config_state:
                config_state, system_state = self.general_state_interactor.get_both_from_path(repo)
            else:
                config_state, system_state = self.general_state_interactor.get_both_from_name(repo)
        combined = config_state + system_state
        if combined:
            return combined
        return config_state, system_state


class CommandSingleRepoCheck(AbstractLeafCommand):
    command = "check"
    help="Compares a repo config state to the repo state on the system"

    def build(self, parser):
        self.repo_or_all(parser)

    def run_command(self, args):
        repo = args["repo"]
        if args["name"]:
            return self.general_state_interactor.compare_on_name(repo)
        if args["path"]:
            return self.general_state_interactor.compare_on_path(repo)
        if args["all"]:
            return self.general_state_interactor.compare_all()
        repo = repo or "."
        config_state = self.config_state_interactor.get_state(name=repo)
        if not config_state:
            return self.general_state_interactor.compare_on_path(repo)
        else:
            return self.general_state_interactor.compare_on_name(repo)

class CommandSingleRepoUpdate(AbstractLeafCommand):
    command = "update"
    help="Updates the config based on the system or vice versa"

    def build(self, parser):
        self.repo(parser)

    def run_command(self, args):
        repo = args["repo"]
        if args["name"]:
            return self.general_state_interactor.compare_on_name(repo)
        if args["path"]:
            return self.general_state_interactor.compare_on_path(repo)
        repo = repo or "."
        config_state = self.config_state_interactor.get_state(name=repo)
        if not config_state:
            return self.general_state_interactor.compare_on_path(repo)
        else:
            return self.general_state_interactor.compare_on_name(repo)
