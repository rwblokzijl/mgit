from mgit.ui.base_commands import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandCheck(MultiRepoCommand):
    command = "check"
    help="Compares a repo config state to the repo state on the system"

    combine=False

    def build(self, parser):
        pass

    def run(self, repo_states):
        return [config_state.compare(system_state) for config_state, system_state in repo_states]

