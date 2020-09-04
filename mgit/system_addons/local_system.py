from git import Repo
from git.exc import InvalidGitRepositoryError

import os
import subprocess

class LocalSystem:

    def run_command(self, command):
        with subprocess.Popen(command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT) as p:
            while (line := p.stdout.readline()):
                yield line # TODO make non blocking, idk how right now

    def path_available(self, path):
        if self.is_git_repo(path):
            return False
        return True

    def is_git_repo(self, path):
        if not os.path.exists(path):
            return False
        try:
            _ = Repo(path).git_dir
            return True
        except InvalidGitRepositoryError:
            return False

    def ensure_directory(self, path):
        os.makedirs(path, exist_ok=True)

    def add_remotes(self, repo, remotes):
        for remote, url in remotes.items():
            repo.create_remote(remote, url)

    def add_origin(self, repo, origin, remotes):
        if origin in remotes:
            repo.create_remote("origin", remotes[origin])
        else:
            raise self.MissingRemoteError()

    def validate_origin(self, origin, remotes):
        if origin and origin not in remotes:
            raise self.MissingRemoteError()

    def init(self, path, remotes={}, origin=None):
        self.validate_origin(origin, remotes)
        self.ensure_directory(path)

        repo = Repo.init(path)

        self.add_remotes(repo, remotes)
        if origin:
            self.add_origin(repo, origin, remotes)

    def exclude(self, line, excludes):
        for exclude in excludes:
            if line.startswith(exclude):
                return False
        return True

    def get_local_git_paths(self, path="~", ignore_paths=[]):
        excludes = [os.path.abspath(os.path.expanduser(path)) for path in ignore_paths]
        command  = "find "+path+" -xdev -name '.git'"
        result   = [os.path.abspath(os.path.expanduser(line.strip().decode("utf-8"))) for line in self.run_command(command)]
        result   = [line for line in result if self.exclude(line, excludes)]
        repos    = list()
        for line in result:
            try:
                repos.append(os.path.realpath(line[:-4]))
            except:
                pass
        return repos

    def get_all_local_repos_in_path(self, path="~", ignore_paths=['~/.vim', '~/.local', '~/.oh-my-zsh', '~/.cargo']):
        repos=list()
        for line in self.get_local_git_paths(path, ignore_paths):
            try:
                repos.append(Repo(line))
            except Exception:
                pass
        return repos

    def recursive_status(self, path, dirty=False):
        repos = self.get_all_local_repos_in_path(path)

        for repo in repos:
            if repo.is_dirty() or repo.untracked_files:
                yield "dirty  " + repo.working_dir
            else:
                if not dirty:
                    yield "clean  " +  repo.working_dir

    class MissingRemoteError(Exception):
        pass
