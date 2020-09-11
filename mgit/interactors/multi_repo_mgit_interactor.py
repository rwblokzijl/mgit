from mgit.interactors.base_mgit_interactor import BaseMgitInteractor

import copy
import itertools

class MultiRepoInteractor(BaseMgitInteractor):

    """
    TODO:
    "mass repo"
    list      | -l -r [remotes] | list repos, (missing remote)
    dirty     | repos           | is any repo dirty
    status    | repos           | show status of all repos (clean up ordering)
    fetch     | repos, remotes  | mass fetch
    pull      | repos, remotes  | mass pull
    push      | repos, remotes  | mass push (after shutdown)
    """

    def sanity_check_repos(self):
        # - IDs must match for:
        #   - repo:remotes
        #   - remote repos
        #   - config:repo
        # - IDs must match for:
        #   - config:repo
        #   - config:repo:path
        pass

    def repos_list_repos(self, path, installed, missing, archived, untracked, conflict, ignored):
        ans = []
        for repo in self.repos:
            path_id = self.local_system.get_repo_id_from_path(repo.path)
            status = None
            is_git = self.local_system.is_git_repo(repo.path)
            is_empty = self.local_system.path_empty_or_missing(repo.path)

            if repo.repo_id == path_id and path_id is not None:
                if installed:
                    status = "installed " + repo.path
            elif repo.repo_id is None and path_id is not None:
                #TODO Warn: ID is not set, but can be, run update
                if installed:
                    status = "installed " + repo.path
            elif repo.repo_id is not None and path_id is not None:
            #    there has to be a repo with same id in repo.path
            #    warn if no ID set AND path has commits?
                if conflict:
                    status = "conflict  " + repo.path
            elif path_id is None and is_git and repo.repo_id is None:
                if installed:
                    status = "empty     " + repo.path
            elif path_id is None and is_git and repo.repo_id is None:
                if installed:
                    status = "empty     " + repo.path
                # remotes should match
            # elif archived:
            #     # not installed but archived is set
            #     pass
            # elif missing:
            #     pass
            if status:
                ans.append(status)
        if untracked:
            for line in self.local_system.get_local_git_paths(path, ignore_paths=[]):
                print(line)
                # question: what makes a repo "untracked"
                #   there is no repo with this path AND ID
                #   if the path exists but the ID is wrong: Warn
                #   if the path exists but the ID is missing: Warn or update?? maybe update flag for this command? maybe
                #   update command
                #   if ID exists but the path is wrong, this might be ok,
                #     if the project with ID is missing: warn and maybe update

                pass
        ans.sort()
        return ans

        # Installed (repos)
        # Archived (repos)
        # Missing (repos)
        # Conflict (repos)
        # Untracked (paths)
        # Ignored (paths)

    def repos_status(self, name, local, dirty, missing, recursive):
        ignore_paths = ['~/.vim', '~/.local', '~/.oh-my-zsh', '~/.cargo', '~/.cache'] # TODO: get from config
        if name:
            repos = []
            for n in name:
                self.repo_should_exist(n)

                repos.append(self.repos[n])
            ans = self.local_system.repos_status(repos=repos, dirty=dirty, missing=missing, recursive=recursive,
                    untracked_files=untracked)
            return ans
        elif local:
            ans =  self.local_system.recursive_status(local, dirty, ignore_paths=ignore_paths, untracked_files=untracked)
            return ans
        else:
            ans = self.local_system.repos_status(repos=self.repos, dirty=dirty, missing=missing, recursive=recursive,
                    untracked_files=untracked)
            return ans

    def repos_dirty(self, name, local, untracked):
        if 0 == len(list(self.repos_status(name, local, dirty=True, missing=False, untracked=untracked, recursive=False))):
            raise Exception()
        else:
            return

