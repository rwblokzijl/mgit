from mgit.system_addons.local_system import LocalSystem
import shutil
from git import Repo

import unittest
import os

class TestLocalSystemInteractions(unittest.TestCase):

    """Test case docstring."""

    def setUp_dirs(self):
        repo = "/tmp/mgit_is_git/"
        os.makedirs(repo, exist_ok=True)
        Repo.init(repo)

        os.makedirs("/tmp/mgit_empty", exist_ok=True)
        self.rmdir("/tmp/mgit_notexist")

        filepath = "/tmp/mgit_notempty"
        os.makedirs(filepath, exist_ok=True)
        open(filepath+"/file1", 'a').close()
        open(filepath+"/file2", 'a').close()
        self.assertTrue(self.local_system.path_available("/tmp/mgit_notempty"))

    def rmdir(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def tearDownDirs(self):
        self.rmdir("/tmp/mgit_empty")
        self.rmdir("/tmp/mgit_notexist")
        self.rmdir("/tmp/mgit_notempty")
        self.rmdir("/tmp/mgit_is_git")
        self.rmdir("/tmp/mgit_dir_missing")

    def setUp(self):
        self.local_system = LocalSystem()
        self.setUp_dirs()

    def tearDown(self):
        self.tearDownDirs()

    def test_path_available(self):
        testfile = "/tmp/mgit_tests/"
        self.assertTrue(self.local_system.path_available("/tmp/mgit_empty"))
        self.assertTrue(self.local_system.path_available("/tmp/mgit_notexist"))
        self.assertTrue(self.local_system.path_available("/tmp/mgit_notempty"))
        self.assertFalse(self.local_system.path_available("/tmp/mgit_is_git"))

    def test_init_dir_exist(self):
        path = "/tmp/mgit_empty"
        self.assertTrue(self.local_system.path_available(path))
        self.local_system.init(path)
        self.assertFalse(self.local_system.path_available(path))

    def test_init_dir_missing(self):
        path = "/tmp/mgit_dir_missing"
        self.assertFalse(os.path.isdir(path))
        self.assertTrue(self.local_system.path_available(path))
        self.local_system.init(path)
        self.assertFalse(self.local_system.path_available(path))

    def test_init_dir_conaining_files(self):
        path = "/tmp/mgit_notempty"
        self.assertTrue(os.path.isdir(path))
        self.assertTrue(self.local_system.path_available(path))
        self.local_system.init(path)
        self.assertFalse(self.local_system.path_available(path))

    def test_with_remote(self):
        path = "/tmp/mgit_dir_missing"
        self.assertFalse(os.path.isdir(path))
        self.assertTrue(self.local_system.path_available(path))

        remotes = {"r1":"u1", "r2":"u2"}
        self.local_system.init(path, remotes=remotes)

        self.assertFalse(self.local_system.path_available(path))
        repo = Repo(path)
        self.assertDictEqual(
                { r.name : r.url for r in repo.remotes },
                remotes
                )

        self.assertFalse(self.local_system.path_available(path))

    def test_with_origin(self):
        path = "/tmp/mgit_dir_missing"
        self.assertFalse(os.path.isdir(path))
        self.assertTrue(self.local_system.path_available(path))

        origin="r1"
        remotes = {"r1":"u1", "r2":"u2"}
        self.local_system.init(path, origin=origin, remotes=remotes)

        self.assertFalse(self.local_system.path_available(path))
        repo = Repo(path)
        self.assertDictEqual(
                { r.name : r.url for r in repo.remotes },
                {"r1":"u1", "r2":"u2", "origin":"u1"}
                )

        self.assertFalse(self.local_system.path_available(path))

    def test_with_invalid_origin(self):
        path = "/tmp/mgit_dir_missing"
        self.assertFalse(os.path.isdir(path))
        self.assertTrue(self.local_system.path_available(path))

        origin="r3"
        remotes = {"r1":"u1", "r2":"u2"}
        with self.assertRaises(LocalSystem.MissingRemoteError):
            self.local_system.init(path, origin=origin, remotes=remotes)

        self.assertTrue(self.local_system.path_available(path))
