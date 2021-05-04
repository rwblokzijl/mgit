from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands.category._category import CommandCategory

from mgit.state.state import *
from typing import *

from collections import OrderedDict

@CommandCategory.register
class CommandCategoryList(AbstractLeafCommand):
    command = "list"
    help="List known categories"

    def build(self, parser):
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)
        parser.add_argument("categories", help="List of categories to show", default=[], nargs="*", type=str)

    def get_all_by_category(self) -> Dict[str, List[RepoState]]:
        ans: Dict[str, List[RepoState]] = {}
        repo_states = self.config.get_all_repo_state()
        for repo_state in repo_states:
            for category in repo_state.categories or set():
                if category not in ans:
                    ans[category] = list()
                ans[category].append(repo_state)
        return ans

    def run(self, categories, verbose=0):
        by_category = self.get_all_by_category()
        if categories:
            by_category = {cat:l for cat, l in by_category.items() if cat in categories}
        if verbose == 0:
            return sorted(by_category.keys())
        represented = {c:[r.represent(verbosity=min(verbose-1, 2)) for r in l] for c, l in by_category.items()}
        return OrderedDict(sorted(represented.items()))

