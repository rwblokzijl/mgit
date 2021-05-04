from mgit.ui.commands.remote._remote import CommandRemote
from mgit.ui.parse_groups import SingleRepoCommand

@CommandRemote.register
class CommandRemoteAdd(SingleRepoCommand):
    command = "add"
    help="Add remotes to repo"

    combine=False

    def build(self, parser):
        parser.add_argument("remotes", help="Name of remotes", metavar="REMOTE", nargs="*", type=str)

    def run(self, config_state, system_state, remotes):
        pass
        # print(config_state, system_state, remotes)
        # repo_state = self.get_repo_state(name, path, repo)
        # remotes = [self.state_helper.get_remote_from_config_or_raise(remote_name) for remote_name in remotes]
        # return self.interactor.remotes_add(**args)

