from mgit.ui.commands.category._category import CommandCategory
from mgit.ui.base_commands                import SingleRepoCommand

@CommandCategory.register
class CommandCategoryAdd(SingleRepoCommand):
    command = "add"
    help="Add category to project"

    config_required = True
    system_required = False

    def build(self, parser):
        parser.add_argument("categories", help="List of categories to show", default=[], nargs="*", type=str)

    def run(self, repo_state, categories):
        repo_state.categories.update(categories)
        self.config.set_state(repo_state)
        return repo_state

