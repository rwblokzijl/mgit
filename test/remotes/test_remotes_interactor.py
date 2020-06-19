from mgit.remotes.remotes_interactor import RemotesInteractor
from mgit.remotes.remotes_builder    import RemotesBuilder
from mgit.remotes.remote             import Remote
from test.test_util          import TestPersistence

import unittest

class TestRemotesInteractor(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        self.persistence = TestPersistence()
        self.persistence.write_all({
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "port" : "22",
                "is_default" : False,
                },
            "test2" : {
                "name" : "test2",
                "url" : "test2@example.com",
                "path" : "/test2/path",
                "type" : "ssh",
                "port" : "22",
                "is_default" : True
                }
            })
        self.remote_data = self.persistence.read_all()

        self.builder     = RemotesBuilder()

    def tearDown(self):
        pass

    def test_init(self):
        ri = RemotesInteractor(self.persistence, self.builder)

        self.assertIn("test", ri.remotes)
        self.assertIn("test2", ri.remotes)
        self.assertTrue(len(ri.remotes) == 2)

    def test_get_remotes(self):
        ri = RemotesInteractor(self.persistence, self.builder)
        remotes = self.builder.build(self.persistence.read_all())

        gotten_data = ri.get_remotes()
        self.assertEqual(gotten_data.keys(), remotes.keys())

    def test_add(self):
        ri = RemotesInteractor(self.persistence, self.builder)
        remote = Remote({
            "name" : "test3",
            "url" : "test3@example.com",
            "path" : "/test3/path",
            "type" : "github",
            "port" : "24",
            "is_default" : True
            })

        self.assertNotIn("test3", ri.get_remotes())
        ri.add(remote)
        self.assertIn("test3", ri.get_remotes())

    def test_save(self):
        persistence = TestPersistence()
        remote = Remote({
            "name" : "test3",
            "url" : "test3@example.com",
            "path" : "/test3/path",
            "type" : "github",
            "port" : "24",
            "is_default" : True
            })
        ri = RemotesInteractor(persistence, self.builder)

        self.assertNotIn("test3", ri.get_remotes())
        ri.add(remote)
        self.assertIn("test3", ri.get_remotes())

        self.assertNotIn("test3", persistence.read_all())
        ri.save(persistence)
        self.assertIn("test3", persistence.read_all())

