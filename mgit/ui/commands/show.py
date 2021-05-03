from mgit.ui.parse_groups import MgitLeafCommand, ArgRepoStateOrAll
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandSingleRepoShow(MgitLeafCommand):
    command = "show"
    help="Show a tracked repo state"

    def build(self, parser):
        self.add_parse_group(ArgRepoStateOrAll(
            parser=parser,
            state_helper=self.state_helper,
            combine=False,
            raise_if_missing=False
            ))
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)

    def show_all(self, verbosity):
        installed, conflicting, missing = self.state_helper.combine_all()
        installed   = {r.represent(verbosity=verbosity) for r in installed}
        conflicting = {r.represent(verbosity=verbosity) for c in conflicting for r in c}
        missing     = {r.represent(verbosity=verbosity) for r in missing}
        return {k:v for k, v in zip(["installed", "conficting", "missing"], (installed, conflicting, missing)) if v}

    def run(self, config_state, system_state, verbose, all):
        if all:
            return self.show_all(verbose)

        if not (config_state and system_state): #not both
            repo_state = config_state or system_state
            return repo_state.represent(verbosity=verbose+1)

        conflicts = config_state.compare(system_state)
        if conflicts:
            return conflicts

        repo_state = config_state + system_state
        return repo_state.represent(verbosity=verbose+1)

