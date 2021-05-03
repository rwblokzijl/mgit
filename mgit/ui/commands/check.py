from mgit.ui.parse_groups import MgitLeafCommand, ArgRepoStateOrAll
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandCheck(MgitLeafCommand):
    command = "check"
    help="Compares a repo config state to the repo state on the system"

    def build(self, parser):
        self.add_parse_group(ArgRepoStateOrAll(
            general_state_interactor=self.general_state_interactor,
            parser=parser,
            combine=False))

    def compare_all(self):
        ans = []
        for config_state in self.config.get_all_repo_state():
            system_state = self.system.get_state(path=config_state.path)
            if system_state:
                ans += system_state.compare(config_state)
        return ans

    def run(self, config_state, system_state, all):
        if all:
            return self.compare_all()

        return config_state.compare(system_state)

