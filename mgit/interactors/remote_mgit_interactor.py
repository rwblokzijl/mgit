from mgit.interactors.base_mgit_interactor import BaseMgitInteractor

import copy
import itertools

class RemoteInteractor(BaseMgitInteractor):

    """
    OLD: we will move these to "remotes" (plural) of per remote commands
        TODO:
        "mass repo"
        list      | -l -r [remotes] | list repos, (missing remote)
        dirty     | repos           | is any repo dirty
        status    | repos           | show status of all repos (clean up ordering)
        fetch     | repos, remotes  | mass fetch
        pull      | repos, remotes  | mass pull
        push      | repos, remotes  | mass push (after shutdown)
    NEW: "remote" (singular)
    """

    def remotes_add(self, path=".", remotes=[], repo_name=None):
        self.remotes_should_exist(remotes)
        #verify and resolve repo
        repo = self.resolve_repo_path(path)

        for remote in remotes:
            if remote in repo.remotes:
                raise self.RemoteRepoExistsError(f"Remote '{remote}' already exists for repo '{repo.name}'")

        # determine repo name in remote
        if not repo_name:
            repo_name = repo.name
        remote_repos = {remote:repo_name for remote in remotes}
        remote_urls =  self.resolve_remote_urls(remote_repos)

        # add to config
        self.repos.add_remotes_to_repo(repo.name, remote_repos)

        # add to remotes
        for remote_name, repo_name in remote_repos.items():
            self.remotes[remote_name].init(name=repo_name)

        # add to actual repo
        self.local_system.add_remotes_to_path(repo.path, remote_urls)

    def remotes_list_repos(self, remotes=[]):

        # get flat repos list
        remotes_repo_dict = dict()
        for remote in remotes:
            if remote in self.remotes:
                remotes_repo_dict[remote] = self.remotes[remote].list()
            else:
                print(f"WARNING: '{remote}' is not a known remote")
        for remote in remotes_repo_dict:
            remotes_repo_dict[remote] = {repo : None for repo in remotes_repo_dict[remote]}

        # note repos with parents
        has_parent = []
        for remote, repos in copy.deepcopy(remotes_repo_dict).items():
            for repo in repos:
                if repo not in self.repos:
                    continue
                if self.repos[repo].parent:
                    parent = self.repos[repo].parent.name
                    if parent in repos:
                        remotes_repo_dict[remote][parent] = remotes_repo_dict[remote][parent] or list() # if none replace with empty list
                        remotes_repo_dict[remote][parent].append(repo)
                        has_parent.append(repo)

        def resolve_children(repo_name, flat_dict):
            remotes_repo_dict = dict()
            children = flat_dict[repo_name]
            if children is None:
                return None
            for child in children:
                remotes_repo_dict[child] = resolve_children(child, flat_dict)
            return remotes_repo_dict

        retval = dict()
        for remote, repos in remotes_repo_dict.items():
            retval[remote] = dict()
            for repo, children in repos.items():
                if repo in has_parent:
                    continue
                retval[remote][repo] = dict()
                retval[remote][repo] = resolve_children(repo, remotes_repo_dict[remote])

        return retval

