from mgit.state import RepoState, NamedRemoteRepo, Remote, RemoteType, UnnamedRemoteRepo
from mgit.config import Config

from parameterized import parameterized

from pathlib import Path

import shutil
import unittest

class TestConfigState(unittest.TestCase):

    def files_for_test(self, look_like_this):
        """
        [Example]
        repo_id = some_id
        path = some_path
        origin = home
        categories = school
        home-repo = some_repi
        archived = 1
        parent = some_other_section
        ignore = 1

        [test_repo_1]
        repo_id = abc123
        path = /tmp/mgit/acceptance/local/test_repo_1
        origin = test_remote_1
        categories = category1    category2
        test_remote_1-repo = test_repo_1
        test_remote_2-repo = test_repo_1
        name = test_repo_1

        [test_repo_2]
        path = /tmp/mgit/acceptance/local/test_repo_2
        origin = test_remote_1
        categories = category2
        test_remote_1-repo = test_repo_2
        name = test_repo_2

        [test_repo_3]
        path = test_repo_3
        parent = test_repo_2
        origin = test_remote_1
        categories = category2
        test_remote_1-repo = test_repo_3
        name = test_repo_3

        [test_repo_5]
        path = test_repo_5
        parent = test_repo_3
        origin = test_remote_1
        categories = category2
        test_remote_1-repo = test_repo_5
        name = test_repo_5

        [test_repo_6]
        path = /tmp/mgit/acceptance/local/test_repo_6
        origin = test_remote_2
        test_remote_2-repo = test_repo_6
        archived=1
        name = test_repo_6
        """

    def setUp(self):
        self.repos_config           = "./test/__files__/test_repos_acceptance.ini"
        self.remotes_config         = "./test/__files__/test_remote_acceptance.ini"

        self.default_repos_config   = "./test/__files__/test_repos_acceptance_default.ini"
        self.default_remotes_config = "./test/__files__/test_remote_acceptance_default.ini"

        self.c = Config(
                self.remotes_config,
                self.repos_config
                )

    def tearDown(self):
        self.reset_configs()

    def reset_configs(self):
        shutil.copy(self.default_remotes_config, self.remotes_config)
        shutil.copy(self.default_repos_config, self.repos_config)

    def test_get_by_id(self):
        ans = self.c.get_state(repo_id="abc123")
        self.assertIsInstance(ans, RepoState)

        self.assertEqual(
                "abc123",
                ans.repo_id
                )

        self.assertEqual(
                "test_repo_1",
                ans.name
                )

        self.assertEqual(
                Path("/tmp/mgit/acceptance/local/test_repo_1"),
                ans.path
                )

    def test_get_state_parent(self):
        ans = self.c.get_state(name="test_repo_3")

        self.assertIsInstance(
                ans.parent,
                RepoState
                )

        self.assertEqual(
                ans.parent.name,
                "test_repo_2"
                )

    def test_get_by_name(self):
        ans = self.c.get_state(name="test_repo_1")
        self.assertIsInstance(ans, RepoState)

        self.assertEqual(
                "abc123",
                ans.repo_id
                )

        self.assertEqual(
                "test_repo_1",
                ans.name
                )

        self.assertEqual(
                Path("/tmp/mgit/acceptance/local/test_repo_1"),
                ans.path
                )

    def test_get_state_remotes(self):
        ans = self.c.get_state(name="test_repo_1")
        self.assertIsInstance(ans, RepoState)

        r1 = Remote(
                "test_remote_1",
                "",
                "/tmp/mgit/acceptance/test_remote_1/",
                RemoteType.LOCAL
                )
        r2 = Remote(
                "test_remote_2",
                "",
                "/tmp/mgit/acceptance/test_remote_2/",
                RemoteType.LOCAL
                )

        self.assertIn(
                NamedRemoteRepo(r1, project_name="test_repo_1"),
                ans.remotes
                )
        self.assertIn(
                NamedRemoteRepo(r2, project_name="test_repo_1"),
                ans.remotes)

    def test_get_state_origin(self):
        """
        ans = self.c.get_state(name="test_repo_1")
        self.assertIsInstance(ans, RepoState)

        r1 = Remote(
                "test_remote_1",
                "bloodyfool@127.0.0.1",
                "/tmp/mgit/acceptance/test_remote_1/",
                RemoteType.LOCAL
                )

        self.assertEqual(
                NamedRemoteRepo(r1, project_name="test_repo_1"),
                ans.origin
                )
        """

    def test_get_state_archived_false(self):
        ans = self.c.get_state(name="test_repo_1")
        self.assertIsInstance(ans, RepoState)

        self.assertEqual(
                False,
                ans.archived
                )

    def test_get_state_archived_true(self):
        ans = self.c.get_state(name="test_repo_6")
        self.assertIsInstance(ans, RepoState)

        self.assertEqual(
                True,
                ans.archived
                )

    def test_get_state_categories(self):
        ans = self.c.get_state(name="test_repo_1")
        self.assertIsInstance(ans, RepoState)

        self.assertEqual(
                {"category1", "category2"},
                ans.categories
                )

    def test_get_state_categories_empty(self):
        ans = self.c.get_state(name="test_repo_6")
        self.assertIsInstance(ans, RepoState)

        self.assertEqual(
                set(),
                ans.categories
                )

    def test_get_state_ignored(self):
        ans = self.c.get_state(name="Example")
        self.assertIsNone(ans)

    def test_get_state_by_path(self):
        ans = self.c.get_state( path="/tmp/mgit/acceptance/local/test_repo_2/test_repo_3")
        self.assertIsInstance(ans, RepoState)

    "Test writing"

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_set_state_invariance(self, name):
        "Tests writing and re-reading of a config"
        #get a repo
        ans = self.c.get_state(name=name)
        self.assertIsInstance(ans, RepoState)

        #mutate
        ans.archived = True
        ans.path /= Path("more")
        ans.repo_id = "asdf"
        ans.categories.add("shoop")

        # write to config and read again
        self.c.set_state(ans)
        self.c._read_configs()
        new = self.c.get_state(name=name)

        # written should be same as merged
        self.assertEqual(
                new,
                ans
                )

    @parameterized.expand([ "test_repo_3", "test_repo_5" ])
    def test_set_state_invariance_parent(self, name="test_repo_3"):
        "Tests writing and re-reading of a config"
        #get a repo
        ans = self.c.get_state(name=name)
        self.assertIsInstance(ans, RepoState)

        self.assertIsNotNone(ans.parent)

        #mutate
        ans.archived = True
        # ans.path /= "~/keking/smek"
        ans.repo_id = "asdf"
        ans.categories = set(["shoop"])
        ans.parent = None

        # write to config and read again
        self.c.set_state(ans)
        self.c._read_configs()
        new = self.c.get_state(name=name)

        self.assertEqual(
                new,
                ans
                )

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_remove_and_recreate_repo(self, name: str):
        before = self.c.get_state(name=name)
        self.c.remove_state(before)

        ans = self.c.get_state(name=name)
        self.assertIsNone(ans)

        self.c.set_state(before)

        new = self.c.get_state(name=name)
        self.assertEqual(
                new,
                before)

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_resolve_unnamed_remote(self, name:str="test_repo_1"):
        remote_repo = list(self.c.get_state(name=name).remotes)[0]

        self.assertIsInstance(remote_repo, NamedRemoteRepo)

        unnamed_remote = UnnamedRemoteRepo(
                url=remote_repo.get_url(),
                remote_name = remote_repo.get_name()
                )

        named = self.c.resolve_unnamed_remote(unnamed_remote)

        self.assertIsInstance(named, NamedRemoteRepo)

        self.assertEqual(named, remote_repo)

    @parameterized.expand([ "test_remote_1", "test_remote_2", ])
    def test_remove_and_recreate_remote(self, name: str):
        before = self.c.get_remote(name=name)
        self.c.remove_remote(before)

        ans = self.c.get_remote(name=name)
        self.assertIsNone(ans)

        self.c.set_remote(before)

        new = self.c.get_remote(name=name)
        self.assertEqual(
                new,
                before)

    def test_get_all_not_none(self):
        ans = self.c.get_all_repo_state()

        self.assertNotIn(None, ans)
