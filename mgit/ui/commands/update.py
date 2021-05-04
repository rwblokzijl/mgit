from mgit.ui.parse_groups import SingleRepoCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandUpdate(SingleRepoCommand):
    command = "update"
    help="Updates the config based on the system or vice versa"

    def build(self, parser):
        parser.add_argument("-c", "--config", help="Update the config based on the system", action="store_true")
        parser.add_argument("-s", "--system", help="Update the system based on the config", action="store_true")

    def run(self, repo_state, config, system):
        if config and system:
            self.config.set_state(repo_state)
            self.system.set_state(repo_state)
        elif system:
            self.system.set_state(repo_state)
        elif config:
            self.config.set_state(repo_state)
        return repo_state

