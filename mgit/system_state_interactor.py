from mgit.state import RepoState, RemoteRepo, NamedRemoteRepo, UnnamedRemoteRepo, Remote, AutoCommand, RemoteBranch, LocalBranch, RemoteType

from git import Repo
from git.exc import GitError
from pathlib import Path

from typing import Optional, Set, List

from subprocess import Popen, PIPE, STDOUT
import dataclasses
import os

class SystemStateInteractor:
    """
    Reads system state and returns a RepoState object

    This only interacts with the Repo through the Repo object
    """

    def get_state(self, path: Path) -> Optional[RepoState]:
        try:
            repo = Repo(path, search_parent_directories=True)
        except GitError:
            return None
        return self._get_state_from_repo(repo)

    def set_state(self, repo_state: RepoState):
        if not repo_state.path:
            raise ValueError(f"'{repo_state.name}' does not specify a path")
        repo_keys = list(dataclasses.asdict(repo_state).keys())
        repo_keys.remove("source")

        # Not relevant for system state
        repo_keys.remove("name")
        repo_keys.remove("auto_commands")
        repo_keys.remove("archived")
        repo_keys.remove("categories")

        # will raise if not repo
        repo = self._get_clone_or_init_repo(repo_state)
        repo_keys.remove("path")

        for remote_repo in repo_state.remotes:
            if remote_repo.get_name() not in repo.remotes:
                repo.create_remote(remote_repo.get_name(), remote_repo.get_url())
        repo_keys.remove("remotes")

        # TODO: validate repo_id and parent?
        repo_keys.remove("repo_id")
        repo_keys.remove("parent")

        # make changes here

        assert not repo_keys, repo_keys

    def get_all_local_repos_in_path(self, path, ignore_paths=None) -> List[RepoState]:
        if ignore_paths is None:
            # ignore_paths = []
            ignore_paths = ['~/.vim', '~/.local', '~/.oh-my-zsh', '~/.cargo', '~/.cache', '~/.config/vim'] # TODO: get from config
        local_git_paths = self._get_local_git_paths(path, ignore_paths)
        return [state for path in local_git_paths if (state := self.get_state(path)) is not None]

    def _get_clone_or_init_repo(self, repo_state) -> Repo:
        repo = self._get_repo_from_path(repo_state.path)
        if repo is None:
            for remote in repo_state.remotes:
                repo = self._clone_repo(repo_state.path, remote)
                if repo:
                    break
        if repo is None:
            repo = self._init_repo(repo_state.path)
        return repo

    def _init_repo(self, path) -> Repo:
        # Should raise
        # try:
        # os.mkdir(path)
        return Repo.init(path=path)
        # except GitError:
        #     return None

    def _clone_repo(self, path, remote_repo: RemoteRepo) -> Repo:
        # Should just raise for now
        # try:
        return Repo.clone_from(url=remote_repo.get_url(), to_path=path, origin=remote_repo.get_name())
        # except GitError:
        #     return None

    def _get_repo_from_path(self, path: Path) -> Optional[Repo]:
        try:
            repo = Repo(path)
        except GitError:
            return None
        return repo

    def _get_repo_id(self, repo):
        try:
            commits = list(repo.iter_commits('HEAD'))
        except:
            return None
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

    def _get_state_from_repo(self, repo: Repo) -> RepoState:
        remotes: Set[RemoteRepo] = set([UnnamedRemoteRepo(rem.name, rem.url) for rem in repo.remotes])
        rs =  RepoState(
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
        return rs

    def _should_include(self, line, excludes):
        for exclude in excludes:
            if line.startswith(exclude):
                return False
        return True

    def _get_local_git_paths(self, path, ignore_paths):
        excludes = [os.path.abspath(os.path.expanduser(path)) for path in ignore_paths]
        command  = "find "+path+" -xdev -name '.git'"
        result   = [os.path.abspath(os.path.expanduser(line.strip().decode("utf-8"))) for line in self._run_command(command)]
        result   = [line for line in result if self._should_include(line, excludes)]
        repos    = list()
        for line in result:
            try:
                repos.append(os.path.realpath(line[:-4]))
            except:
                pass
        return repos

    def _run_command(self, command):
        with Popen(command,
                shell=True,
                stdout=PIPE,
                stderr=STDOUT) as p:
            while (line := p.stdout.readline()):
                yield line # TODO make non blocking, idk how right now

