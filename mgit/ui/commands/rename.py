from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandRename(AbstractLeafCommand):
    command = "rename"
    help="Rename a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Old name of the project", type=str)
        parser.add_argument("new_name", help="New name of the project", type=str)

    def run(self, name, new_name):

        try:
            self.config.get_state(name=new_name)
            raise NameError(f"Repo {new_name} already exists")
        except self.config.ConfigError:
            pass

        config_state = self.config.get_state(name=name)

        self.config.remove_state(config_state)
        config_state.name = new_name
        self.config.set_state(config_state)
        return config_state

