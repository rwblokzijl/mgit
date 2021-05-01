from mgit.ui.cli_utils import MgitLeafCommand, ArgRepoStateOrAll
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandSingleRepoShow(MgitLeafCommand):
    command = "show"
    help="Show a tracked repo state"

    def build(self, parser):
        self.add_parse_group(ArgRepoStateOrAll(parser, general_state_interactor=self.general_state_interactor))
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)

    def show_all(self, verbosity):
        installed, conflicting, missing = self.general_state_interactor.combine_all()
        installed   = {r.represent(verbosity=verbosity) for r in installed}
        conflicting = {r.represent(verbosity=verbosity) for r in conflicting}
        missing     = {r.represent(verbosity=verbosity) for r in missing}
        return {k:v for k, v in zip(["installed", "conficting", "missing"], (installed, conflicting, missing)) if v}

    def run(self, repo_state, verbose, all):
        if all:
            return self.show_all(verbose)

        if repo_state:
            return repo_state.represent(verbosity=verbose+1)

