from mgit.local.system import System

from mgit.local.state import RepoState, UnnamedRemoteRepo

# from git import Repo
import pygit2

from pygit2 import Repository

from pathlib import Path

import unittest
import os
import shutil

class TestSystemState(unittest.TestCase):

    """Test case docstring."""

    def create_git_repo_with_commit(self):
        os.makedirs(self.repo_with_commit, exist_ok=True)
        repo = pygit2.init_repository(self.repo_with_commit)
        relative_file_path = Path("file.txt")
        full_file_path = self.repo_with_commit / relative_file_path
        full_file_path.touch()
        repo.index.add(relative_file_path)
        repo.index.write()
        repo.create_commit(
            "HEAD",                  # reference_name
            repo.default_signature,  # author
            repo.default_signature,  # committer
            "Message",               # message
            repo.index.write_tree(), # tree
            [] # initial commit      # parents
        )

    def setUp_dirs(self):
        self.unittest_path: Path = Path("/tmp/mgit/")
        os.makedirs(self.unittest_path, exist_ok=True)
        #1
        self.repo_with_commit = Path("/tmp/mgit/with_commit")
        self.create_git_repo_with_commit()

        ##2
        #os.makedirs("/tmp/mgit_empty", exist_ok=True)
        ##3
        #self.rmdir("/tmp/mgit_notexist")

        ##4
        #filepath = "/tmp/mgit_notempty"
        #os.makedirs(filepath, exist_ok=True)
        #open(filepath+"/file1", 'a').close()
        #open(filepath+"/file2", 'a').close()

    def rmdir(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def tearDownDirs(self):
        self.rmdir(self.unittest_path)

        self.rmdir("/tmp/mgit_empty")
        self.rmdir("/tmp/mgit_notexist")
        self.rmdir("/tmp/mgit_notempty")
        self.rmdir("/tmp/mgit_is_git")
        self.rmdir("/tmp/mgit_dir_missing")

    def setUp(self):
        self.repo_dir = Path(Repository(os.path.abspath(__file__)).workdir) #use this very git repo to test
        self.setUp_dirs()

    def tearDown(self):
        self.tearDownDirs()

    def test_get_state_type(self):
        ans = System().get_state(self.repo_dir)
        self.assertIsInstance(ans, RepoState)

    def test_get_state_remotes(self):
        ans = System().get_state(self.repo_dir)
        self.assertIn(
                UnnamedRemoteRepo("home", "bloodyfool@git.blokzijl.family:/data/git/projects/mgit"),
                ans.remotes
                )
        self.assertIn(
                UnnamedRemoteRepo("parents", "bloodyfool@parents.blokzijl.family:/data/git/projects/mgit"),
                ans.remotes)

    def test_get_id(self):
        ans = System().get_state(path=self.repo_dir)
        self.assertEqual(
                "9392e7789458d330301039232d2c72254c2aed3a",
                ans.repo_id
                )

    def test_non_exist(self):
        with self.assertRaises(System.SystemError):
            System().get_state(Path("/tmp/mgit_notexist"))

    def test_parent(self):
        ans = System().get_state(Path("~/school/thesis/4_implementation/gateway/backend/"))
        self.assertEqual(
                "f428e4998a7d8084cb7d557807672aa2b0f5ece9",
                ans.repo_id
                )
        self.assertEqual(
                "9db32f8a599c68a0d49f7344acc60810e3ebe218",
                ans.parent.repo_id
                )

    def test_get_state(self):
        ans = System().get_state(path=self.repo_with_commit)
        self.assertIsNotNone(ans.repo_id)

    # Writing

    def test_write_clone(self) -> None:
        path = self.unittest_path / Path("test_1")

        origin = System().get_state(path=self.repo_with_commit)

        self.assertIsNotNone(origin)

        if not origin:
            return

        repo_state = RepoState(
                source        = "repo",
                repo_id       = origin.repo_id,
                path          = path,
                remotes       = {
                    UnnamedRemoteRepo(remote_name="remote_1", url=str(self.repo_with_commit)),
                    UnnamedRemoteRepo(remote_name="remote_2", url=str(self.repo_with_commit))
                    },
                parent        = None,

                #unknown
                name          = None,
                auto_commands = None,
                archived      = None,
                tags    = None
                )

        with self.assertRaises(System.SystemError):
            System().get_state(path)

        System().set_state(repo_state)

        ans = System().get_state(path)

        self.assertEqual(
                ans,
                repo_state)

    def test_write_init(self) -> None:
        path = self.unittest_path / Path("test_2")

        repo_state = RepoState(
                source        = "repo",
                repo_id       = None,
                path          = path,
                remotes       = set(),
                parent        = None,

                #unknown
                name          = None,
                auto_commands = None,
                archived      = None,
                tags    = None
                )

        with self.assertRaises(System.SystemError):
            System().get_state(path)

        System().set_state(repo_state)

        ans = System().get_state(path)

        self.assertEqual(
                ans,
                repo_state)

    def test_remove_remotes(self):
        path = self.unittest_path / Path("test_1")

        origin = System().get_state(path=self.repo_with_commit)

        self.assertIsNotNone(origin)

        if not origin:
            return

        repo_state = RepoState(
                source        = "repo",
                repo_id       = origin.repo_id,
                path          = path,
                remotes       = {
                    UnnamedRemoteRepo(remote_name="remote_1", url=str(self.repo_with_commit)),
                    UnnamedRemoteRepo(remote_name="remote_2", url=str(self.repo_with_commit))
                    },
                parent        = None,

                #unknown
                name          = None,
                auto_commands = None,
                archived      = None,
                tags    = None
                )

        System().set_state(repo_state)
        ans = System().get_state(path)
        self.assertEqual(
                ans,
                repo_state)

        repo_state.remotes.pop()
        repo_state.remotes.pop()

        System().set_state(repo_state)
        ans = System().get_state(path)
        self.assertEqual(
                ans.remotes,
                repo_state.remotes)
        self.assertEqual(
                ans,
                repo_state)

