from mgit.repos.repos_interactor import ReposInteractor
from mgit.repos.repos_builder    import ReposBuilder
from mgit.repos.repos            import Repo

from test.test_util                  import TestPersistence

import unittest
from unittest.mock import MagicMock

class TestReposInteractor(unittest.TestCase):
    """Test case docstring."""

    def setUp(self):
        self.persistence = TestPersistence({
                "example" : {
                    "name" : "example",
                    "path" : "example",
                    "parent" : "example2",
                    "originurl" : "bloodyfool@git.bloodyfool.family:/direct_repo",
                    "origin" : "home",
                    "categories" : "config",
                    # "ignore" : "1",
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
                    "categories" : "config",
                    # "ignore" : "1",
                    "home-repo" : "example-name-in-home",
                    "github-repo" : "different-example-name",
                    "repo_id" : "1234567890f39a8a19a8364fbed2fa317112342",
                    "archived" : False,
                    }
                })
        self.repo_data = self.persistence.read_all()

        self.builder                           = ReposBuilder()

        self.remote                            = MagicMock()
        self.remote.get_url.return_value       = "~/test"

        self.remotes                           = MagicMock()
        self.remotes.__contains__.return_value = True
        self.remotes.__getitem__.return_value  = self.remote

    def tearDown(self):
        pass

    def test_init(self):
        repos = ReposInteractor(self.persistence, self.builder, self.remotes)

        self.assertIn("example", repos)
        self.assertIn("example2", repos)
        self.assertTrue(len(repos) == 2)

    def test_contains(self):
        repos = ReposInteractor(self.persistence, self.builder, self.remotes)
        self.assertIn("example2", repos)

    def test_get_repos(self):
        repos_interactor = ReposInteractor(self.persistence, self.builder, self.remotes)
        repos = self.builder.build(self.persistence.read_all(), self.remotes)

        gotten_data = repos_interactor.get_items()
        self.assertEqual(gotten_data.keys(), repos.keys())

    def test_add(self):
        repos = ReposInteractor(self.persistence, self.builder, self.remotes)

        self.assertNotIn("example3", repos)
        repos.add( **{
                    "name" : "example3",
                    "path" : "~/example2",
                    "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                    "origin" : "home",
                    "categories" : "config",
                    "home-repo" : "example-name-in-home",
                    "github-repo" : "different-example-name",
                    "repo_id" : "1234567890f39a8a19a8364fbed2fa317112343",
                    "archived" : False,
                    }
                )
        self.assertIn("example3", repos)

    def test_add_exists(self):
        repos = ReposInteractor(self.persistence, self.builder, self.remotes)
        with self.assertRaises(ReposInteractor.ItemExistsError):
            repos.add( **{
                "name" : "example2",
                "path" : "~/example2",
                "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                "origin" : "home",
                "categories" : "config",
                "home-repo" : "example-name-in-home",
                "github-repo" : "different-example-name",
                "repo_id" : "1234567890f39a8a19a8364fbed2fa317112341",
                "archived" : False,
                })

    def test_edit(self):
        repos = ReposInteractor(self.persistence, self.builder, self.remotes)

        self.assertIn("example2", repos)
        self.assertEqual("1234567890f39a8a19a8364fbed2fa317112342", repos["example2"].repo_id)
        repos.edit( **{
            "name" : "example2",
            "path" : "~/example2",
            "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
            "origin" : "home",
            "categories" : "config",
            "home-repo" : "example-name-in-home",
            "github-repo" : "different-example-name",
            "repo_id" : "1234567890f39a8a19a8364fbed2fa317112341",
            "archived" : False,
            })
        self.assertEqual("1234567890f39a8a19a8364fbed2fa317112341", repos["example2"].repo_id)

    def test_edit_not_exists(self):
        repos = ReposInteractor(self.persistence, self.builder, self.remotes)
        self.assertNotIn("example3", repos)
        with self.assertRaises(ReposInteractor.ItemExistsError):
            repos.edit( **{
                "name" : "example3",
                "path" : "~/example2",
                "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                "origin" : "home",
                "categories" : "config",
                "home-repo" : "example-name-in-home",
                "github-repo" : "different-example-name",
                "repo_id" : "1234567890f39a8a19a8364fbed2fa317112341",
                "archived" : False,
                })

    def test_save(self):
        repos = ReposInteractor(self.persistence, self.builder, self.remotes)

        self.assertNotIn("example3", repos)
        repos.add( **{
            "name" : "example3",
            "path" : "~/example2",
            "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
            "origin" : "home",
            "categories" : "config",
            "home-repo" : "example-name-in-home",
            "github-repo" : "different-example-name",
            "repo_id" : "1234567890f39a8a19a8364fbed2fa317112341",
            "archived" : False,
            })
        repos.save()
        self.assertIn("example3", self.persistence.read_all())

    def test_edit_not_save(self):
        repos = ReposInteractor(self.persistence, self.builder, self.remotes)

        self.assertNotIn("example3", repos)
        repos.add( **{
            "name" : "example3",
            "path" : "~/example2",
            "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
            "origin" : "home",
            "categories" : "config",
            "home-repo" : "example-name-in-home",
            "github-repo" : "different-example-name",
            "repo_id" : "1234567890f39a8a19a8364fbed2fa317112341",
            "archived" : False,
            })
        self.assertNotIn("example3", self.persistence.read_all())

    def test_context_manager(self):
        with ReposInteractor(self.persistence, self.builder, self.remotes) as repos:
            self.assertNotIn("example3", repos)
            repos.add( **{
                "name" : "example3",
                "path" : "~/example2",
                "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                "origin" : "home",
                "categories" : "config",
                "home-repo" : "example-name-in-home",
                "github-repo" : "different-example-name",
                "repo_id" : "1234567890f39a8a19a8364fbed2fa317112341",
                "archived" : False,
                })
        self.assertIn("example3", self.persistence.read_all())

    def test_afterEditAndSave_readBuildsSame(self):
        with ReposInteractor(self.persistence, self.builder, self.remotes) as repos:
            self.assertNotIn("example3", repos)
            repos.add( **{
                "name" : "example3",
                "path" : "~/example2",
                "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                "origin" : "home",
                "categories" : "config",
                "home-repo" : "example-name-in-home",
                "github-repo" : "different-example-name",
                "repo_id" : "1234567890f39a8a19a8364fbed2fa317112341",
                "archived" : False,
                })
            before = self.persistence.read()
        after = self.persistence.read_all()
        self.assertEqual(before, after)

    def test_afterSave_readBuildsSame(self):
        with ReposInteractor(self.persistence, self.builder, self.remotes) as repos:
            self.assertNotIn("example3", repos)
            before = self.persistence.read()
        after = self.persistence.read_all()
        self.assertEqual(before, after)

    def test_repo_id_map(self):
        with ReposInteractor(self.persistence, self.builder, self.remotes) as repos:
            self.assertEqual(
                    [repos["example2"]],
                    repos.by("repo_id")["1234567890f39a8a19a8364fbed2fa317112342"]
                    )
            self.assertEqual(
                    [repos["example"]],
                    repos.by("repo_id")["1234567890f39a8a19a8364fbed2fa317108abe6"]
                    )

    def test_repo_id_double(self):
        rid = "1234567890f39a8a19a8364fbed2fa317112342"
        self.repo_data["example"]["repo_id"] = rid
        with ReposInteractor(self.persistence, self.builder, self.remotes) as repos:
            q = repos.by("repo_id")[rid]
            self.assertIn( repos["example"], q )
            self.assertIn( repos["example2"], q )

    def test_repo_id_missing(self):
        with self.assertRaises(ReposInteractor.ItemDoesntExistError):
            with ReposInteractor(self.persistence, self.builder, self.remotes) as repos:
                repos.get_by_property("repo_id", "idk")

    def test_get_by_missing_property(self):
        with self.assertRaises(ReposInteractor.NonIdentifyablePropertyError):
            with ReposInteractor(self.persistence, self.builder, self.remotes) as repos:
                repos.get_by_property("jemoeder", "idk")
