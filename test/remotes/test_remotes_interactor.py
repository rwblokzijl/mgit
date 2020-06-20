from mgit.remotes.remotes_interactor import RemotesInteractor
from mgit.remotes.remotes_builder    import RemotesBuilder
from mgit.remotes.remote             import Remote

from test.test_util                  import TestPersistence

import unittest

class TestRemotesInteractor(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        self.persistence = TestPersistence({
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
        remotes = RemotesInteractor(self.persistence, self.builder)

        self.assertIn("test", remotes)
        self.assertIn("test2", remotes)
        self.assertTrue(len(remotes) == 2)

    def test_contains(self):
        remotes = RemotesInteractor(self.persistence, self.builder)
        self.assertIn("test2", remotes)

    def test_get_remotes(self):
        remotes_interactor = RemotesInteractor(self.persistence, self.builder)
        remotes = self.builder.build(self.persistence.read_all())

        gotten_data = remotes_interactor.get_items()
        self.assertEqual(gotten_data.keys(), remotes.keys())

    def test_add(self):
        remotes = RemotesInteractor(self.persistence, self.builder)

        self.assertNotIn("test3", remotes)
        remotes.add(
                name = "test3",
                url = "test3@example.com",
                path = "/test3/path",
                remote_type = "github",
                port = "24",
                default = True
                )
        self.assertIn("test3", remotes)

    def test_add_exists(self):
        remotes = RemotesInteractor(self.persistence, self.builder)
        with self.assertRaises(RemotesInteractor.ItemExistsError):
            remotes.add(
                    name = "test2",
                    url = "test3@example.com",
                    path = "/test3/path",
                    remote_type = "github",
                    port = "24",
                    default = True
                    )

    def test_edit(self):
        remotes = RemotesInteractor(self.persistence, self.builder)

        self.assertIn("test2", remotes)
        self.assertEqual("test2@example.com", remotes["test2"].url)
        remotes.edit(
                name = "test2",
                url = "test3@example.com",
                path = "/test3/path",
                remote_type = "github",
                port = "24",
                default = True
                )
        self.assertEqual("test3@example.com", remotes["test2"].url)

    def test_edit_not_exists(self):
        remotes = RemotesInteractor(self.persistence, self.builder)
        self.assertNotIn("test3", remotes)
        with self.assertRaises(RemotesInteractor.ItemExistsError):
            remotes.edit(
                    name = "test3",
                    url = "test3@example.com",
                    path = "/test3/path",
                    remote_type = "github",
                    port = "24",
                    default = True
                    )

    def test_save(self):
        remotes = RemotesInteractor(self.persistence, self.builder)

        self.assertNotIn("test3", remotes)
        remotes.add(
                name = "test3",
                url = "test3@example.com",
                path = "/test3/path",
                remote_type = "github",
                port = "24",
                default = True
                )
        remotes.save()
        self.assertIn("test3", self.persistence.read_all())

    def test_edit_not_save(self):
        remotes = RemotesInteractor(self.persistence, self.builder)

        self.assertNotIn("test3", remotes)
        remotes.add(
                name = "test3",
                url = "test3@example.com",
                path = "/test3/path",
                remote_type = "github",
                port = "24",
                default = True
                )
        self.assertNotIn("test3", self.persistence.read_all())

    def test_context_manager(self):
        with RemotesInteractor(self.persistence, self.builder) as remotes:
            self.assertNotIn("test3", remotes)
            remotes.add(
                    name = "test3",
                    url = "test3@example.com",
                    path = "/test3/path",
                    remote_type = "github",
                    port = "24",
                    default = True
                    )
        self.assertIn("test3", self.persistence.read_all())

    def test_afterEditAndSave_readBuildsSame(self):
        with RemotesInteractor(self.persistence, self.builder) as remotes:
            self.assertNotIn("test3", remotes)
            remotes.add(
                    name = "test3",
                    url = "test3@example.com",
                    path = "/test3/path",
                    remote_type = "github",
                    port = "24",
                    default = True
                    )
            before = self.persistence.read()
        after = self.persistence.read_all()
        self.assertEqual(before, after)

    def test_afterSave_readBuildsSame(self):
        with RemotesInteractor(self.persistence, self.builder) as remotes:
            self.assertNotIn("test3", remotes)
            before = self.persistence.read()
        after = self.persistence.read_all()
        self.assertEqual(before, after)


