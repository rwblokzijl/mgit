from mgit.state.state  import *
from git         import Repo, GitError
from typing      import *
from dataclasses import dataclass

from mgit.ui.cli            import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

@dataclass(frozen=True)
class RemoteBranchStatus:
    remote_branch: RemoteBranch
    commits_ahead: int
    commits_behind: int

    def __bool__(self):
        return bool(self.commits_ahead) or bool(self.commits_behind)

    def repr(self):
        return f"    {str(self.commits_ahead).rjust(2)}+ {str(self.commits_behind).rjust(2)}- {self.remote_branch.remote_repo.get_name()}"

    def __repr__(self):
        if self.__bool__():
            return self.repr()
        return ""

@dataclass(frozen=True)
class BranchStatus:
    local_branch: LocalBranch
    remote_branch_status: FrozenSet[RemoteBranchStatus]

    def __bool__(self):
        return any(self.remote_branch_status)

    def __repr__(self):
        return '\n  ' + self.local_branch.ref + '\n' + '\n'.join([repr(x) for x in self.remote_branch_status if x])

@dataclass
class Status:
    repo_state: RepoState
    dirty: bool
    untracked_files: bool
    branch_status: FrozenSet[BranchStatus]

    def __bool__(self):
        return any(self.branch_status) or self.dirty or self.untracked_files

    def __repr__(self):
        return self.represent(verbose=False)

    def represent(self, verbose=True):
        ans = ""
        ans += ('dirty' if self.dirty or self.untracked_files else 'clean')
        ans += ('(u)' if self.untracked_files else '   ') + " "
        ans += (self.repo_state.name or str(self.repo_state.path)) + " "
        ans += '\n  '.join([repr(x) for x in self.branch_status if x])
        return ans.strip('\n')

@MgitCommand.register
class CommandStatus(AbstractLeafCommand):
    command = "status"
    help="Show the differences between remotes and local branches"

    def build(self, parser):
        parser.add_argument(      "name",        help="Name of the project", nargs="*", type=str)
        parser.add_argument("-l", "--local",     help="Path to recursively explore", metavar="DIR", nargs="?", const=".", type=str)

        parser.add_argument("-u", "--untracked", help="List directories with untracked files as dirty", default=False, action="store_true")
        # parser.add_argument("-m", "--missing",   help="Include missing repos", default=False, action="store_true")

        parser.add_argument("-d", "--dirty",     help="Only show dirty repos", action='store_true')
        parser.add_argument("-p", "--remotes",   help="Include unpushed/pulled in dirty", default=False, action="store_true")

        parser.add_argument("-c", "--count",     help="Only return the amount of repos returned", default=False, action="store_true")

    def get_status_for_repos(self, repo_states: List[RepoState]) -> Iterable[Status]:
        return (status for repo_state in repo_states if (status := self.get_status_for_repo(repo_state)) is not None)

    def get_status_for_repo(self, repo_state: RepoState) -> Optional[Status]:
        try:
            repo = Repo(repo_state.path)
        except GitError:
            return None

        branch_status = set()
        for branch in repo.branches:
            # TODO: use configured branch mappings here
            remote_branch_status = set()
            for remote in repo.remotes:
                try:
                    commits_behind = len(list(repo.iter_commits(f'{branch.name}..{remote.name}/{branch.name}')))
                except:
                    commits_behind = 0
                try:
                    commits_ahead  = len(list(repo.iter_commits(f'{remote.name}/{branch.name}..{branch.name}')))
                except:
                    commits_ahead  = 0
                remote_branch_status.add(RemoteBranchStatus(
                        RemoteBranch(UnnamedRemoteRepo(remote_name=remote.name, url=remote.url),ref=branch.name),
                        commits_ahead=commits_ahead,
                        commits_behind=commits_behind
                        ))
            branch_status.add(BranchStatus(LocalBranch(ref=branch.name), frozenset(remote_branch_status)))

        return Status(
                repo_state=repo_state,
                dirty=bool(repo.is_dirty()),
                untracked_files=bool(repo.untracked_files),
                branch_status=frozenset(branch_status))

    def get_config_from_name_or_raise(self, name) -> RepoState:
        config_state = self.config.get_state(name=name)
        if not config_state:
            raise ValueError(f"'{name}' is not known as a tracked repo")
        return config_state

    def run(self, name, local, untracked, dirty, remotes, count):
        # ignore_paths = ['~/.vim', '~/.local', '~/.oh-my-zsh', '~/.cargo', '~/.cache', '~/.config/vim'] # TODO: get from config
        if name:
            repo_states = [self.get_config_from_name_or_raise(name=name) for name in name]
            all_status = self.get_status_for_repos(repo_states)
            all_status = sorted(all_status, key=lambda x: x.repo_state.name)
        elif local:
            repo_states = self.system.get_all_local_repos_in_path(local)
            all_status = [status for status in self.get_status_for_repos(repo_states) if status or not dirty]
            all_status = sorted(all_status, key=lambda x: x.repo_state.path)
        else:
            repo_states = self.system.get_all_local_repos_in_path(".")
            all_status = [status for status in self.get_status_for_repos(repo_states) if status or not dirty]

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

