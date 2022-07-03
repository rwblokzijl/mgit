from mgit.ui.base_commands import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.local.state import *

from pygit2 import Repository
import pygit2

from typing import *

@MgitCommand.register
class CommandFetch(MultiRepoCommand):
    command = "fetch"
    help="Fetch for repos from remotes"

    def build(self, parser):
        pass

    def run(self, repo_states: List[RepoState]):
        for repo_state in repo_states:
            repo = Repository(repo_state.path.expanduser().absolute())
            print(f"Fetching {repo_state.name}")
            for remote in repo.remotes:
                username = remote.url.split('@')[0]
                remote.fetch(callbacks=pygit2.RemoteCallbacks(credentials=pygit2.KeypairFromAgent(username)))

