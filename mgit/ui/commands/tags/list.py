from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands.tags._tags import CommandTags

from mgit.local.state import *
from typing import *

from collections import OrderedDict

@CommandTags.register
class CommandCategoryList(AbstractLeafCommand):
    command = "list"
    help="List known tags"

    def build(self, parser):
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)
        parser.add_argument("tags", help="List of tags to show", default=[], nargs="*", type=str)

    def get_all_by_category(self) -> Dict[str, List[RepoState]]:
        ans: Dict[str, List[RepoState]] = {}
        repo_states = self.config.get_all_repo_state()
        for repo_state in repo_states:
            for tag in repo_state.tags or set():
                if tag not in ans:
                    ans[tag] = list()
                ans[tag].append(repo_state)
        return ans

    def run(self, tags, verbose=0):
        by_category = self.get_all_by_category()
        if tags:
            by_category = {cat:l for cat, l in by_category.items() if cat in tags}
        if verbose == 0:
            return sorted(by_category.keys())
        represented = {c:[r.represent(verbosity=min(verbose-1, 2)) for r in l] for c, l in by_category.items()}
        return OrderedDict(sorted(represented.items()))

