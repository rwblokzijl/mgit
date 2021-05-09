from mgit.ui.commands._mgit import MgitCommand
from mgit.ui.base_commands import SingleRepoCommand

@MgitCommand.register
class CommandArchive(SingleRepoCommand):
    command = "archive"
    help="Archive a tracked repo"

    config_required = True
    system_required = False

    def build(self, parser):
        pass

    def run(self, repo_state):
        repo_state.archived = True
        self.config.set_state(repo_state)
        return repo_state

