from mgit.interactors.general_interactor import GeneralInteractor

class RemotesInteractor(GeneralInteractor):
    def __init__(self, persistence, builder):
        self.maps = {
                "type" : {}
                }
        super().__init__(persistence, builder)

