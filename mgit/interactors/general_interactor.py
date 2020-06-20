
class GeneralInteractor:
    def __init__(self, persistence, builder):
        self.persistence = persistence
        self.builder = builder
        self.build_items()

    def build_items(self):
        self.entities = self.builder.build(self.persistence.read())

    def get_items(self):
        return self.entities

    def __len__(self):
        return len(self.entities)

    def __getitem__(self, key):
        return self.entities[key]

    def __contains__(self, key):
        return key in self.entities

    def entities(self):
        return self.entities.items()

    def add(self, name, **kwargs):
        if name not in self.persistence:
            kwargs["name"] = name
            self.persistence.set(name, kwargs)
            self.build_items()
        else:
            raise self.ItemExistsError(f"Item '{name}' exists already")

    def edit(self, name, **kwargs):
        if name in self.persistence:
            kwargs["name"] = name
            self.persistence.set(name, kwargs)
            self.build_items()
        else:
            raise self.ItemExistsError(f"Item '{name}' doesn't exist")

    def as_dict(self):
        return {k:v.as_dict() for k, v in self.entities.items()}

    def save(self):
        self.persistence.write_all()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.save()

    def __str__(self):
        return str(self.as_dict())

    class ItemDoesntExistError(Exception):
        pass

    class ItemExistsError(Exception):
        pass

