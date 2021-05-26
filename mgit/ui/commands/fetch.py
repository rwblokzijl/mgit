from mgit.ui.base_commands import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.local.state import *

from typing import *

@MgitCommand.register
class CommandFetch(MultiRepoCommand):
    command = "fetch"
    help="Fetch for repos from remotes"

    def build(self, parser):
        pass

    def run(self, repo_states):
        for repo_state in repo_states:
            print(repo_state.name)
