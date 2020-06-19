from mgit.remotes.remote import Remote

import unittest

class TestRemote(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        Remote({
            "name" : "test",
            "url" : "test@example.com",
            "path" : "/test/path",
            "type" : "ssh",
            "port" : "22",
            "is_default" : False,
            })

    def test_dict(self):
        remote_dict = {
            "name" : "test2",
            "url" : "test2@example.com",
            "path" : "/test2/path",
            "type" : "ssh",
            "port" : "22",
            "is_default" : True
            }
        remote = Remote(remote_dict)
        self.assertDictEqual(remote_dict, remote_dict)

    def test_get_name(self):
        remote_dict = {
            "name" : "test2",
            "url" : "test2@example.com",
            "path" : "/test2/path",
            "type" : "ssh",
            "port" : "22",
            "is_default" : True
            }
        remote = Remote(remote_dict)
        get = remote["name"]
        loc = remote_dict["name"]
        self.assertEqual(get, loc)

    def test_get_url(self):
        remote_dict = {
            "name" : "test2",
            "url" : "test2@example.com",
            "path" : "/test2/path",
            "type" : "ssh",
            "port" : "22",
            "is_default" : True
            }
        remote = Remote(remote_dict)
        self.assertEqual(
                "test2@example.com:/test2/path",
                remote.get_url()
                )

    def test_get_url_empty(self):
        remote_dict = {
            "name" : "test2",
            "url" : "test2@example.com",
            "path" : "",
            "type" : "ssh",
            "port" : "22",
            "is_default" : True
            }
        remote = Remote(remote_dict)
        self.assertEqual(
                "test2@example.com:",
                remote.get_url()
                )

