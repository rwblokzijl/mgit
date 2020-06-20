
class RemotesInteractor:

    def __init__(self, persistence, builder):
        self.persistence = persistence
        self.builder = builder
        self.build_remotes()

    def build_remotes(self):
        self.remotes = self.builder.build(self.persistence.read())

    def get_remotes(self):
        return self.remotes

    def __contains__(self, key):
        return key in self.remotes

    def add(self, name, **kwargs):
        if name not in self.persistence:
            kwargs["name"] = name
            self.persistence.set(name, kwargs)
            self.build_remotes()
        else:
            raise self.RemoteExistsError(f"Remote '{name}' exists already")

    def edit(self, name, **kwargs):
        if name in self.persistence:
            kwargs["name"] = name
            self.persistence.set(name, kwargs)
            self.build_remotes()
        else:
            raise self.RemoteExistsError(f"Remote '{name}' doesn't exist")

    def save(self):
        self.persistence.write_all()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.save()

    class RemoteDoesntExistError(Exception):
        pass

    class RemoteExistsError(Exception):
        pass
