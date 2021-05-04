from mgit.ui.parse_groups import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.state.state import *

from typing import *

@MgitCommand.register
class CommandSingleRepoShow(MultiRepoCommand):
    command = "show"
    help="Show a tracked repo state"

    combine         = False
    config_required = False
    system_required = False

    def build(self, parser):
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)

    def combine_all(self) -> Tuple[List[RepoState], List[Tuple[RepoState, RepoState]], List[RepoState]]:
        installed: List[RepoState]                     = []
        conflicting: List[Tuple[RepoState, RepoState]] = []
        missing: List[RepoState]                       = []
        for config_state in sorted(self.config.get_all_repo_state()):
            system_state = self.system.get_state(path=config_state.path)
            if system_state:
                combined = system_state + config_state
                if combined:
                    installed.append(combined)
                else:
                    conflicting.append((config_state, system_state))
            else:
                missing.append(config_state)
        return installed, conflicting, missing

    def show_all(self, repo_states=None, verbosity=1):
        installed, conflicting, missing = self.combine_all()
        installed   = {r.represent(verbosity=verbosity) for r in installed}
        conflicting = {r.represent(verbosity=verbosity) for c in conflicting for r in c}
        missing     = {r.represent(verbosity=verbosity) for r in missing}
        return {k:v for k, v in zip(["installed", "conficting", "missing"], (installed, conflicting, missing)) if v}

    def run(self, repo_states, verbose, all):
        if all:
            return self.show_all(verbosity=verbose)

        ans = []
        for config_state, system_state in repo_states:
            if config_state and system_state: #both
                repo_state = config_state + system_state
                if repo_state:
                    ans.append(repo_state.represent(verbosity=verbose+1))
            else:
                repo_state = config_state or system_state
                ans.append(repo_state.represent(verbosity=verbose+1))
        return ans

