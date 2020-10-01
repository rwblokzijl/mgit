from mgit.interactors.base_mgit_interactor import BaseMgitInteractor

from pathlib import Path

class SingleRepoInteractor(BaseMgitInteractor):
    """
    TODO:
    "add       | path, name              | add a repo (init remote?)                               |"
    "move      | path, name              | move a repo to another path                             |"
    "remove    | name                    | stop tracking a repo                                    |"
    "rename    | name, name              | rename the repo in the config                           |"
    "archive   | name                    | add archive flag to                                     |"
    "unarchive | name                    | remove archive flag to                                  |"
    """

    def resolve_remote_urls(self, remote_repos):
        return {k:self.remotes[k].get_url_with_repo(v) for k, v in remote_repos.items()}

    def get_default_remotes(self):
        return [remote for remote in self.remotes if remote.is_default]

    "show      | name                    | show a repo by name                                     |"
    def repo_show(self, project):
        self.repo_should_exist(project)
        return self.repos[project].as_dict()

    "init      | path, [[remote name]..] | init a repo local and remote                            |"
    def repo_init(self, name, path, remotes=[], origin=None):
        remote_repos = dict(remotes or [])

        self.repo_shouldnt_exist(         name )
        self.path_should_be_available(    path )
        self.remotes_should_exist(        remote_repos.keys() )
        self.remote_repos_shouldnt_exist( remote_repos )

        self.local_system.init(path=path,
                remotes=self.resolve_remote_urls(remote_repos),
                origin=origin
                )

        #add to config
        self.repos.add_new_repo(
                name=name,
                path=path,
                remotes=remote_repos
            )

        for remote_name, repo_name in remote_repos.items():
            self.remotes[remote_name].init(name=repo_name)

    "install   | name   | install a repo from remote by name (add listed remotes) |"
    def get_repo_install_info(self, name, remote=None):
        self.repo_should_exist( name )
        repo = self.repos[name]
        self.path_should_be_available(repo.path)

        repo_dict = repo.as_dict()

        repo_info = dict()
        repo_info["path"] = repo_dict["path"]
        repo_info["remotes"] = {k:v["url"] for k,v in repo_dict["remotes"].items()}

        if remote is not None and remote not in repo_info["remotes"]:
            raise self.MissingRemoteError(f"{remote} is not a valid remote for {name}")

        repo_info["origin"] = remote or repo_dict["origin"]["name"]

        return repo_info

    def repo_missing(self, repo):
        if not self.local_system.path_empty_or_missing(repo.path):
            return False
        return True

    def repo_install(self, name, remote):
        repo_info = self.get_repo_install_info(name)

        self.local_system.clone(path=repo_info["path"], remotes=repo_info["remotes"], origin=repo_info["origin"])



