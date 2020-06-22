from mgit.remotes.remotes_builder import RemotesBuilder
from test.test_util import TestPersistence

import unittest
from unittest import mock

class TestRemotesBuilder(unittest.TestCase):

    def setUp(self):
        self.persistence = TestPersistence({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                },
            "test2" : {
                "name" : "test2",
                "url" : "test2@example.com",
                "path" : "/test2/path",
                "type" : "ssh",
                "is_default" : True
                }
            })

    def test_success(self):
        remotes = RemotesBuilder().build(self.persistence.read_all())
        self.assertIn("test", remotes)
        self.assertIn("test2", remotes)

    def test_missing_name(self):
        self.persistence.set_all({
            "test" : {
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesBuilder.InvalidConfigError):
            RemotesBuilder().build(self.persistence.read_all())

    def test_missing_url(self):
        self.persistence.set_all({
            "test" : {
                "name" : "test",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesBuilder.InvalidConfigError):
            RemotesBuilder().build(self.persistence.read_all())

    def test_missing_path(self):
        self.persistence.set_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesBuilder.InvalidConfigError):
            RemotesBuilder().build(self.persistence.read_all())

    def test_non_int_port(self):
        self.persistence.set_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "port" : "hello",
                "is_default" : False
                }
            })
        with self.assertRaises(RemotesBuilder.InvalidConfigError):
            RemotesBuilder().build(self.persistence.read_all())

    def test_non_bool_default(self):
        self.persistence.set_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : "Not True"
                }
            })
        with self.assertRaises(RemotesBuilder.InvalidConfigError):
            RemotesBuilder().build(self.persistence.read_all())

    def test_unknown_type(self):
        self.persistence.set_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "what even is this type",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesBuilder.InvalidConfigError):
            RemotesBuilder().build(self.persistence.read_all())

    def test_different_name(self):
        self.persistence.set_all({
            "test" : {
                "name" : "test_different_name",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(RemotesBuilder.InvalidConfigError):
            RemotesBuilder().build(self.persistence.read_all())

