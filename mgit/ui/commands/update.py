from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandSingleRepoUpdate(AbstractLeafCommand):
    command = "update"
    help="Updates the config based on the system or vice versa"

    def build(self, parser):
        self.repo_by_path_name_or_infer(parser)

    def run(self, **args):
        repo = args["repo"]
        if args["name"]:
            config_state, system_state = self.state_helper.get_both_from_name(repo)
        if args["path"]:
            config_state, system_state = self.state_helper.get_both_from_path(repo)
        repo = repo or "."
        config_state, system_state = self.state_helper.get_both_from_name_or_path(repo)

        state = config_state + system_state

        self.config.set_state(state)
        self.system.set_state(state)
        return state

