from mgit.local.state import *
from typing import *

from git import GitError

from fabric  import Connection
from git     import Repo
from pathlib import Path
import os

class RemoteSystem:

    class RemoteError(Exception):
        pass

    def __init__(self):
        self.class_map: Dict[RemoteType, Type[RemoteSystem]] = {
                RemoteType.SSH: SSHRemoteSystem,
                # RemoteType.GITHUB: None,
                # RemoteType.GITLAB: None
                RemoteType.LOCAL: LocalRemoteSystem
                }

    def init_repo(self, remote_repo: NamedRemoteRepo):
        return self._get_interactor(remote_repo.remote).init_repo(remote_repo)

    def list_remote(self, remote: Remote) -> List[str]:
        return self._get_interactor(remote).list_remote(remote)

    def get_remote_repo_id_mappings(self, remote: Remote) -> Dict[str, Optional[str]]:
        return self._get_interactor(remote).get_remote_repo_id_mappings(remote)

    def _get_interactor(self, remote: Remote) -> 'RemoteSystem':
        return self.class_map[remote.type]()

class LocalRemoteSystem(RemoteSystem):

    def init_repo(self, remote_repo: NamedRemoteRepo) -> str:
        try:
            Repo.init(remote_repo.get_path(), mkdir=True)
            return remote_repo.get_path()
        except GitError as e:
            raise self.RemoteError from e #("Cannot init '{remote_repo.project_name}' in '{remote_repo.remote.name}'")

    def list_remote(self, remote: Remote) -> List[str]:
        return os.listdir(remote.path)

    def get_remote_repo_id_mappings(self, remote: Remote) -> Dict[str, Optional[str]]:
        return {name:self._get_repo_id(Repo(Path(remote.path) / name )) for name in self.list_remote(remote)}

    def _get_repo_id(self, repo):
        try:
            commits = list(repo.iter_commits('HEAD'))
        except:
            return None
        if len(commits) < 1:
            return None
        return commits[-1].hexsha

class SSHRemoteSystem(RemoteSystem):

    def init_repo(self, remote_repo: NamedRemoteRepo) -> str:
        "Inits a new repo and returns its url"
        remote_path = remote_repo.get_path()
        remote_url = remote_repo.remote.url
        if self._exists_remote(remote_repo):
            print("WARNING: Remote folder already exists, not creating remote repo")
            return remote_url
        if not self._run_ssh('mkdir ' + remote_path, url=remote_url):
            raise self.RemoteError("Couldn't create folder, check permissions")
        if not self._run_ssh('git init --bare ' + remote_path, url=remote_url, hide=True):
            raise self.RemoteError("Created folder but could not init repo, manual action required")
        return remote_url

    def list_remote(self, remote: Remote) -> List[str]:
        "Lists all repos in the remote"
        command = f"ls {remote.path}"
        return self._run_ssh(command, url=remote.url, hide=True).stdout.strip().splitlines()

    def get_remote_repo_id_mappings(self, remote: Remote) -> Dict[str, Optional[str]]:
        "Returns a map of the remote repos and their IDs"
        names = self.list_remote(remote)

        command = ""
        for name in names:
            path = os.path.join(remote.path, name)
            command += f"echo {name}; cd {path} && (git rev-list --parents HEAD || echo false) | tail -1;"
        result = self._run_ssh(command, url=remote.url, hide=True).stdout.strip().splitlines()

        clean = [ str(x.strip()) for x in result ]
        pairwise = iter(clean)
        self.repo_id_map = {name : rid if rid != "false" else None for name, rid in zip(pairwise, pairwise)}

        return self.repo_id_map

    def _run_ssh(self, *args, url, **kwargs):
        username, url, port = self._unpack_url(url)
        with Connection(url, user=username, port=port) as ssh:
            return ssh.run(*args, warn=True, **kwargs)

    def _exists_remote(self, remote_repo: NamedRemoteRepo):
        ans = self._run_ssh(f'[ -d "{remote_repo.get_path()}" ]', url=remote_repo.remote.url)
        if ans.return_code == 0:
            return True
        else:
            return False

    def _unpack_url(self, url):
        port = 22
        username, url = url.split('@', 1)
        if ':' in url:
            url, port = url.split(':', 1)
        return username, url, port

    """
    def get_remote_repo_id(self, name):
        if name in self.repo_id_map:
            return self.repo_id_map[name]
        path = os.path.join(self.path, name)
        if not self._exists_remote(path):
            # print("Remote folder already exists, not creating remote repo")
            raise self.MissingRepoException
        command = f"cd {path} && (git rev-list --parents HEAD || echo false) | tail -1"
        git_id, = [str(x.strip()) for x in self._run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()]
        # print(git_id)
        if git_id == "false": #Git repo doesn't exist, OR Git repo exists, but has no commits yet
            command = f"cd {path} && git tag || echo false"
            result = [str(x.strip()) for x in self._run_ssh(command, username=self.username, remote=self.url, hide=True).stdout.strip().splitlines()]
            self.repo_id_map[name] = None
            if result == ["false"]:
                raise self.MissingRepoException
            else:
                raise self.EmptyRepoException
        else:
            self.repo_id_map[name] = git_id
        return self.repo_id_map[name]
    """
