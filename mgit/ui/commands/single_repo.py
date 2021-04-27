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
        """ Prepares the details to init a repo """
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
        config_state = self.general_state_interactor.get_config_from_name_or_raise(args["name"])
        config_state.source = ""
        if args.pop('y') or self.interactor.test_mode or query_yes_no(f"Do you want to install the following repo: \n{config_state.represent()}"):
            return self.system_state_interactor.set_state(config_state)
        else:
            return "Doing nothing"

class CommandSingleRepoRename(AbstractLeafCommand):
    command = "rename"
    help="Rename a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Old name of the project", type=str)
        parser.add_argument("new_name", help="New name of the project", type=str)

    def run_command(self, args):
        name     = args["name"]
        new_name = args["new_name"]

        new_state = self.config_state_interactor.get_state(name=new_name)
        if new_state:
            raise NameError(f"Repo {new_name} already exists")

        config_state = self.config_state_interactor.get_state(name=name)
        if not config_state:
            raise NameError(f"No repo named {name}")

        self.config_state_interactor.remove_state(config_state)
        config_state.name = new_name
        self.config_state_interactor.set_state(config_state)
        return config_state

class CommandSingleRepoShow(AbstractLeafCommand):
    command = "show"
    help="Show a tracked repo state"

    def build(self, parser):
        self.repo_by_path_name_or_infer_or_all(parser)
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)

    def show_all(self, verbosity):
        installed, conflicting, missing = self.general_state_interactor.combine_all()
        installed   = {r.represent(verbosity=verbosity) for r in installed}
        conflicting = {r.represent(verbosity=verbosity) for r in conflicting}
        missing     = {r.represent(verbosity=verbosity) for r in missing}
        return {k:v for k, v in zip(["installed", "conficting", "missing"], (installed, conflicting, missing)) if v}

    def run_command(self, args):
        repo = args["repo"]
        if args["all"]:
            return self.show_all(args['verbose'])

        if args["name"]:
            config_state, system_state = self.general_state_interactor.get_both_from_name(repo)
        elif args["path"]:
            config_state, system_state = self.general_state_interactor.get_both_from_path(repo)
        else: #infer
            config_state, system_state = self.general_state_interactor.get_both_from_name_or_path(repo)

        combined = config_state + system_state
        if combined:
            return combined
        return config_state, system_state

class CommandSingleRepoCheck(AbstractLeafCommand):
    command = "check"
    help="Compares a repo config state to the repo state on the system"

    def build(self, parser):
        self.repo_by_path_name_or_infer_or_all(parser)

    def compare_all(self):
        ans = []
        for config_state in self.config_state_interactor.get_all_repo_state():
            system_state = self.system_state_interactor.get_state(path=config_state.path)
            if system_state:
                ans += system_state.compare(config_state)
        return ans

    def run_command(self, args):
        if args["all"]:
            return self.compare_all()
        repo = args["repo"]
        if args["name"]:
            config_state, system_state = self.general_state_interactor.get_both_from_name(repo)
        if args["path"]:
            config_state, system_state = self.general_state_interactor.get_both_from_path(repo)
        repo = repo or "."
        config_state, system_state = self.general_state_interactor.get_both_from_name_or_path(repo)

        return config_state.compare(system_state)

class CommandSingleRepoUpdate(AbstractLeafCommand):
    command = "update"
    help="Updates the config based on the system or vice versa"

    def build(self, parser):
        self.repo_by_path_name_or_infer(parser)

    def run_command(self, args):
        repo = args["repo"]
        if args["name"]:
            config_state, system_state = self.general_state_interactor.get_both_from_name(repo)
        if args["path"]:
            config_state, system_state = self.general_state_interactor.get_both_from_path(repo)
        repo = repo or "."
        config_state, system_state = self.general_state_interactor.get_both_from_name_or_path(repo)

        state = config_state + system_state

        self.config_state_interactor.set_state(state)
        self.system_state_interactor.set_state(state)
        return state
