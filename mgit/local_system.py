from mgit.state import RepoState, RemoteBranch, LocalBranch, UnnamedRemoteRepo

from subprocess       import Popen, PIPE, STDOUT
from git              import Repo, GitError, Head
from typing           import List, Optional, Iterable, FrozenSet
from dataclasses      import dataclass

import os

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

class LocalSystem:

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

