from mgit.remotes.remote import Remote

import unittest

class TestRemote(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        Remote(name = "test",
                url = "test@example.com",
                path = "/test/path",
                remote_type = "ssh",
                port = "22",
                default = False,
                base_data = {},
                )

    def test_dict(self):
        remote_dict = {
            "name" : "test2",
            "url" : "test2@example.com",
            "path" : "/test2/path",
            "type" : "ssh",
            "port" : "22",
            "is_default" : True
            }
        remote = Remote(
                name = "test2",
                url = "test2@example.com",
                path = "/test2/path",
                remote_type = "ssh",
                port = "22",
                default = True,
                base_data = {},
                )
        self.assertDictEqual(remote.as_dict(), remote_dict)

    def test_get_name(self):
        remote = Remote(
                name = "test2",
                url = "test2@example.com",
                path = "/test2/path",
                remote_type = "ssh",
                port = "22",
                default = True,
                base_data = {},
                )
        get = remote.name
        self.assertEqual(get, "test2")

    def test_get_url(self):
        remote = Remote(
                name = "test2",
                url = "test2@example.com",
                path = "/test2/path",
                remote_type = "ssh",
                port = "22",
                default = True,
                base_data = {},
                )
        self.assertEqual(
                "test2@example.com:/test2/path",
                remote.get_url()
                )

    def test_get_url_empty(self):
        remote = Remote(
                name = "test2",
                url = "test2@example.com",
                path = "",
                remote_type = "ssh",
                port = "22",
                default = True,
                base_data = {},
                )
        self.assertEqual(
                "test2@example.com:",
                remote.get_url()
                )

