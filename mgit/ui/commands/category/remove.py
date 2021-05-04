from mgit.ui.commands.category._category import CommandCategory
from mgit.ui.parse_groups                import SingleRepoCommand

@CommandCategory.register
class CommandCategoryRemove(SingleRepoCommand):
    command = "remove"
    help="Remove category from project"

    config_required = True
    system_required = False

    def build(self, parser):
        parser.add_argument("categories", help="List of categories to remove", default=[], nargs="*", type=str)

    def run(self, repo_state, categories):
        repo_state.categories -= set(categories)
        self.config.set_state(repo_state)
        return repo_state


