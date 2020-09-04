from mgit.interactors.base_mgit_interactor import BaseMgitInteractor

class SingleRepoInteractor(BaseMgitInteractor):
    """
    TODO:
    "add       | path, name              | add a repo (init remote?)                               |"
    "move      | path, name              | move a repo to another path                             |"
    "remove    | name                    | stop tracking a repo                                    |"
    "rename    | name, name              | rename the repo in the config                           |"
    "archive   | name                    | add archive flag to                                     |"
    "unarchive | name                    | remove archive flag to                                  |"
    "install   | name                    | install a repo from remote by name (add listed remotes) |"
    """

    def resolve_remote_urls(self, remote_repos):
        return {k:self.remotes[k].get_url_with_repo(v) for k, v in remote_repos.items()}

    "show      | name                    | show a repo by name                                     |"
    def repo_show(self, project):
        self.repo_should_exist(project)
        return self.repos["dotfiles"].as_dict()

    "init      | path, [[remote name]..] | init a repo local and remote                            |"
    def repo_init(self, name, path=None, remotes=[]):

        remote_repos = dict(remotes or [])

        self.repo_shouldnt_exist(         name )
        self.path_should_be_available(    path )
        self.remotes_should_exist(        remote_repos.keys() )
        self.remote_repos_shouldnt_exist( remote_repos )

        self.local_system.init(path=path,
                remotes=self.resolve_remote_urls(remote_repos)
                )

        #add to config
        self.repos.add_new_repo(
                name=name,
                path=path,
                remotes=remote_repos
            )

        for remote_name, repo_name in remote_repos.items():
            self.remotes[remote_name].init(name=repo_name)

