from mgit.remotes import RemotesCreator

import unittest
from unittest import mock

class TestRemotesCreator(unittest.TestCase):

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
                        "type" : "test2",
                        "is_default" : True
                        }
                    }

        def read_all(self):
            return self.persistence

        def write_all(self, data):
            self.persistence = data

    def setUp(self):
        self.persistence = self.TestPersistence()

    def test_ignore(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                "ignore" : 1
                },
            "test2" : {
                "name" : "test2",
                "url" : "test2@example.com",
                "path" : "/test2/path",
                "type" : "ssh",
                "is_default" : True
                }
            })

        remotes = RemotesCreator(self.persistence)
        self.assertNotIn("test", remotes)
        self.assertIn("test2", remotes)

    def test_missing_name(self):
        self.persistence.write_all({
            "test" : {
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesCreator.InvalidConfigError):
            RemotesCreator(self.persistence)

    def test_missing_url(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesCreator.InvalidConfigError):
            RemotesCreator(self.persistence)

    def test_missing_path(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesCreator.InvalidConfigError):
            RemotesCreator(self.persistence)

    def test_non_int_port(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "port" : "hello",
                "is_default" : False
                }
            })
        with self.assertRaises(RemotesCreator.InvalidConfigError):
            RemotesCreator(self.persistence)

    def test_non_bool_default(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : "Not True"
                }
            })
        with self.assertRaises(RemotesCreator.InvalidConfigError):
            RemotesCreator(self.persistence)

    def test_unknown_type(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "what even is this type",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesCreator.InvalidConfigError):
            RemotesCreator(self.persistence)

    def test_different_name(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test_different_name",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesCreator.InvalidConfigError):
            RemotesCreator(self.persistence)

    def test_add_remote(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test_different_name",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                }
            })
    #         with RemotesCreator("fakeTestPath") as remotes:
    #             remotes.add(
    #                     name="test2",
    #                     url="test@example.com:/kek/in/bek",
    #                     type="ssh",
    #                     is_default=False)
    #             self.assertIn("test2", remotes)

    #         print(mock_open)
            # with Remotes("fakeTestPath") as remotes:
            #     self.assertIn("test2", remotes)



