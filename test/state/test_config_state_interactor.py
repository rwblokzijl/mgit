from mgit.state.state import RepoState, NamedRemoteRepo, Remote, RemoteType
from mgit.state.config_state_interactor import ConfigStateInteractor

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
        self.c = ConfigStateInteractor(
                "test/__files__/test_remote_acceptance.ini",
                "test/__files__/test_repos_acceptance.ini"
                )

    def tearDown(self):
        pass

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
                "/tmp/mgit/acceptance/local/test_repo_1",
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
                "/tmp/mgit/acceptance/local/test_repo_1",
                ans.path
                )

    def test_get_state_remotes(self):
        ans = self.c.get_state(name="test_repo_1")
        self.assertIsInstance(ans, RepoState)

        r1 = Remote(
                "test_remote_1",
                "bloodyfool@127.0.0.1",
                "/tmp/mgit/acceptance/test_remote_1/",
                RemoteType.SSH
                )
        r2 = Remote(
                "test_remote_2",
                "bloodyfool@127.0.0.1",
                "/tmp/mgit/acceptance/test_remote_2/",
                RemoteType.SSH
                )

        self.assertIn(
                NamedRemoteRepo(r1, project_name="test_repo_1"),
                ans.remotes
                )
        self.assertIn(
                NamedRemoteRepo(r2, project_name="test_repo_1"),
                ans.remotes)

    def test_get_state_origin(self):
        ans = self.c.get_state(name="test_repo_1")
        self.assertIsInstance(ans, RepoState)

        r1 = Remote(
                "test_remote_1",
                "bloodyfool@127.0.0.1",
                "/tmp/mgit/acceptance/test_remote_1/",
                RemoteType.SSH
                )

        self.assertEqual(
                NamedRemoteRepo(r1, project_name="test_repo_1"),
                ans.origin
                )

        self.assertEqual(
                False,
                ans.archived
                )

    def test_get_state_archived(self):
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

