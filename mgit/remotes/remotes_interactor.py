
class RemotesInteractor:

    def __init__(self, persistence, builder):
        self.remotes = builder.build(persistence.read_all())

    def get_remotes(self):
        return self.remotes

    def add(self, remote):
        self.remotes[remote["name"]] = remote

    def save(self, persistence):
        writable = self.get_remotes_dict()
        persistence.write_all(writable)

    def get_remotes_dict(self):
        return { remote["name"]:remote.as_dict() for remote in self.remotes.values() }

