from mgit.interactors.general_persistence_interactor import GeneralPersistenceInteractor

class ReposCollection(GeneralPersistenceInteractor):

    def __init__(self, persistence, builder, remotes):
        self.remotes = remotes
        self.maps    = {
                "repo_id" : {},
                "categories" : {},
                "path" : {},
                }

        super().__init__(persistence, builder)

    def build_items(self):
        self.entities = self.builder.build(self.persistence.read(), self.remotes)

    def add_remotes_to_repo(self, name, remotes={}):
        kwargs = {}
        kwargs["name"]       = name
        kwargs.update({k + "-repo" : v for k, v in remotes.items()})
        self.edit(**kwargs)
        self.save()

    def add_new_repo(self, name, path, categories=[], remotes={}, archived=False, parent=None, repo_id=None, origin=None):
        kwargs = {}

        kwargs["name"]       = name
        kwargs["path"]       = path
        kwargs["categories"] = categories

        kwargs.update({k + "-repo" : v for k, v in remotes.items()})

        if parent:
            kwargs["parent"]     = parent
        if archived:
            kwargs["archived"]   = archived
        if repo_id:
            kwargs["repo_id"]    = repo_id
        if origin:
            kwargs["origin"]     = origin

        self.add(
                **kwargs
                )
        self.save()
