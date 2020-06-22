from mgit.persistence.remotes_config_persistence import RemotesConfigFilePersistence
from mgit.remotes.remotes_builder                import RemotesBuilder
from mgit.remotes.remotes_interactor             import RemotesInteractor

from mgit.persistence.repo_config_persistence import ReposConfigFilePersistence
from mgit.repos.repos_builder                 import ReposBuilder
from mgit.repos.repos_interactor              import ReposInteractor

import json

def build_interactor():
    pass

class Builder:
    def build(self, repos_config, remotes_config):
        remotes_persistence = RemotesConfigFilePersistence(remotes_config)
        remotes_interactor = RemotesInteractor(persistence=remotes_persistence, builder=RemotesBuilder())

        repos_persistence = ReposConfigFilePersistence(repos_config)
        repos_interactor  = ReposInteractor(persistence=repos_persistence, builder=ReposBuilder(), remotes=remotes_interactor)

        return Interactor(repos_interactor, remotes_interactor)

class Interactor:
    def __init__(self, repos_interactor, remotes_interactor):
        self.remotes_interactor = remotes_interactor
        self.repos_interactor = repos_interactor

    def as_dict(self):
        return self.repos_interactor.as_dict()

    def __str__(self):
        return json.dumps(self.as_dict(), indent=2)

    def save(self):
        self.repos_interactor.save()
        self.remotes_interactor.save()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.save()

    ###
    # General
    ###

    class RepoNotFoundError(Exception):
        pass

    class CategoryNotFoundError(Exception):
        pass

    ###
    # Categories
    ###

    def categories_list(self):
        return self.repos_interactor.by("categories").keys()

    def categories_show(self, categories):
        ans = dict()
        for category in categories:
            ans[category] = [r.name for r in self.repos_interactor.by("categories").get(category, [])]
        return ans

    def categories_add(self, project, category):
        if project not in self.repos_interactor:
            raise(self.RepoNotFoundError(project))
        repo_cats = list(self.repos_interactor[project].categories)
        repo_cats.append(category)
        repo_cats = list(set(repo_cats))
        with self.repos_interactor:
            self.repos_interactor.edit(project, categories=repo_cats)

    def categories_remove(self, project, category):
        if project not in self.repos_interactor:
            raise(self.RepoNotFoundError(project))
        repo_cats = list(self.repos_interactor[project].categories)
        if category not in repo_cats:
            raise self.CategoryNotFoundError(category)
        repo_cats.remove(category)
        repo_cats = list(set(repo_cats))
        with self.repos_interactor:
            self.repos_interactor.edit(project, categories=repo_cats)

