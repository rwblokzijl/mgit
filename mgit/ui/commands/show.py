from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandSingleRepoShow(AbstractLeafCommand):
    command = "show"
    help="Show a tracked repo state"

    def build(self, parser):
        self.repo_by_path_name_or_infer_or_all(parser)
        parser.add_argument('-v', '--verbose', help="Verbose", action='count', default=0)

    def show_all(self, verbosity):
        installed, conflicting, missing = self.general_state_interactor.combine_all()
        installed   = {r.represent(verbosity=verbosity) for r in installed}
        conflicting = {r.represent(verbosity=verbosity) for r in conflicting}
        missing     = {r.represent(verbosity=verbosity) for r in missing}
        return {k:v for k, v in zip(["installed", "conficting", "missing"], (installed, conflicting, missing)) if v}

    def run(self, **args):
        repo = args["repo"]
        if args["all"]:
            return self.show_all(args['verbose'])

        if args["name"]:
            config_state, system_state = self.general_state_interactor.get_both_from_name(repo)
        elif args["path"]:
            config_state, system_state = self.general_state_interactor.get_both_from_path(repo)
        else: #infer
            config_state, system_state = self.general_state_interactor.get_both_from_name_or_path(repo)

        combined = config_state + system_state
        if combined:
            return combined
        return config_state, system_state

