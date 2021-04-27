from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from mgit.ui.cli_utils import query_yes_no

import argparse
import os
import json

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
        # parser.add_argument("-m",   "--missing",   help="Include missing repos", default=False, action="store_true")
        parser.add_argument("-r",   "--recursive", help="Include subrepos", default=False, action="store_true")

        parser.add_argument("-d",   "--dirty",     help="Only show dirty repos", action='store_true')
        parser.add_argument("-p",   "--remotes",   help="Include unpushed/pulled in dirty", default=False, action="store_true")

        parser.add_argument("-c",   "--count",   help="Only return the amount of output", default=False, action="store_true")

    def run_command(self, args):
        # ignore_paths = ['~/.vim', '~/.local', '~/.oh-my-zsh', '~/.cargo', '~/.cache', '~/.config/vim'] # TODO: get from config
        # TODO: Missing???
        if args['name']:
            repo_states = [self.general_state_interactor.get_config_from_name_or_raise(name=name) for name in args['name']]
            all_status = self.local_system_interactor.get_status_for_repos(repo_states)
            all_status = sorted(all_status, key=lambda x: x.repo_state.name)
        elif args['local']:
            repo_states = self.system_state_interactor.get_all_local_repos_in_path(args['local'])
            all_status = [status for status in self.local_system_interactor.get_status_for_repos(repo_states) if status or not args['dirty']]
            all_status = sorted(all_status, key=lambda x: x.repo_state.path)

        # filter down the results
        if args['dirty']: #dirty only
            all_status = [s for s in all_status if s] #remove all "clean"
        all_status = [s for s in all_status if (
            s.dirty or # always include dirty
            (s.untracked_files and args['untracked']) or # untracked only counts if flag is set
            (s.branch_status and args['remotes'])) ] # unpushed/merged only counts if flag is set
        if args['count']: # return count only
            return len(all_status)
        else:
            return all_status
