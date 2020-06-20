from mgit.interactors.general_interactor import GeneralInteractor

class RemotesInteractor(GeneralInteractor):
    def __init__(self, persistence, builder):
        self.persistence = persistence
        self.builder = builder
        self.build_items()

