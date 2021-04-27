from mgit.repos.repos import Repo
from mgit.repos.repo_remotes import RepoRemote
from mgit.repos.repo_remotes import DerivedRepoRemote
from mgit.repos.repo_remotes import UnnamedRepoOrigin

import os

class ReposBuilder:
    """
    "example2" : {
        "name" : "example2",
        "path" : "example2",
        "originurl" : "bloodyfool2@git.bloodyfool.family",
        "origin" : "home",
        "categories" : "config",
        "home-repo" : "example-name-in-home",
        "ewi-gitlab-repo" : "different-example-name",
        "auto-home-master": "commit push fetch pull"
        }
    """

    def build(self, repo_data, remotes={}):
        self.remotes = remotes

        self.repos = self.validate_and_build_repos(repo_data)

        self.resolve_parents_and_link()
        self.resolve_and_verify_paths()

        return self.repos

    def validate_and_build_repos(self, repo_data):
        ans = {}
        for key, repo_dict in repo_data.items():
            repo = self.validate_and_build_repo(key, repo_dict)
            if repo is not None:
                ans[key] = repo
        return ans

    def validate_and_build_repo(self, key, repo_dict):
        ignore     = bool(int(repo_dict.get("ignore", 0)))
        if ignore:
            return None
        name       = self.validate_name(       key, repo_dict)
        path       = self.validate_path(       key, repo_dict)
        parent     = self.validate_parent(     key, repo_dict)
        categories = self.validate_categories( key, repo_dict)
        archived   = self.validate_archived(   key, repo_dict)
        repo_id    = self.validate_id(         key, repo_dict)
        remotes    = self.validate_remotes(    key, repo_dict)
        origin     = self.validate_origin(     key, repo_dict, remotes)

        return Repo(
                name       = name,
                path       = path,
                parent     = parent,
                origin     = origin,
                categories = categories,
                remotes    = remotes,
                archived   = archived,
                repo_id    = repo_id,
                base_data  = repo_dict
                )

    def validate_name(self, key, repo_dict):
        if "name" not in repo_dict:
            raise self.InvalidConfigError(f"'name' for {key} should exist in dict")
        if key != repo_dict["name"]:
            raise self.InvalidConfigError(f"""'name' for {key} should be equal in dict, found {repo_dict["name"]}""")
        return repo_dict["name"]

    def validate_path(self, key, repo_dict):
        if "path" not in repo_dict:
            raise self.InvalidConfigError(f"'path' for {key} should exist in dict")
        return repo_dict["path"]

    def validate_parent(self, key, repo_dict):
        if "parent" in repo_dict and repo_dict["parent"]:
            return repo_dict["parent"]
        else:
            return None

    def validate_categories(self, key, repo_dict):
        if "categories" in repo_dict:
            assert type(repo_dict["categories"]) is list, f"Repo {key} has non list categories: {repo_dict['categories']}"
            return repo_dict["categories"]

    def validate_remotes(self, key, repo_dict):
        remotes_dict = dict()
        for key, repo_name in repo_dict.items():
            if not key.endswith("-repo"):
                continue
            remote_name      = key[:-5]
            remote = self.validate_remote(key, remote_name, repo_name)
            if remote is not None:
                remotes_dict[remote_name] = remote
        return remotes_dict

    def validate_archived(self, key, repo_dict):
        if "archived" in repo_dict:
            return bool( repo_dict["archived"] )
        else:
            return False

    def validate_id(self, key, repo_dict):
        if "repo_id" in repo_dict:
            return repo_dict["repo_id"]
        else:
            return None

    def validate_remote(self, key, remote_name, repo_name):
        # if remote_name in self.remotes:
        #     self.remotes[remote_name] = self.Remote(remote_name, remotes[remote_name])
        # else:
        #     log_warning(f"Remote '{remote_name}', listed in '{self.name}', doesn't exist, skipping")
        if remote_name in self.remotes:
            return DerivedRepoRemote(self.remotes[remote_name], repo_name)
        else:
            raise self.MissingRemoteReferenceError(f"Missing referenced remote '{remote_name}' for repo '{key}'")

    def validate_origin(self, key, repo_dict, remotes):
        if "origin" in repo_dict:
            origin_name = repo_dict["origin"]
            if origin_name in remotes:
                return remotes[repo_dict["origin"]]
            else:
                raise self.MissingOriginReferenceError(f"Missing origin referenced remote '{origin_name}' for repo '{key}'")
        if "originurl" in repo_dict:
            return UnnamedRepoOrigin(repo_dict["originurl"])
        return None
        # raise self.MissingOriginError(f"Missing origin and originurl for repo '{key}'")

    def resolve_parents_and_link(self):
        for repo_name, repo in self.repos.items():
            self.resolve_parent_and_link(repo)

    def resolve_parent_and_link(self, repo):
        if repo.parent is None:
            return
        if repo.parent in self.repos:
            self.link_parent_and_child(repo)
        else:
            raise self.MissingParentError(f"Parent '{repo.parent}' for repo '{repo.name}' doesn't exist")

    def link_parent_and_child(self, repo):
        repo.parent = self.repos[repo.parent]
        repo.parent.children.append(repo)

    def resolve_and_verify_paths(self):
        for repo_name, repo in self.repos.items():
            self.resolve_and_verify_path(repo)

    def resolve_and_verify_path(self, repo):
        if repo.parent is None:
            if not os.path.isabs(os.path.expanduser(repo.path)):
                raise self.PathError(f"Repo '{repo.name}' without absolute path '{repo.path}' mush have parent")
            return
        if os.path.isabs(os.path.expanduser(repo.path)):
            raise self.PathError(f"Repo '{repo.name}' with parent '{repo.parent}' cannot have an absolute path")
        repo.path = os.path.join(repo.parent.path, repo.path)

    class InvalidConfigError(Exception):
        pass

    class MissingRemoteReferenceError(Exception):
        pass

    class MissingOriginReferenceError(Exception):
        pass

    class MissingOriginError(Exception):
        pass

    class MissingParentError(Exception):
        pass

    class PathError(Exception):
        pass
