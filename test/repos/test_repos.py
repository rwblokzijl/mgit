from mgit.repos.repos import ReposBuilder
from mgit.repos.repos import Repo
from mgit.repos.repos import DerivedRepoRemote
from mgit.repos.repos import UnnamedRepoOrigin
from test.test_util import TestPersistence

import unittest
from unittest.mock import Mock

class TestReposBuilder(unittest.TestCase):

    def setUp(self):
        self.persistence = TestPersistence()
        self.example_dict = {
                "example" : {
                    "name" : "example",
                    "path" : "example",
                    "originurl" : "bloodyfool@git.bloodyfool.family:/direct_repo",
                    "origin" : "home",
                    "categories" : "config",
                    # "ignore" : "1",
                    "home-repo" : "example-name-in-home",
                    "github-repo" : "different-example-name",
                    },
                "example2" : {
                    "name" : "example2",
                    "path" : "example2",
                    "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                    "origin" : "home",
                    "categories" : "config",
                    # "ignore" : "1",
                    "home-repo" : "example-name-in-home",
                    "github-repo" : "different-example-name",
                    }
                }
        homeMock = Mock()
        homeMock.get_url.return_value = "bloodyfool@git.bloodyfool.family:"
        githubMock = Mock()
        githubMock.get_url.return_value = "git@github.com:Bloodyfool/"
        self.test_remotes = {
                "home" : homeMock,
                "github" : githubMock
                }

    def test_success(self):
        self.persistence.write_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)
        self.assertIn("example", repos)
        self.assertIn("example2", repos)

    def test_ignore(self):
        self.example_dict["example"]["ignore"] = 1
        self.persistence.write_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)
        self.assertNotIn("example", repos)
        self.assertIn("example2", repos)

    def test_different_name(self):
        self.persistence.write_all({
            "test" : {
                "name" : "test_different_name",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "is_default" : False,
                }
            })
        with self.assertRaises(ReposBuilder.InvalidConfigError):
            ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_missing_name(self):
        del(self.example_dict["example"]["name"])
        self.persistence.write_all(self.example_dict)

        with self.assertRaises(ReposBuilder.InvalidConfigError):
            ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_missing_path(self):
        del(self.example_dict["example"]["path"])
        self.persistence.write_all(self.example_dict)

        with self.assertRaises(ReposBuilder.InvalidConfigError):
            ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_categories(self):
        self.example_dict["example"]["categories"] = "test1 test2 123"
        self.persistence.write_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        for cat in ["test1", "test2", "123"]:
            self.assertIn(cat, ans["example"].categories)

    def test_remotes(self):
        self.persistence.write_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertSetEqual(
                set(["home", "github"]),
                set(ans["example"].remotes.keys())
                )

    def test_remote_content(self):
        self.persistence.write_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(
                "bloodyfool@git.bloodyfool.family:example-name-in-home",
                ans["example"].remotes["home"].get_url()
                )
        self.assertEqual(
                "git@github.com:Bloodyfool/different-example-name",
                ans["example"].remotes["github"].get_url()
                )

    def test_missing_remotes_error(self):
        self.persistence.write_all(self.example_dict)

        with self.assertRaises(ReposBuilder.MissingRemoteReferenceError):
            ans = ReposBuilder().build(self.persistence.read_all())

    def test_origin_ref(self):
        del(self.example_dict["example"]["originurl"])
        self.persistence.write_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(
                "bloodyfool@git.bloodyfool.family:example-name-in-home",
                ans["example"].origin.get_url()
                )

    def test_originurl(self):
        del(self.example_dict["example"]["origin"])
        self.persistence.write_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(
                "bloodyfool@git.bloodyfool.family:/direct_repo",
                ans["example"].origin.get_url()
                )

    def test_missing_origin_ref_error(self):
        del(self.example_dict["example"]["originurl"])
        del(self.example_dict["example"]["home-repo"])
        self.persistence.write_all(self.example_dict)

        with self.assertRaises(ReposBuilder.MissingOriginReferenceError):
            ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_missing_origin_error(self):
        del(self.example_dict["example"]["originurl"])
        del(self.example_dict["example"]["origin"])
        self.persistence.write_all(self.example_dict)

        with self.assertRaises(ReposBuilder.MissingOriginError):
            ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

class TestRepo(unittest.TestCase):

    def test_init(self):
        Repo( "name", "path", "origin", "categories", "remotes" )

class TestDerivedRepoRemote(unittest.TestCase):

    def setUp(self):
        self.remote_mock = Mock()
        self.remote_mock.get_url.return_value = "bloodyfool@git.bloodyfool.family"
        self.drr = DerivedRepoRemote(self.remote_mock, "repo")

    def test_init(self):
        DerivedRepoRemote(Mock(), "repo")

    def test_get_url(self):
        self.remote_mock.get_url.return_value = "remote"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        url = drr.get_url()

        self.assertEqual("remote/repo", url)

    def test_get_relative_url(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        url = drr.get_url()

        self.assertEqual("bloodyfool@git.blokzijl.family:repo", url)

    def test_get_absolute_url(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:"
        drr = DerivedRepoRemote(self.remote_mock, "/repo")
        url = drr.get_url()

        self.assertEqual("bloodyfool@git.blokzijl.family:/repo", url)

    def test_get_relative_to_relative_url(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:/test/kek"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        url = drr.get_url()

        self.assertEqual("bloodyfool@git.blokzijl.family:/test/kek/repo", url)

    def test_get_relative_to_relative_url_trailing(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:/test/kek/"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        url = drr.get_url()

        self.assertEqual("bloodyfool@git.blokzijl.family:/test/kek/repo", url)

    def test_get_relative_to_relative_url_trailing(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:/test/kek/"
        drr = DerivedRepoRemote(self.remote_mock, "/repo")
        with self.assertRaises(DerivedRepoRemote.InvalidPathError):
            url = drr.get_url()

class TestUnnamedRepoOrigin(unittest.TestCase):

    def test_init(self):
        UnnamedRepoOrigin("urlll")

    def test_get_url(self):
        url = "urlll"
        self.assertEqual(
                url,
                UnnamedRepoOrigin(url).get_url()
                )

        url = "urlll2"
        self.assertEqual(
                url,
                UnnamedRepoOrigin(url).get_url()
                )
