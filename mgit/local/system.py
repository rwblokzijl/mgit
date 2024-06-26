from mgit.remote.remote_system import RemoteSystem
from mgit.local.state import *
# from typing import *

from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
from dataclasses import asdict

from pygit2 import Repository, GitError
import pygit2
import fnmatch
import configparser

class System:
    """
    Reads system state and returns a RepoState object

    This only interacts with the Repo through the Repo object
    """

    def __init__(self, settings_config="~/.config/mgit/settings.ini"):
        self._settings_file = os.path.abspath(os.path.expanduser(settings_config))

        self._settings_config = self._read_config()

    def _read_config(self):
        settings = configparser.ConfigParser(delimiters=('='))
        if not settings.read(self._settings_file):
            raise FileNotFoundError(f"Failed to open {self._settings_file}")

        return settings

    def get_state(self, path: Path | str) -> RepoState:
        git_workdir = pygit2.discover_repository(str(Path(path).expanduser().absolute()))
        if git_workdir is None:
            raise self.SystemError(f"Not a git dir: {git_workdir}")
        repo = Repository(git_workdir)
        return self._get_state_from_repo(repo)

    def set_state(self, repo_state: RepoState, remote: RemoteRepo|None=None, init=False):
        if not repo_state.path:
            raise ValueError(f"'{repo_state.name}' does not specify a path")
        repo_keys = list(asdict(repo_state).keys())
        repo_keys.remove("source")

        # Not relevant for system state
        repo_keys.remove("name")
        repo_keys.remove("auto_commands")
        repo_keys.remove("archived")
        repo_keys.remove("tags")

        # TODO: validate repo_id and parent?
        repo_keys.remove("repo_id")
        repo_keys.remove("parent")

        # will raise if not repo
        if remote:
            repo = self._clone_repo_from_remote_or_raise(repo_state, remote)
        elif init:
            repo = self._init_repo(repo_state.path.expanduser().absolute())
        else:
            repo = self._get_clone_or_init_repo(repo_state, remote)
        repo_keys.remove("path")

        # NO RAISING AFTER THIS POINT, CATS ARE ADDED
        self._remove_remotes(repo_state.path)
        for remote_repo in repo_state.remotes:
            if remote_repo.name not in repo.remotes:
                repo.remotes.create(remote_repo.name, remote_repo.url)
        repo_keys.remove("remotes")

        # make changes here

        assert not repo_keys, repo_keys


    def _remove_remotes(self, path):
        repo: Repository | None = self._get_repo_from_path(path)
        if repo is not None:
            for remote in repo.remotes:
                repo.remotes.delete(remote.name)

    def _get_state_or_none(self, *args, **kwargs) -> Optional[RepoState]:
        try:
            return self.get_state(*args, **kwargs)
        except self.SystemError:
            return None

    def get_all_local_repos_in_path(self, path: Path | str, ignore_paths=None) -> List[RepoState]:
        if ignore_paths is None:
            ignore_paths = self._settings_config["settings"]["local-ignore"].split()
        local_git_paths = self._get_local_git_paths(Path(path), ignore_paths)
        return [state for local_path in local_git_paths if (state := self._get_state_or_none(local_path)) is not None]

    def _clone_repo_from_remote_or_raise(self, repo_state, remote) -> Repository:
        repo = self._clone_repo_from_remote(repo_state.path, remote)
        if not repo:
            raise RemoteSystem.RemoteError("Cannot clone from")
        return repo

    def _get_clone_or_init_repo(self, repo_state, remote=None) -> Repository:
        repo = self._get_repo_from_path(repo_state.path)
        if repo is None:
            repo = self._clone_repo(repo_state, remote)
        if repo is None:
            repo = self._init_repo(repo_state.path)
        return repo

    def _init_repo(self, path: Path) -> Repository:
        return Repository(pygit2.init_repository(path=path.expanduser().absolute()).workdir)

    def _clone_repo(self, repo_state: RepoState, default_remote=None):
        repo = None
        for remote in repo_state.remotes:
            repo = self._clone_repo_from_remote(repo_state.path, remote)
            if repo:
                break
        return repo

    def _clone_repo_from_remote(self, path, remote_repo: RemoteRepo) -> Repository | None:
        try:
            # return Repo.clone(url=remote_repo.url, to_path=path.expanduser().absolute(), origin=remote_repo.name)
            return pygit2.clone_repository(url=remote_repo.url, path=path.expanduser().absolute())
        except GitError:
            return None

    def _get_repo_from_path(self, path: Path) -> Repository | None:
        try:
            # repo = Repo(path.expanduser().absolute())
            repo = Repository(path.expanduser().absolute())
        except GitError:
            return None
        return repo

    def _get_repo_id(self, repo):
        try:
            commits = list(repo.walk(repo.head.target))
        except (GitError, KeyError):
            return None
        if len(commits) < 1:
            return None
        return commits[-1].hex

    def _get_parent(self, repo):
        parent_path = Path(repo.workdir).parents[0]
        parent_git_dir = pygit2.discover_repository(str(parent_path.expanduser().absolute()))
        if parent_git_dir is None:
            return None
        parent = Repository(parent_git_dir)
        return self._get_state_from_repo(parent)

    def _get_state_from_repo(self, repo: Repository) -> RepoState:
        remotes: Set[RemoteRepo] = set([UnnamedRemoteRepo(str(rem.name), str(rem.url)) for rem in repo.remotes])
        rs =  RepoState(
                source="repo",
                repo_id=self._get_repo_id(repo) or None,
                path=Path(repo.workdir),
                remotes=remotes,
                parent=self._get_parent(repo),

                #unknown
                name=None,
                # origin=None,
                auto_commands=None,
                archived=None,
                tags=None
                )
        assert rs.path
        return rs

    def _get_local_git_paths(self, path: Path, ignore_paths):
        excludes = [Path(i_path).expanduser() for i_path in ignore_paths]
        command  = f"find {path} -xdev -name '.git'"
        result   = self._run_command(command)
        lines    = [line.strip().decode("utf-8") for line in result]
        paths    = set([str(Path(line).expanduser().absolute()) for line in lines])
        for exclude in excludes:
            paths -= set(fnmatch.filter(paths, str(exclude)))
        paths    = [Path(path) for path in paths]
        repos    = [path.parent for path in paths]
        return repos

    def _run_command(self, command):
        with Popen(command,
                shell=True,
                stdout=PIPE,
                stderr=STDOUT) as p:
            while (line := p.stdout.readline()): #type: ignore
                yield line # TODO make non blocking, idk how right now

    class SystemError(Exception):
        pass

