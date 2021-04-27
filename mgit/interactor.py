from mgit.persistence.remotes_config_persistence import RemotesConfigFilePersistence
from mgit.remotes.remotes_builder                import RemotesBuilder
from mgit.remotes.remotes_collection             import RemotesCollection

from mgit.persistence.repo_config_persistence import ReposConfigFilePersistence
from mgit.repos.repos_builder                 import ReposBuilder
from mgit.repos.repos_collection              import ReposCollection

from mgit.interactors.remote_mgit_interactor      import RemoteInteractor
from mgit.interactors.single_repo_mgit_interactor import SingleRepoInteractor
from mgit.interactors.multi_repo_mgit_interactor  import MultiRepoInteractor

from mgit.system_addons.local_system import LocalSystem

class Builder:
    """
    The builder takes all the dependencies and injects the into the Mgit interactor, if the persistence or system
    interactors every have to change, the interactor doesn't have to know about it
    """
    def build(self, repos_config, remotes_config):
        remotes_persistence = RemotesConfigFilePersistence(remotes_config)
        remotes             = RemotesCollection(persistence=remotes_persistence, builder=RemotesBuilder())

        repos_persistence = ReposConfigFilePersistence(repos_config)
        repos             = ReposCollection(persistence=repos_persistence, builder=ReposBuilder(), remotes=remotes)

        local_system_interactor = LocalSystem()

        return MgitInteractor(repos, remotes, local_system_interactor)

class MgitInteractor(
        RemoteInteractor,
        SingleRepoInteractor,
        MultiRepoInteractor,
        ):
    "The business logic is contained in several smaller interactors, just to keep the files at a managable size"
    pass

