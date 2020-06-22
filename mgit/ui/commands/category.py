from mgit.ui.cli import AbstractNodeCommand
from mgit.ui.cli import AbstractLeafCommand

class CommandCategory(AbstractNodeCommand):
    command = "category"
    help="Manage categories"
    def get_sub_commands(self):
        return [
                CommandCategoryList(self.interactor),
                CommandCategoryShow(self.interactor),
                CommandCategoryAdd(self.interactor),
                CommandCategoryRemove(self.interactor)
                ]

class CommandCategoryList(AbstractLeafCommand):
    command = "list"
    help="List known categories"

    def build(self, parser):
        pass

    def run_command(self, args):
        return self.interactor.categories_list(**args)

class CommandCategoryShow(AbstractLeafCommand):
    command = "show"

    def build(self, parser):
        parser.add_argument("categories", help="List of categories to show", nargs="*", type=str)

    def run_command(self, args):
        return self.interactor.categories_show(**args)

class CommandCategoryAdd(AbstractLeafCommand):
    command = "add"

    def build(self, parser):
        parser.add_argument("project", help="Name of the project", type=str)
        parser.add_argument("category", help="Name of the category", type=str)

    def run_command(self, args):
        return self.interactor.categories_add(**args)

class CommandCategoryRemove(AbstractLeafCommand):
    command = "remove"

    def build(self, parser):
        parser.add_argument("project", help="Name of the project", type=str)
        parser.add_argument("category", help="Name of the category", type=str)

    def run_command(self, args):
        return self.interactor.categories_remove(**args)


