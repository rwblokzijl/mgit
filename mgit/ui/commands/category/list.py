from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands.category._category import CommandCategory

from collections import OrderedDict

@CommandCategory.register
class CommandCategoryList(AbstractLeafCommand):
    command = "list"
    help="List known categories"

    def build(self, parser):
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)
        parser.add_argument("categories", help="List of categories to show", nargs="*", type=str)

    def run(self, categories=[], verbose=0):
        by_category = self.state_helper.get_all_by_category()
        if categories:
            by_category = {cat:l for cat, l in by_category.items() if cat in categories}
        if verbose == 0:
            return sorted(by_category.keys())
        represented = {c:[r.represent(verbosity=min(verbose-1, 2)) for r in l] for c, l in by_category.items()}
        return OrderedDict(sorted(represented.items()))

