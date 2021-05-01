from mgit.ui.cli            import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

@MgitCommand.register
class CommandMultiRepoStatus(AbstractLeafCommand):
    command = "status"
    help="Show the git status for all "

    def build(self, parser):
        parser.add_argument(        "name",        help="Name of the project", nargs="*", type=str)
        parser.add_argument("-l",   "--local",     help="Path to recursively explore", metavar="DIR", nargs="?", const=".", type=str)

        parser.add_argument("-u",   "--untracked", help="List directories with untracked files as dirty", default=False, action="store_true")
        # parser.add_argument("-m",   "--missing",   help="Include missing repos", default=False, action="store_true")
        parser.add_argument("-r",   "--recursive", help="Include subrepos", default=False, action="store_true")

        parser.add_argument("-d",   "--dirty",     help="Only show dirty repos", action='store_true')
        parser.add_argument("-p",   "--remotes",   help="Include unpushed/pulled in dirty", default=False, action="store_true")

        parser.add_argument("-c",   "--count",   help="Only return the amount of output", default=False, action="store_true")

    def run(self, name, local, untracked, recursive, dirty, remotes, count):
        # ignore_paths = ['~/.vim', '~/.local', '~/.oh-my-zsh', '~/.cargo', '~/.cache', '~/.config/vim'] # TODO: get from config
        # TODO: Missing???
        if name:
            repo_states = [self.general_state_interactor.get_config_from_name_or_raise(name=name) for name in name]
            all_status = self.local_system_interactor.get_status_for_repos(repo_states)
            all_status = sorted(all_status, key=lambda x: x.repo_state.name)
        elif local:
            repo_states = self.system_state_interactor.get_all_local_repos_in_path(local)
            all_status = [status for status in self.local_system_interactor.get_status_for_repos(repo_states) if status or not dirty]
            all_status = sorted(all_status, key=lambda x: x.repo_state.path)
        else:
            repo_states = self.system_state_interactor.get_all_local_repos_in_path(".")
            all_status = [status for status in self.local_system_interactor.get_status_for_repos(repo_states) if status or not dirty]

        # filter down the results
        if dirty: #dirty only
            all_status = [s for s in all_status if s] #remove all "clean"
        all_status = [s for s in all_status if (
            s.dirty or # always include dirty
            (s.untracked_files and untracked) or # untracked only counts if flag is set
            (s.branch_status and remotes)) ] # unpushed/merged only counts if flag is set
        if count: # return count only
            return len(all_status)
        else:
            return all_status
