from test.test_interactor import TestInteractor

from test.test_util import File_var

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
                interactor.repos["example"].categories
                )

        interactor.categories_add("example", "config")

        self.assertEqual(
                ["config"],
                interactor.repos["example"].categories
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
                interactor.repos["example"].categories
                )

        interactor.categories_remove("example", "config")

        self.assertEqual(
                [],
                interactor.repos["example"].categories
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

