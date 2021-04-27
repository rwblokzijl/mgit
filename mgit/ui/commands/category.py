from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

from collections import OrderedDict

class CommandCategory(AbstractNodeCommand):
    command = "category"
    help="Manage categories"
    def get_sub_commands(self):
        return [
                CommandCategoryList,
                CommandCategoryAdd,
                CommandCategoryRemove,
                ]

class CommandCategoryList(AbstractLeafCommand):
    command = "list"
    help="List known categories"

    def build(self, parser):
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)
        parser.add_argument("categories", help="List of categories to show", nargs="*", type=str)

    def run_command(self, args):
        by_category = self.general_state_interactor.get_all_by_category()
        if args['categories']:
            by_category = {cat:l for cat, l in by_category.items() if cat in args['categories']}
        if args['verbose'] == 0:
            return sorted(by_category.keys())
        represented = {c:[r.represent(verbosity=min(args['verbose']-1, 2)) for r in l] for c, l in by_category.items()}
        return OrderedDict(sorted(represented.items()))

class CommandCategoryAdd(AbstractLeafCommand):
    command = "add"

    def build(self, parser):
        parser.add_argument("project", help="Name of the project", type=str)
        parser.add_argument("categories", help="List of categories to show", nargs="*", type=str)

    def run_command(self, args):
        config_state = self.general_state_interactor.get_config_from_name_or_raise(args['project'])
        config_state.categories.update(args['categories'])
        self.config_state_interactor.set_state(config_state)
        return config_state

class CommandCategoryRemove(AbstractLeafCommand):
    command = "remove"

    def build(self, parser):
        parser.add_argument("project", help="Name of the project", type=str)
        parser.add_argument("categories", help="List of categories to show", nargs="*", type=str)

    def run_command(self, args):
        config_state = self.general_state_interactor.get_config_from_name_or_raise(args['project'])
        config_state.categories.difference(args['categories'])
        self.config_state_interactor.set_state(config_state)
        return config_state


