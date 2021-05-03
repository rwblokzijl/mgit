from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands.remote._remote import CommandRemote

@CommandRemote.register
class CommandRemoteAdd(AbstractLeafCommand):
    command = "add"
    help="Add remotes to repo"

    def build(self, parser):
        self.repo_by_path_name_or_infer(parser)
        parser.add_argument("remotes", help="Name of remotes", metavar="REMOTE", nargs="*", type=str)

    def get_repo_state(self, name, path, repo):
        if name:
            config_state, system_state = self.state_helper.get_both_from_name(repo)
        elif path:
            config_state, system_state = self.state_helper.get_both_from_path(repo)
        else: #infer
            config_state, system_state = self.state_helper.get_both_from_name_or_path(repo)
        return config_state + system_state

    def run(self, name, path, repo, remotes):
        repo_state = self.get_repo_state(name, path, repo)
        remotes = [self.state_helper.get_remote_from_config_or_raise(remote_name) for remote_name in remotes]
        return self.interactor.remotes_add(**args)

