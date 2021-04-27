from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.state.remote_interactor import RemoteInteractor

from mgit.ui.cli_utils import query_yes_no

import argparse
import os
import json


class CommandRemote(AbstractNodeCommand):
    command = "remote"
    help="Commands concerning the remotes"
    def get_sub_commands(self):
        return [
                CommandRemoteList,
                CommandRemoteAdd,
                CommandRemoteCheck,
                ]

class CommandRemoteList(AbstractLeafCommand):
    command = "list"
    help="List repos for remotes"

    def build(self, parser):
        parser.add_argument("remotes", help="Name of remote repo", metavar="REMOTE", nargs="*", type=str)

    def run_command(self, args):
        if args['remotes']:
            remotes = [self.general_state_interactor.get_remote_from_config_or_raise(remote_name) for remote_name in args['remotes']]
        else:
            remotes = self.config_state_interactor.get_all_remotes_from_config()

        return {remote.name:self.remote_interactor.list_remote(remote) for remote in remotes}

class CommandRemoteAdd(AbstractLeafCommand):
    command = "add"
    help="Add remotes to repo"

    def build(self, parser):
        self.repo_by_path_name_or_infer(parser)
        parser.add_argument("remotes", help="Name of remotes", metavar="REMOTE", nargs="*", type=str)

    def run_command(self, args):
        repo = args["repo"]
        if args["name"]:
            self.general_state_interactor.get_config_from_name_or_raise(name)
        if args["path"]:
            self.general_state_interactor.get_config_from_path_or_raise(name)
        repo = repo or "."
        remotes = [self.general_state_interactor.get_remote_from_config_or_raise(remote_name) for remote_name in args['remotes']]
        return self.interactor.remotes_add(**args)

class CommandRemoteCheck(AbstractLeafCommand):
    command = "check"
    help="Check repos in remotes"

    def build(self, parser):
        parser.add_argument("remote", help="Name of remote repo", metavar="REMOTE", type=str)

    def run_command(self, args):
        remote = self.config_state_interactor.get_remote(args["remote"])
        return RemoteInteractor().get_remote_repo_id_mappings(remote)

