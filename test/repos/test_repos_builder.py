from mgit.repos.repos_builder import ReposBuilder

from test.test_util import TestPersistence

import unittest
from unittest.mock import Mock

class TestReposBuilder(unittest.TestCase):

    def setUp(self):
        self.example_dict = {
                "example" : {
                    "name" : "example",
                    "path" : "example",
                    "parent" : "example2",
                    "originurl" : "bloodyfool@git.bloodyfool.family:/direct_repo",
                    "origin" : "home",
                    "categories" : ["config"],
                    "home-repo" : "example-name-in-home",
                    "github-repo" : "different-example-name",
                    "repo_id" : "1234567890f39a8a19a8364fbed2fa317108abe6",
                    "archived" : True,
                    },
                "example2" : {
                    "name" : "example2",
                    "path" : "~/example2",
                    "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                    "origin" : "home",
                    "categories" : ["config"],
                    "home-repo" : "example-name-in-home",
                    "github-repo" : "different-example-name",
                    "repo_id" : "1234567890f39a8a19a8364fbed2fa317112341",
                    "archived" : False,
                    }
                }
        self.persistence = TestPersistence(self.example_dict)
        homeMock = Mock()
        homeMock.get_url.return_value = "bloodyfool@git.bloodyfool.family:"
        githubMock = Mock()
        githubMock.get_url.return_value = "git@github.com:Bloodyfool/"
        self.test_remotes = {
                "home" : homeMock,
                "github" : githubMock
                }

    def test_success(self):
        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)
        self.assertIn("example", repos)
        self.assertIn("example2", repos)

        self.assertEqual(repos["example"].name, "example")
        self.assertEqual(repos["example"].path, "~/example2/example")
        self.assertEqual(repos["example"].parent , repos["example2"])
        self.assertEqual(repos["example"].origin , repos["example"].remotes["home"])
        self.assertEqual(repos["example"].categories , ["config"])
        self.assertEqual(repos["example"].remotes["home"].repo_name, "example-name-in-home")
        self.assertEqual(repos["example"].remotes["github"].repo_name, "different-example-name")
        self.assertEqual(repos["example"].repo_id , "1234567890f39a8a19a8364fbed2fa317108abe6")
        self.assertEqual(repos["example"].archived , True)

    def test_different_name(self):
        self.persistence.set_all({
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
        self.persistence.set_all(self.example_dict)

        with self.assertRaises(ReposBuilder.InvalidConfigError):
            ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_missing_path(self):
        del(self.example_dict["example"]["path"])
        self.persistence.set_all(self.example_dict)

        with self.assertRaises(ReposBuilder.InvalidConfigError):
            ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_categories(self):
        self.example_dict["example"]["categories"] = ["test1", "test2", "123"]
        self.persistence.set_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        for cat in ["test1", "test2", "123"]:
            self.assertIn(cat, ans["example"].categories)

    def test_remotes(self):
        self.persistence.set_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertSetEqual(
                set(["home", "github"]),
                set(ans["example"].remotes.keys())
                )

    def test_remote_content(self):
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
        with self.assertRaises(ReposBuilder.MissingRemoteReferenceError):
            ReposBuilder().build(self.persistence.read_all())

    def test_missing_archived_resolves_to_false(self):
        del(self.example_dict["example"]["archived"])
        self.persistence.set_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].archived , False)

    def test_missing_repo_id(self):
        del(self.example_dict["example"]["repo_id"])
        self.persistence.set_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].repo_id , None)

    def test_archived_false(self):
        self.example_dict["example"]["archived"] = False
        self.persistence.set_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].archived , False)

    def test_archived_zero(self):
        self.example_dict["example"]["archived"] = 0
        self.persistence.set_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].archived , False)

    def test_archived_one(self):
        self.example_dict["example"]["archived"] = 1
        self.persistence.set_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].archived , True)

    def test_archived_true(self):
        self.example_dict["example"]["archived"] = True
        self.persistence.set_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].archived , True)

    def test_archived_text(self):
        self.example_dict["example"]["archived"] = "sdf"
        self.persistence.set_all(self.example_dict)

        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].archived , True)

    def test_origin_ref(self):
        del(self.example_dict["example"]["originurl"])
        self.persistence.set_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(
                "bloodyfool@git.bloodyfool.family:example-name-in-home",
                ans["example"].origin.get_url()
                )

    def test_originurl(self):
        del(self.example_dict["example"]["origin"])
        self.persistence.set_all(self.example_dict)

        ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(
                "bloodyfool@git.bloodyfool.family:/direct_repo",
                ans["example"].origin.get_url()
                )

    def test_missing_origin_ref_error(self):
        del(self.example_dict["example"]["originurl"])
        del(self.example_dict["example"]["home-repo"])
        self.persistence.set_all(self.example_dict)

        with self.assertRaises(ReposBuilder.MissingOriginReferenceError):
            ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    @unittest.skip("this behaviour will added later in the top level")
    def test_missing_origin_error(self):
        del(self.example_dict["example"]["originurl"])
        del(self.example_dict["example"]["origin"])
        self.persistence.set_all(self.example_dict)

        with self.assertRaises(ReposBuilder.MissingOriginError):
            ans = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_origin_over_originurl(self):
        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].origin , repos["example"].remotes["home"])

    def test_parent_link(self):
        self.persistence.set_all(self.example_dict)
        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].parent , repos["example2"])

    def test_path_including_parent(self):
        self.example_dict["example2"]["path"] = "~/hoopla"
        self.example_dict["example"]["path"] = "shoop"
        self.persistence.set_all(self.example_dict)
        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertEqual(repos["example"].path, "~/hoopla/shoop")

    def test_child_with_absolute_path(self):
        self.example_dict["example"]["path"] = "~/shoop"
        self.persistence.set_all(self.example_dict)

        with self.assertRaises(ReposBuilder.PathError):
            ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_no_parent_while_relative_path(self):
        self.example_dict["example2"]["path"] = "shoop"
        self.persistence.set_all(self.example_dict)

        with self.assertRaises(ReposBuilder.PathError):
            ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

    def test_children(self):
        repos = ReposBuilder().build(self.persistence.read_all(), self.test_remotes)

        self.assertIn(repos["example"], repos["example2"].children)

