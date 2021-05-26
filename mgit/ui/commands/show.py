from mgit.ui.base_commands import MultiRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.local.state import *

from typing import *

@MgitCommand.register
class CommandShow(MultiRepoCommand):
    command = "show"
    help="Show a tracked repo state"

    combine         = False
    system_required = False

    def build(self, parser):
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)

    def _combine_all(self, repo_states) -> Tuple[List[RepoState], List[Tuple[RepoState, RepoState]], List[RepoState]]:
        installed: List[RepoState]                     = []
        conflicting: List[Tuple[RepoState, RepoState]] = []
        missing: List[RepoState]                       = []
        for config_state, system_state in repo_states:
            if system_state:
                try:
                    combined = system_state + config_state
                    installed.append(combined)
                except RepoState.StateConflict:
                    conflicting.append((config_state, system_state))
            else:
                missing.append(config_state)
        return installed, conflicting, missing

    def _show_all(self, repo_states=None, verbosity=1):
        installed, conflicting, missing = self._combine_all(repo_states)
        installed   = {r.represent(verbosity=verbosity) for r in installed}
        conflicting = {r.represent(verbosity=verbosity) for c in conflicting for r in c}
        missing     = {r.represent(verbosity=verbosity) for r in missing}
        return {k:v for k, v in zip(["installed", "conficting", "missing"], (installed, conflicting, missing)) if v}

    def run(self, repo_states, verbose):
        return self._show_all(repo_states, verbosity=verbose)

