from mgit.ui.base_commands import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.local.state import *

from git import Repo

from typing import *

@MgitCommand.register
class CommandFetch(MultiRepoCommand):
    command = "fetch"
    help="Fetch for repos from remotes"

    def build(self, parser):
        pass

    def run(self, repo_states: List[RepoState]):
        for repo_state in repo_states:
            repo = Repo(repo_state.path)
            print(f"Fetching {repo_state.name}")
            for remote in repo.remotes:
                remote.fetch()

