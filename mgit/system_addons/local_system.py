from git import Repo
from git.exc import InvalidGitRepositoryError

import os
import subprocess
import collections

class LocalSystem:

    """
    Local System interactor
    """

    " Helpers "
    def run_command(self, command):
        with subprocess.Popen(command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT) as p:
            while (line := p.stdout.readline()):
                yield line # TODO make non blocking, idk how right now

    " Read only functions"
    def get_repo_id_from_path(self, path):
        try:
            Repo(path)
        except:
            return None
        git_id = "".join([str(x.strip().decode("utf-8")) for x in self.run_command(f"cd {path} && git rev-list --parents HEAD | tail -1")])
        if ' ' in git_id: #Git repo exists, but has no commits yet
            return None
        return(git_id)

    def path_empty_or_missing(self, path):
        if not os.path.exists(path):
            return True
        if os.path.isdir(path) and not os.listdir(path):
            return True
        return False

    def is_empty_git_repo(self, path):
        if not self.is_git_repo(path):
            return False
        if os.path.isdir(path) and os.listdir(path) == [".git"]:
            return True

    def path_available(self, path):
        if not os.path.exists(path):
            return True
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

    def validate_origin(self, origin, remotes):
        if origin and origin not in remotes:
            raise self.MissingRemoteError()

    def should_include(self, line, excludes):
        for exclude in excludes:
            if line.startswith(exclude):
                return False
        return True

    def get_local_git_paths(self, path="~", ignore_paths=[]):
        excludes = [os.path.abspath(os.path.expanduser(path)) for path in ignore_paths]
        command  = "find "+path+" -xdev -name '.git'"
        result   = [os.path.abspath(os.path.expanduser(line.strip().decode("utf-8"))) for line in self.run_command(command)]
        result   = [line for line in result if self.should_include(line, excludes)]
        repos    = list()
        for line in result:
            try:
                repos.append(os.path.realpath(line[:-4]))
            except:
                pass
        return repos

    def get_all_local_repos_in_path(self, path="~", ignore_paths=[]):
        repos=list()
        for line in self.get_local_git_paths(path, ignore_paths):
            try:
                repos.append(Repo(line))
            except Exception:
                pass
        return repos

    def repos_status(self, repos, dirty, missing, recursive, untracked_files=False, top_level=True,
            include_remotes=False):
        ans = {}
        for repo in repos:
            repo_children = None
            repo_status = None

            # Calculate children
            if len(repo.children) and recursive:
                repo_children = self.repos_status(repos=repo.children, dirty=dirty, missing=missing, recursive=recursive, top_level=False)

            # Skip on top level if repo is child
            if recursive and repo.parent is not None and top_level:
                continue

            try:
                local_repo = Repo(repo.path)

                try:
                    commits_behind = len(list(local_repo.iter_commits('master..origin/master')))
                except:
                    commits_behind = 0
                try:
                    commits_ahead  = len(list(local_repo.iter_commits('origin/master..master')))
                except:
                    commits_ahead  = 0

                if local_repo.is_dirty():
                    repo_status = "dirty     " + repo.name
                elif untracked_files and local_repo.untracked_files:
                    repo_status = "dirty(u)  " + repo.name
                elif include_remotes and (commits_ahead or commits_behind):
                    repo_status = f"{str(commits_ahead).rjust(3)}+ {str(commits_behind).rjust(3)}- " + repo.working_dir
                elif not dirty or repo_children:
                    repo_status = "clean     " +  repo.name
            except Exception as e:
                if missing:
                    repo_status = "missing   " + repo.name
            if repo_children or repo_status:
                ans[repo_status] = repo_children
        return collections.OrderedDict(sorted(ans.items()))

    def recursive_status(self, path, dirty=False, untracked_files=False, ignore_paths=[], include_remotes=False):
        repos = self.get_all_local_repos_in_path(path, ignore_paths=ignore_paths)

        for repo in repos:

            try:
                commits_behind = len(list(repo.iter_commits('master..origin/master')))
            except:
                commits_behind = 0
            try:
                commits_ahead  = len(list(repo.iter_commits('origin/master..master')))
            except:
                commits_ahead  = 0

            if repo.is_dirty():
                yield "dirty     " + repo.working_dir
            elif untracked_files and repo.untracked_files:
                yield "dirty(u)  " + repo.working_dir
            elif include_remotes and (commits_ahead or commits_behind):
                yield f"{str(commits_ahead).rjust(3)}+ {str(commits_behind).rjust(3)}- " + repo.working_dir
            else:
                if not dirty:
                    yield "clean     " +  repo.working_dir

    " Write functions"
    # Git helpers
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

    # Git commands
    def init(self, path, remotes={}, origin=None):
        self.validate_origin(origin, remotes)
        self.ensure_directory(path)

        repo = Repo.init(path)

        self.add_remotes(repo, remotes)
        if origin:
            self.add_origin(repo, origin, remotes)

    def clone(self, path, remotes, origin):
        repo = Repo.clone_from(remotes[origin], os.path.expanduser(path), multi_options=[f'--origin {origin}'])
        remotes.pop(origin)
        self.add_remotes(repo, remotes)

    def fetch(self, path, remotes=None):
        def fetchh(remote):
            remote.fetch()
            yield f"fetching {path} from {remote}"
        try:
            repo = Repo(path)
            if remotes:
                for remote in repo.remotes:
                    if str(remote) in remotes:
                        yield fetchh(remote)
            else:
                for remote in repo.remotes:
                    yield fetchh(remote)
        except:
            pass

    class MissingRemoteError(Exception):
        pass

