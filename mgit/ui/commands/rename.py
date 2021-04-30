from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandSingleRepoRename(AbstractLeafCommand):
    command = "rename"
    help="Rename a tracked repo"

    def build(self, parser):
        parser.add_argument("name", help="Old name of the project", type=str)
        parser.add_argument("new_name", help="New name of the project", type=str)

    def run(self, **args):
        name     = args["name"]
        new_name = args["new_name"]

        new_state = self.config_state_interactor.get_state(name=new_name)
        if new_state:
            raise NameError(f"Repo {new_name} already exists")

        config_state = self.config_state_interactor.get_state(name=name)
        if not config_state:
            raise NameError(f"No repo named {name}")

        self.config_state_interactor.remove_state(config_state)
        config_state.name = new_name
        self.config_state_interactor.set_state(config_state)
        return config_state

