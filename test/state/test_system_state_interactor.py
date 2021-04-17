from mgit.state.system_state_interactor import SystemStateInteractor

from mgit.state.state import RepoState, UnnamedRemoteRepo

from git import Repo

import unittest
import os
import shutil

class Test(unittest.TestCase):

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

    def rmdir(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def tearDownDirs(self):
        self.rmdir("/tmp/mgit_empty")
        self.rmdir("/tmp/mgit_notexist")
        self.rmdir("/tmp/mgit_notempty")
        self.rmdir("/tmp/mgit_is_git")
        self.rmdir("/tmp/mgit_dir_missing")

        self.rmdir("/tmp/mgit/unittest")

    def setUp(self):
        self.repo_dir = "~/devel/mgit"
        self.setUp_dirs()

    def tearDown(self):
        self.tearDownDirs()

    def test_get_state_type(self):
        ans = SystemStateInteractor().get_state(self.repo_dir)
        self.assertIsInstance(ans, RepoState)

    def test_get_state_remotes(self):
        ans = SystemStateInteractor().get_state(self.repo_dir)
        self.assertIn(
                UnnamedRemoteRepo("home", "bloodyfool@git.blokzijl.family:/data/git/projects/mgit"),
                ans.remotes
                )
        self.assertIn(
                UnnamedRemoteRepo("bagn", "bloodyfool@bagn.blokzijl.family:/data/git/projects/mgit"),
                ans.remotes)

    def test_get_id(self):
        ans = SystemStateInteractor().get_state(path=self.repo_dir)
        self.assertEqual(
                "9392e7789458d330301039232d2c72254c2aed3a",
                ans.repo_id
                )

    def test_non_exist(self):
        ans = SystemStateInteractor().get_state("/tmp/mgit_notexist")
        self.assertIsNone(ans)

    def test_parent(self):
        ans = SystemStateInteractor().get_state("~/school/thesis/4_implementation/gateway/backend/")
        self.assertEqual(
                "f428e4998a7d8084cb7d557807672aa2b0f5ece9",
                ans.repo_id
                )
        self.assertEqual(
                "9db32f8a599c68a0d49f7344acc60810e3ebe218",
                ans.parent.repo_id
                )

