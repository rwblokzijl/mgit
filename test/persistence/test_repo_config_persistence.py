import os

import unittest
from unittest import mock

from mgit.persistence.repo_config_persistence import ReposConfigFilePersistence

class TestRepoConfigPersistence(unittest.TestCase):

    """Testing repo behaviour"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        path = "test/__files__/test_repos.ini"
        repos = ReposConfigFilePersistence(path)
        self.assertEqual(repos.configPath, os.path.abspath(path))

    def test_remembersFilePath(self):
        path = "test/__files__/test_repos.ini"
        repos = ReposConfigFilePersistence(path)
        self.assertEqual(repos.configPath, os.path.abspath(path))

    def test_whenMissingFile_TrowsException(self):
        path = "test/__files__/this_file_shouldnt_exist_please_delete.ini"
        with self.assertRaises(ReposConfigFilePersistence.FileNotFoundError):
            repos = ReposConfigFilePersistence(path).read_all()

    def test_simpleRepoIsLoaded(self):
        test_file = \
                "[example]\n" + \
                "path = example\n" + \
                "originurl = bloodyfool@git.bloodyfool.family\n" + \
                "originpath = /data/git/projects/example-name-in-origin\n" + \
                "origin = home\n" + \
                "categories = config\n" + \
                "ignore = 1\n" + \
                "home-repo = example-name-in-home\n" + \
                "ewi-gitlab-repo = different-example-name\n"

        mock_open = mock.mock_open(read_data=test_file)
        with mock.patch("builtins.open", mock_open):
            repos = ReposConfigFilePersistence("test/path")
            self.assertIn("example", repos.read_all())

    def test_read_all(self):
        "read_all should return a list of repo dicts"

        test_file = \
                "[example]\n" + \
                "path = example\n" + \
                "originurl = bloodyfool@git.bloodyfool.family\n" + \
                "originpath = /data/git/projects/example-name-in-origin\n" + \
                "origin = home\n" + \
                "categories = config\n" + \
                "ignore = 1\n" + \
                "home-repo = example-name-in-home\n" + \
                "ewi-gitlab-repo = different-example-name\n" + \
                "\n" + \
                "[example2]\n" + \
                "path = example2\n" + \
                "originurl = bloodyfool2@git.bloodyfool.family\n" + \
                "originpath = /data/git/projects2/example-name-in-origin\n" + \
                "origin = home\n" + \
                "categories = config\n" + \
                "ignore = 1\n" + \
                "home-repo = example-name-in-home\n" + \
                "ewi-gitlab-repo = different-example-name\n"

        repos_dict = {
                "example" : {
                    "name" : "example",
                    "path" : "example",
                    "originurl" : "bloodyfool@git.bloodyfool.family",
                    "originpath" : "/data/git/projects/example-name-in-origin",
                    "origin" : "home",
                    "categories" : "config",
                    "ignore" : "1",
                    "home-repo" : "example-name-in-home",
                    "ewi-gitlab-repo" : "different-example-name",
                    },
                "example2" : {
                    "name" : "example2",
                    "path" : "example2",
                    "originurl" : "bloodyfool2@git.bloodyfool.family",
                    "originpath" : "/data/git/projects2/example-name-in-origin",
                    "origin" : "home",
                    "categories" : "config",
                    "ignore" : "1",
                    "home-repo" : "example-name-in-home",
                    "ewi-gitlab-repo" : "different-example-name",
                    }
                }

        self.maxDiff = None
        mock_open = mock.mock_open(read_data=test_file)
        with mock.patch("builtins.open", mock_open):
            repos = ReposConfigFilePersistence("test/path")
            self.assertDictEqual(repos.read_all(), repos_dict)

    def test_write_all(self):
        # setup

        repos_dict = {
                "example" : {
                    "name" : "example",
                    "path" : "example",
                    "originurl" : "bloodyfool@git.bloodyfool.family",
                    "originpath" : "/data/git/projects/example-name-in-origin",
                    "origin" : "home",
                    "categories" : "config",
                    "ignore" : "1",
                    "home-repo" : "example-name-in-home",
                    "ewi-gitlab-repo" : "different-example-name",
                    },
                "example2" : {
                    "name" : "example2",
                    "path" : "example2",
                    "originurl" : "bloodyfool2@git.bloodyfool.family",
                    "originpath" : "/data/git/projects2/example-name-in-origin",
                    "origin" : "home",
                    "categories" : "config",
                    "ignore" : "1",
                    "home-repo" : "example-name-in-home",
                    "ewi-gitlab-repo" : "different-example-name",
                    }
                }

        test_file = "/tmp/mgit_test_file.ini"
        if os.path.isfile(test_file):
            os.remove(test_file)

        # execute test
        ReposConfigFilePersistence(test_file).write_all(repos_dict)
        repos_conf = ReposConfigFilePersistence(test_file).read_all()

        #teardown
        if os.path.isfile(test_file):
            os.remove(test_file)

        #assert
        self.assertDictEqual(repos_conf, repos_dict)
