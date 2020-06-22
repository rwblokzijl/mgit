from mgit.interactors.general_interactor import GeneralInteractor

class ReposInteractor(GeneralInteractor):

    def __init__(self, persistence, builder, remotes):
        self.remotes = remotes
        self.maps    = {
                "repo_id" : {},
                "categories" : {},
                }

        super().__init__(persistence, builder)

    def build_items(self):
        self.entities = self.builder.build(self.persistence.read(), self.remotes)
