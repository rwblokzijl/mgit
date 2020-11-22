from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.cli_utils import query_yes_no

import argparse
import os
import json

"""
"automatic git functions" - stored: auto-[remote]-[branch] = [commit] [push] [pull] [fetch]

auto | show | name [function] [branch] | show configured info

auto | add | commit | name branch         | auto-commit-[branch] = 1
auto | add/set | push   | name branch remotes | auto-push-[branch] = [REMOTE]..
auto | add/set | fetch  | name branch remotes | auto-fetch-[branch] = [[REMOTE]..]

auto | set | pull   | name branch remote  | auto-pull-[branch] = REMOTE

auto | remove | commit | name branch         | auto-commit-[branch] = 0
auto | remove | push   | name branch remotes | auto-push-[branch] = [REMOTE]..
auto | remove | fetch  | name branch remotes | auto-fetch-[branch] = [[REMOTE]..]
auto | remove | pull   | name branch remote  | auto-pull-[branch] = REMOTE

auto | commit | name branch         | commit branches with auto commit configured (warn when wrong branch is checked out)
auto | push   | name branch remotes | push branches with auto push configured
auto | fetch  | name branch remotes | fetch branches with auto fetch configured
auto | pull   | name branch remote  | pull branches with auto pull configured
"""

def function_options_type(option):
    options = ["commit", "push", "fetch", "pull"]
    if option not in options:
        raise argparse.ArgumentTypeError(f"'{option}' is not a recognised command valid options are: {', '.join(options)}")
    else:
        return option

class CommandAuto(AbstractNodeCommand):
    command = "auto"
    help="Commands concerning the automatic commit, push, fetch, and pull"
    def get_sub_commands(self):
        return [
                CommandAutoAdd(self.interactor),
                CommandAutoSet(self.interactor),
                CommandAutoRemove(self.interactor),
                CommandAutoShow(self.interactor),
                ]

class CommandAutoAdd(AbstractNodeCommand):
    command = "add"
    help="Add auto function to repos"

    def get_sub_commands(self):
        return [
                CommandAutoAddPush(self.interactor),
                CommandAutoAddFetch(self.interactor),
                ]

class CommandAutoSet(AbstractNodeCommand):
    command = "add"
    help="Set auto function for repos"

    def get_sub_commands(self):
        return [
                CommandAutoSetCommit(self.interactor),
                CommandAutoSetPush(self.interactor),
                CommandAutoSetFetch(self.interactor),
                CommandAutoSetPull(self.interactor),
                ]

class CommandAutoRemove(AbstractNodeCommand):
    command = "remove"
    help="Remove auto function from repos"

    def get_sub_commands(self):
        return [
                CommandAutoRemoveCommit(self.interactor),
                CommandAutoRemovePush(self.interactor),
                CommandAutoRemoveFetch(self.interactor),
                CommandAutoRemovePull(self.interactor),
                ]

"show"
class CommandAutoShow(AbstractLeafCommand):
    command = "show"
    help="Show auto functions for repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)
        parser.add_argument("functions", help="Name of the branch", nargs="*", type=function_options_type)
        # parser.add_argument("-b", "--branch", help="Name of the branch", type=str)
        # parser.add_argument("-f", "--functions", help="Name of the branch", nargs="*", type=function_options_type)

    def run_command(self, args):
        return self.interactor.auto_show(**args)

"add"
"auto | add | push   | name branch remotes | auto-push-[branch] = [REMOTE].."
class CommandAutoAddPush(AbstractLeafCommand):
    command = "push"
    help="Add auto push remotes to a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)
        parser.add_argument("remotes", help="Remotes to auto push to", metavar="REMOTE", nargs="+", type=str)

    def run_command(self, args):
        return self.interactor.auto_add_push(**args)

"auto | add | fetch  | name branch remotes | auto-fetch-[branch] = [[REMOTE]..]"
class CommandAutoAddFetch(AbstractLeafCommand):
    command = "fetch"
    help="Add auto fetch remotes to a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)
        parser.add_argument("remotes", help="Remotes to auto fetch from", metavar="REMOTE", nargs="+", type=str)

    def run_command(self, args):
        return self.interactor.auto_add_fetch(**args)

"set"
"auto | set | commit | name branch         | auto-commit-[branch] = 1"
class CommandAutoSetCommit(AbstractLeafCommand):
    command = "commit"
    help="Set auto commit function for repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)

    def run_command(self, args):
        return self.interactor.auto_set_commit(**args)

"auto | set | push   | name branch remotes | auto-push-[branch] = [REMOTE].."
class CommandAutoSetPush(AbstractLeafCommand):
    command = "push"
    help="Set auto push remotes for a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)
        parser.add_argument("remotes", help="Remotes to auto push to", metavar="REMOTE", nargs="+", type=str)

    def run_command(self, args):
        return self.interactor.auto_set_push(**args)

"auto | set | fetch  | name branch remotes | auto-fetch-[branch] = [[REMOTE]..]"
class CommandAutoSetFetch(AbstractLeafCommand):
    command = "fetch"
    help="Add auto fetch remotes for a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)
        parser.add_argument("remotes", help="Remotes to auto fetch from", metavar="REMOTE", nargs="+", type=str)

    def run_command(self, args):
        return self.interactor.auto_set_fetch(**args)

"auto | set | pull   | name branch remote  | auto-pull-[branch] = REMOTE"
class CommandAutoSetPull(AbstractLeafCommand):
    command = "pull"
    help="Set auto pull remote for a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)
        parser.add_argument("remote", help="Remote to auto pull from", metavar="REMOTE", type=str)

    def run_command(self, args):
        return self.interactor.auto_set_pull(**args)

"remove"
"auto | remove | commit | name branch         | auto-commit-[branch] = 0"
class CommandAutoRemoveCommit(AbstractLeafCommand):
    command = "commit"
    help="Remove auto commit function from repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)

    def run_command(self, args):
        return self.interactor.auto_remove_commit(**args)

"auto | remove | push   | name branch remotes | auto-push-[branch] = [REMOTE].."
class CommandAutoRemovePush(AbstractLeafCommand):
    command = "push"
    help="Remove auto push remotes from a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)
        parser.add_argument("remotes", help="Remotes to auto push to", metavar="REMOTE", nargs="+", type=str)

    def run_command(self, args):
        return self.interactor.auto_remove_push(**args)

"auto | remove | fetch  | name branch remotes | auto-fetch-[branch] = [[REMOTE]..]"
class CommandAutoRemoveFetch(AbstractLeafCommand):
    command = "fetch"
    help="Remove auto fetch remotes from a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)
        parser.add_argument("remotes", help="List of remotes", metavar="REMOTE", nargs="+", type=str)

    def run_command(self, args):
        return self.interactor.auto_remove_fetch(**args)

"auto | remove | pull   | name branch remote  | auto-pull-[branch] = REMOTE"
class CommandAutoRemovePull(AbstractLeafCommand):
    command = "pull"
    help="Remove auto pull remote from a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Name of a tracked repo", type=str)
        parser.add_argument("branch", help="Name of the branch", type=str)

    def run_command(self, args):
        return self.interactor.auto_remove_pull(**args)

"git commands"
"auto | commit | name branch         | commit branches with auto commit configured (warn when wrong branch is checked out)"
class CommandAutoCommit(AbstractLeafCommand):
    command = "commit"
    help="Auto commit all configured repos"

    def run_command(self, args):
        print(args)
        # return self.interactor.auto_commit(**args)

"auto | push   | name branch remotes | push branches with auto push configured"
class CommandAutoPush(AbstractLeafCommand):
    command = "push"
    help="Auto push all configured repos"

    def run_command(self, args):
        print(args)
        # return self.interactor.auto_push(**args)

"auto | fetch  | name branch remotes | fetch branches with auto fetch configured"
class CommandAutoFetch(AbstractLeafCommand):
    command = "fetch"
    help="Auto fetch all configured repos"

    def run_command(self, args):
        print(args)
        # return self.interactor.auto_fetch(**args)

"auto | pull   | name branch remote  | pull branches with auto pull configured"
class CommandAutoPull(AbstractLeafCommand):
    command = "pull"
    help="Auto pull all configured repos"

    def run_command(self, args):
        print(args)
        # return self.interactor.auto_pull(**args)

