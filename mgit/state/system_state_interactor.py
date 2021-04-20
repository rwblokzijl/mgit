from mgit.state.state import RepoState, RemoteRepo, NamedRemoteRepo, UnnamedRemoteRepo, Remote, AutoCommand, RemoteBranch, LocalBranch, RemoteType

from git import Repo
from git.exc import GitError
from pathlib import Path

from typing import Optional, Set

import subprocess
import dataclasses

class SystemStateInteractor:
    """Reads system state and returns a RepoState object"""

    def get_state(self, path: Path) -> Optional[RepoState]:
        try:
            repo = Repo(path, search_parent_directories=True)
            return self._get_state_from_repo(repo)
        except GitError:
            return None

    def set_state(self, repo_state: RepoState):
        if not repo_state.path:
            raise ValueError(f"Repo_state must have a path")
        repo_keys = list(dataclasses.asdict(repo_state).keys())
        repo_keys.remove("source")
        repo_keys.remove("name")

        # make changes here

        assert not repo_keys, repo_keys

    def _get_repo_from_path(self, path: Path):
        try:
            repo = Repo(path)
        except GitError:
            return None
        return repo

    def _run_command(self, command):
        with subprocess.Popen(command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT) as p:
            while (line := p.stdout.readline()):
                yield line # TODO make non blocking, idk how right now

    def _get_repo_id(self, repo):
        commits = list(repo.iter_commits('HEAD'))
        if len(commits) < 1:
            return None
        return commits[-1].hexsha

    def _get_parent(self, repo):
        parent_path = Path(repo.working_dir).parents[0]
        try:
            parent = Repo(parent_path, search_parent_directories=True)
        except GitError:
            return None
        return self._get_state_from_repo(parent)

    def _get_state_from_repo(self, repo) -> RepoState:
        remotes: Set[RemoteRepo] = set([UnnamedRemoteRepo(rem.name, rem.url) for rem in repo.remotes])
        return RepoState(
                source="repo",
                repo_id=self._get_repo_id(repo),
                path=Path(repo.working_dir),
                remotes=remotes,
                parent=self._get_parent(repo),

                #unknown
                name=None,
                # origin=None,
                auto_commands=None,
                archived=None,
                categories=None
                )

