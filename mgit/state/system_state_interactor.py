from mgit.state.state import RepoState, RemoteRepo, NamedRemoteRepo, UnnamedRemoteRepo, Remote, AutoCommand, RemoteBranch, LocalBranch, RemoteType

from git import Repo
from git.exc import GitError
from pathlib import Path

from typing import Optional

import subprocess

class SystemStateInteractor:
    """Reads system state and returns a RepoState object"""

    def get_state(self, path: Path) -> Optional[RepoState]:
        try:
            repo = Repo(path, search_parent_directories=True)
            return self._get_state_from_repo(repo)
        except GitError:
            return None

    def set_state(self, repo_state: RepoState):
        raise NotImplementedError("Not yet implemented")

    def _run_command(self, command):
        with subprocess.Popen(command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT) as p:
            while (line := p.stdout.readline()):
                yield line # TODO make non blocking, idk how right now

    def _get_repo_id_from_path(self, path: Path):
        try:
            Repo(path)
        except GitError:
            return None
        git_id = "".join([str(x.strip().decode("utf-8")) for x in self._run_command(f"cd {path} && git rev-list --parents HEAD | tail -1")])
        if ' ' in git_id: #Git repo exists, but has no commits yet
            return None
        return(git_id)

    def _get_parent(self, repo):
        parent_path = Path(repo.working_dir).parents[0]
        try:
            parent = Repo(parent_path, search_parent_directories=True)
        except GitError:
            return None
        return self._get_state_from_repo(parent)

    def _get_state_from_repo(self, repo):
        remotes = set([UnnamedRemoteRepo(rem.name, rem.url) for rem in repo.remotes])
        return RepoState(
                source="repo",
                repo_id=self._get_repo_id_from_path(repo.working_dir),
                path=Path(repo.working_dir),
                remotes=remotes,
                parent=self._get_parent(repo),

                #unknown
                name=None,
                origin=None,
                auto_commands=None,
                archived=None,
                categories=None
                )

