from mgit.ui.cli                        import AbstractLeafCommand
from mgit.ui.commands.category._category import CommandCategory

from collections import OrderedDict

@CommandCategory.register
class CommandCategoryAdd(AbstractLeafCommand):
    command = "add"
    help="Add category to project"

    def build(self, parser):
        parser.add_argument("project", help="Name of the project", type=str)
        parser.add_argument("categories", help="List of categories to show", nargs="*", type=str)

    def run(self, project, categories=[]):
        config_state = self.general_state_interactor.get_config_from_name_or_raise(project)
        config_state.categories.update(categories)
        self.config_state_interactor.set_state(config_state)
        return config_state

