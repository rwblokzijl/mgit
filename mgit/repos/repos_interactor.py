from mgit.interactors.general_interactor import GeneralInteractor

class ReposInteractor(GeneralInteractor):

    def __init__(self, persistence, builder, remotes):
        self.persistence = persistence
        self.builder = builder
        self.remotes = remotes
        self.build_items()

    def build_items(self):
        self.entities = self.builder.build(self.persistence.read(), self.remotes)

