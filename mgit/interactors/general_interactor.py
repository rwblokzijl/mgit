
class GeneralInteractor:
    def __init__(self, persistence, builder):
        self.persistence = persistence
        self.builder = builder
        self.build()

    def build(self):
        self.build_items()
        self.generate_maps()

    def build_items(self):
        self.entities = self.builder.build(self.persistence.read())

    def get_items(self):
        return self.entities

    def __len__(self):
        return len(self.entities)

    def __getitem__(self, key):
        return self.entities[key]

    def by(self, property):
        if property not in self.maps:
            raise self.NonIdentifyablePropertyError(f"No mappings found for '{property}'")
        return self.maps[property]

    def __contains__(self, key):
        return key in self.entities

    def entities(self):
        return self.entities.items()

    def generate_maps(self):
        for map in self.maps:
            self.maps[map] = {}
            self.maps.pop("name", None)
        for entity in self.entities.values():
            self.add_to_maps(entity)
        self.maps["name"] = self.entities

    def add_to_maps(self, repo):
        for map in self.maps:
            self.add_to_map_property(map, repo)

    def add_to_map_property_item(self, property, key, value):
        name = getattr(value, "name", key)
        if key not in self.maps[property]:
            self.maps[property][key] = list()

        self.maps[property][key].append(value)

    def add_to_map_property(self, property, value):
        key = getattr(value, property, None)
        self.add_to_map_property_item(property, key, value)

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

    def get_by_property(self, property, value):
        if property not in self.maps:
            raise self.NonIdentifyablePropertyError(f"No mappings found for '{property}'")
        if value not in self.maps[property]:
            raise self.ItemDoesntExistError(f"No repo found with '{property}' '{value}'")

        return self.maps[property][value]


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

    class NonIdentifyablePropertyError(Exception):
        pass

