from mgit.persistence.remotes_config_persistence import RemotesConfigFilePersistence
from mgit.remotes.remotes_builder                import RemotesBuilder
from mgit.remotes.remotes_interactor             import RemotesInteractor

from mgit.repos.repos_builder     import ReposBuilder

from mgit.persistence.repo_config_persistence    import ReposConfigFilePersistence



import json

class Builder:
    def build(self, repos_config, remotes_config):
        remotes_persistence = RemotesConfigFilePersistence(remotes_config)
        remotes_interactor = RemotesInteractor(persistence=remotes_persistence, builder=RemotesBuilder())

        repo_data = ReposConfigFilePersistence(repos_config).read_all()
        repos = ReposBuilder().build(repo_data=repo_data, remotes=remotes_interactor.remotes)

        return Interactor(repos, remotes_interactor)

class Interactor:
    def __init__(self, repos, remotes_interactor):
        self.remotes_interactor = remotes_interactor
        self.repos = repos

    def as_dict(self):
        return {k : v.as_dict() for k, v in self.repos.items()}

    def __str__(self):
        return json.dumps(self.as_dict(), indent=2)
