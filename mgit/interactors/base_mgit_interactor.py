import json

class BaseMgitInteractor:
    def __init__(self, repos, remotes, local_system_interactor, test_mode=False):
        self.test_mode = test_mode
        self.remotes = remotes
        self.repos = repos
        self.local_system = local_system_interactor

    def as_dict(self):
        return self.repos.as_dict()

    def __str__(self):
        return json.dumps(self.as_dict(), indent=2)

    def save(self):
        self.repos.save()
        self.remotes.save()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.save()

    ###
    # Helpers
    ###

    def repo_should_exist(self, key):
        if key not in self.repos:
            raise self.RepoNotFoundError(f"No tracked project found: '{key}'")

    def repo_shouldnt_exist(self, key):
        if key in self.repos:
            raise self.RepoExistsError(f"A project with name '{key}' already exists")

    def path_should_be_git_repo(self, path):
        pass

    def path_should_be_available(self, path):
        if not self.local_system.path_available(path):
            raise self.PathUnavailableError(f"Directory '{path}' exists and is not empty")

    def remotes_should_exist(self, remotes):
        for remote in remotes:
            if remote not in self.remotes:
                raise self.MissingRemoteError(f"No managed remote found: '{remote}'")

    def remote_repos_shouldnt_exist(self, remotes):
        for remote_name, repo_name in remotes.items():
            if repo_name in self.remotes[remote_name]:
                raise self.RemoteRepoExistsError(f"'{repo_name}' already exists in '{remote_name}'")

    ###
    # Exceptions
    ###

    class RemoteRepoExistsError(Exception):
        pass

    class MissingRemoteError(Exception):
        pass

    class PathUnavailableError(Exception):
        pass

    class RepoNotFoundError(Exception):
        pass

    class RepoExistsError(Exception):
        pass

    class CategoryNotFoundError(Exception):
        pass

