from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands.remote._remote import CommandRemote

@CommandRemote.register
class CommandRemoteAdd(AbstractLeafCommand):
    command = "add"
    help="Add remotes to repo"

    def build(self, parser):
        self.repo_by_path_name_or_infer(parser)
        parser.add_argument("remotes", help="Name of remotes", metavar="REMOTE", nargs="*", type=str)

    def run(self, **args):
        repo = args["repo"]
        if args["name"]:
            self.general_state_interactor.get_config_from_name_or_raise(name)
        if args["path"]:
            self.general_state_interactor.get_config_from_path_or_raise(name)
        repo = repo or "."
        remotes = [self.general_state_interactor.get_remote_from_config_or_raise(remote_name) for remote_name in args['remotes']]
        return self.interactor.remotes_add(**args)

