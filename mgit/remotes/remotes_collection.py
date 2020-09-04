from mgit.interactors.general_persistence_interactor import GeneralPersistenceInteractor

class RemotesCollection(GeneralPersistenceInteractor):
    def __init__(self, persistence, builder):
        self.maps = {
                "type" : {}
                }
        super().__init__(persistence, builder)

