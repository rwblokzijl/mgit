from mgit.ui.base_commands import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.local.state import *
from mgit.util.git_actions import merge

from pygit2 import Repository
import pygit2

from typing import *

@MgitCommand.register
class CommandPull(MultiRepoCommand):
    command = "merge"
    help="Merge remote branches into repo"

    def build(self, parser):
        pass

    def run(self, repo_states: List[RepoState]):
        for repo_state in repo_states:
            repo = Repository(repo_state.path.expanduser().absolute())
            print(f"Merging {repo_state.name}")
            merge(repo)

