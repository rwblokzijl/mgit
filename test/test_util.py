
class TestPersistence:
    def __init__(self):
        self.persistence = {
                "test" : {
                    "name" : "test",
                    "url" : "test@example.com",
                    "path" : "/test/path",
                    "type" : "ssh",
                    "is_default" : False
                    },
                "test2" : {
                    "name" : "test2",
                    "url" : "test2@example.com",
                    "path" : "/test2/path",
                    "type" : "github",
                    "is_default" : True
                    }
                }

    def read_all(self):
        return self.persistence

    def write_all(self, data):
        self.persistence = data

