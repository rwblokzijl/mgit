from mgit.interactor import Builder
from mgit.interactor import Interactor

from mgit.remotes.remotes_builder                import RemotesBuilder
from mgit.remotes.remotes_interactor             import RemotesInteractor

from mgit.repos.repos_builder                 import ReposBuilder
from mgit.repos.repos_interactor              import ReposInteractor

from test.test_util import TestPersistence, File_var

import unittest

class TestInteractor(unittest.TestCase):

    """Test case docstring."""

    def get_file_test_interactor(self):
        return Builder().build(
                repos_config="test/__files__/test_repos.ini",
                remotes_config="test/__files__/test_remote.ini"
                )

    def get_memory_test_interactor(self, repo_con=None, remotes_con=None,
            remote_persistence_file=None, repo_persistence_file=None):
        self.remotes_data =  {
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "port" : "22",
                "is_default" : False,
                },
            "test2" : {
                "name" : "test2",
                "url" : "test2@example.com",
                "path" : "/test2/path",
                "type" : "ssh",
                "port" : "22",
                "is_default" : True
                }
            }
        remotes_persistence = TestPersistence(remotes_con or self.remotes_data, remote_persistence_file)
        remotes_interactor = RemotesInteractor(persistence=remotes_persistence, builder=RemotesBuilder())

        self.repos_data = {
            "example" : {
                "name" : "example",
                "path" : "example",
                "parent" : "example2",
                "origin" : "test",
                "categories" : ["config"],
                "test-repo" : "example-name-in-home",
                "test2-repo" : "different-example-name",
                "repo_id" : "1234567890f39a8a19a8364fbed2fa317108abe6",
                "archived" : True,
                },
            "example2" : {
                "name" : "example2",
                "path" : "~/example2",
                "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                "categories" : ["school"],
                "test-repo" : "example-name-in-test",
                "test2-repo" : "different-example-name",
                "repo_id" : "1234567890f39a8a19a8364fbed2fa317112342",
                "archived" : False,
                }
            }
        repos_persistence = TestPersistence(repo_con or self.repos_data, repo_persistence_file)
        repos_interactor  = ReposInteractor(persistence=repos_persistence, builder=ReposBuilder(), remotes=remotes_interactor)

        return Interactor(repos_interactor, remotes_interactor)

class TestInteractorGeneral(TestInteractor):

    def test_show(self):
        interactor = self.get_file_test_interactor()
        self.assertIn(
                "ti2316",
                interactor.as_dict()
                )

    def test_show_path(self):
        interactor = self.get_file_test_interactor()
        self.assertEqual(
                "~/.config/dotfiles",
                interactor.as_dict()["dotfiles"]["path"]
                )

class TestCategoryInteractions(TestInteractor):

    """Testing Categories commands"""

    ###
    # categories
    ###

    def test_category_list(self):
        interactor = self.get_file_test_interactor()
        self.assertEqual(
                sorted(["school","config", "devel"]),
                sorted(interactor.categories_list())
                )

    def test_category_show_one(self):
        interactor = self.get_file_test_interactor()
        self.maxDiff = None
        self.assertDictEqual(
                {"devel" : ['mlaundry', 'mgit']},
                interactor.categories_show(["devel"])
                )

    def test_category_show_two(self):
        interactor = self.get_file_test_interactor()
        self.maxDiff = None
        expected = {
            "devel" : ['mlaundry', 'mgit'],
            'config': ['backgrounds', 'dotfiles', 'config-mgit']
            }

        # run
        show = interactor.categories_show(["devel", "config"])

        #keys equal
        self.assertEqual(
                sorted(expected.keys()),
                sorted(show.keys())
                )

        for key in expected.keys():
            self.assertEqual(
                    sorted(expected[key]),
                    sorted(show[key])
                    )

    def test_category_show_missing(self):
        interactor = self.get_file_test_interactor()
        self.maxDiff = None
        expected = {
            "devel" : ['mlaundry', 'mgit'],
            'config': ['backgrounds', 'dotfiles', 'config-mgit'],
            'missing_category': []
            }

        # run
        show = interactor.categories_show(["devel", "config", "missing_category"])

        #keys equal
        self.assertEqual(
                sorted(expected.keys()),
                sorted(show.keys())
                )

        # vals equal
        for key in expected.keys():
            self.assertEqual(
                    sorted(expected[key]),
                    sorted(show[key])
                    )

    def test_category_add(self):
        repo_f = File_var()
        remote_f = File_var()
        interactor = self.get_memory_test_interactor(remote_persistence_file=remote_f, repo_persistence_file=repo_f)

        show = interactor.categories_show(["config"])["config"]
        self.assertEqual(
                ["example"],
                show
                )

        interactor.categories_add("example2", "config")

        show = interactor.categories_show(["config"])["config"]
        self.assertEqual(
                sorted(["example", "example2"]),
                show
                )

    def test_category_add_existing(self):
        repo_f = File_var()
        remote_f = File_var()
        interactor = self.get_memory_test_interactor(remote_persistence_file=remote_f, repo_persistence_file=repo_f)

        self.assertEqual(
                ["config"],
                interactor.repos_interactor["example"].categories
                )

        interactor.categories_add("example", "config")

        self.assertEqual(
                ["config"],
                interactor.repos_interactor["example"].categories
                )

    def test_category_add_missing_repo(self):
        repo_f = File_var()
        remote_f = File_var()
        interactor = self.get_memory_test_interactor(remote_persistence_file=remote_f, repo_persistence_file=repo_f)

        with self.assertRaises(interactor.RepoNotFoundError):
            interactor.categories_add("example3", "config")

    def test_category_remove(self):
        repo_f = File_var()
        remote_f = File_var()
        interactor = self.get_memory_test_interactor(remote_persistence_file=remote_f, repo_persistence_file=repo_f)

        self.assertEqual(
                ["config"],
                interactor.repos_interactor["example"].categories
                )

        interactor.categories_remove("example", "config")

        self.assertEqual(
                [],
                interactor.repos_interactor["example"].categories
                )

    def test_category_remove_missing_repo(self):
        repo_f = File_var()
        remote_f = File_var()
        interactor = self.get_memory_test_interactor(remote_persistence_file=remote_f, repo_persistence_file=repo_f)

        with self.assertRaises(interactor.RepoNotFoundError):
            interactor.categories_remove("example3", "config")

    def test_category_remove_missing_category(self):
        repo_f = File_var()
        remote_f = File_var()
        interactor = self.get_memory_test_interactor(remote_persistence_file=remote_f, repo_persistence_file=repo_f)

        with self.assertRaises(interactor.CategoryNotFoundError):
            interactor.categories_remove("example", "shoop")
