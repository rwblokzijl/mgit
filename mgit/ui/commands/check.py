from mgit.ui.parse_groups import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandCheck(MultiRepoCommand):
    command = "check"
    help="Compares a repo config state to the repo state on the system"

    combine=False

    def build(self, parser):
        pass

    def compare_all(self):
        ans = []
        for config_state in self.config.get_all_repo_state():
            system_state = self.system.get_state(path=config_state.path)
            if system_state:
                ans += system_state.compare(config_state)
        return ans

    def run(self, repo_states, all):
        if all:
            return self.compare_all()

        return [config_state.compare(system_state) for config_state, system_state in repo_states]

