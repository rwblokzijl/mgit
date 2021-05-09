from mgit.ui.commands.remote._remote import CommandRemote
from mgit.ui.base_commands import SingleRepoCommand
from mgit.ui.parsers import RemoteParser

from mgit.local.state import *

@CommandRemote.register
class CommandRemoteAdd(SingleRepoCommand):
    command = "add"
    help="Add remotes to repo"

    # we add the remote seperately, ignoring previous conflicts
    combine=False

    def build(self, parser):
        parser.add_argument("remotes", help="Name of remotes", metavar="REMOTE", nargs="*", type=str)

    def _add_remote_repo(self, remote_repo: RemoteRepo, repo_state: RepoState):
        "Replaces remote_repo into repo_state.remotes"
        already_exists = {r for r in repo_state.remotes if r.get_name() == remote_repo.get_name()}
        repo_state.remotes -= already_exists
        repo_state.remotes.add(remote_repo)

    def run(self, config_state, system_state, remotes):
        remote_repos = RemoteParser(self.config).parse(remote_names=remotes, default_name=config_state.name)
        for remote_repo in remote_repos:
            try:
                self.remote_system.init_repo(remote_repo)
                self._add_remote_repo(remote_repo, config_state)
                self._add_remote_repo(remote_repo, system_state)
            except self.remote_system.RemoteError:
                pass

        self.config.set_state(config_state)
        self.system.set_state(system_state)
        return
