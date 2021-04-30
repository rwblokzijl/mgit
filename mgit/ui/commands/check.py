from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandSingleRepoCheck(AbstractLeafCommand):
    command = "check"
    help="Compares a repo config state to the repo state on the system"

    def build(self, parser):
        self.repo_by_path_name_or_infer_or_all(parser)

    def compare_all(self):
        ans = []
        for config_state in self.config_state_interactor.get_all_repo_state():
            system_state = self.system_state_interactor.get_state(path=config_state.path)
            if system_state:
                ans += system_state.compare(config_state)
        return ans

    def run(self, **args):
        if args["all"]:
            return self.compare_all()
        repo = args["repo"]
        if args["name"]:
            config_state, system_state = self.general_state_interactor.get_both_from_name(repo)
        if args["path"]:
            config_state, system_state = self.general_state_interactor.get_both_from_path(repo)
        repo = repo or "."
        config_state, system_state = self.general_state_interactor.get_both_from_name_or_path(repo)

        return config_state.compare(system_state)

