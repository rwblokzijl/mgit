import os

import unittest
from unittest import mock

from mgit.persistence.remotes_config_persistence import RemotesConfigFilePersistence

class TestRemoteConfigPersistence(unittest.TestCase):

    """Testing remote behaviour"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        path = "test/__files__/test_remote.ini"
        remotes = RemotesConfigFilePersistence(path)
        self.assertEqual(remotes.configPath, os.path.abspath(path))

    def test_remembersFilePath(self):
        path = "test/__files__/test_remote.ini"
        remotes = RemotesConfigFilePersistence(path)
        self.assertEqual(remotes.configPath, os.path.abspath(path))

    def test_whenMissingFile_returnEmpty(self):
        path = "test/__files__/this_file_shouldnt_exist_please_delete.ini"
        remotes = RemotesConfigFilePersistence(path).read_all()
        self.assertDictEqual({}, remotes)

    def test_no_defaults(self):
        test_file = \
                "[test]\n" + \
                "url=test@example.com\n" + \
                "path=/test/path\n" + \
                "type=ssh"

        mock_open = mock.mock_open(read_data=test_file)
        with mock.patch("builtins.open", mock_open):
            remotes = RemotesConfigFilePersistence("test/path")

    def test_simpleRemoteIsLoaded(self):
        test_file = \
                "[test]\n" + \
                "url=test@example.com\n" + \
                "path=/test/path\n" + \
                "type=ssh"

        mock_open = mock.mock_open(read_data=test_file)
        with mock.patch("builtins.open", mock_open):
            remotes = RemotesConfigFilePersistence("test/path")
            self.assertIn("test", remotes.read_all())

    def test_read_all(self):
        "read_all should return a list of remote dicts"

        test_file = \
                "[defaults]\n" + \
                "test2=1\n" + \
                "\n" + \
                "[test]\n" + \
                "url=test@example.com\n" + \
                "path=/test/path\n" + \
                "type=ssh\n" + \
                "\n" + \
                "[test2]\n" + \
                "url=test2@example.com\n" + \
                "path=/test2/path\n" + \
                "type=test2"

        remotes_dict = {
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

        mock_open = mock.mock_open(read_data=test_file)
        with mock.patch("builtins.open", mock_open):
            remotes = RemotesConfigFilePersistence("test/path")
            self.assertDictEqual(remotes.read_all(), remotes_dict)

    def test_write_all(self):
        # setup
        expected = {
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
        test_file = "/tmp/mgit_test_file.ini"
        if os.path.isfile(test_file):
            os.remove(test_file)

        # execute test
        persistence = RemotesConfigFilePersistence(test_file)
        persistence.set("test", expected["test"])
        persistence.set("test2", expected["test2"])
        persistence.write_all()

        remotes_conf = RemotesConfigFilePersistence(test_file).read_all()

        #teardown
        if os.path.isfile(test_file):
            os.remove(test_file)

        #assert
        self.assertDictEqual(remotes_conf, expected)

