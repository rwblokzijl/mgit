from mgit.interactor import Builder

import unittest

class TestInteractor(unittest.TestCase):

    """Test case docstring."""

    def test_init(self):
        Builder().build(
                repos_config="test/__files__/test_repos.ini",
                remotes_config="test/__files__/test_remote.ini"
                )

    def test_show(self):
        interactor = Builder().build(
                repos_config="test/__files__/test_repos.ini",
                remotes_config="test/__files__/test_remote.ini"
                )
        self.assertIn(
                "ti2316",
                interactor.as_dict()
                )

    def test_show_path(self):
        interactor = Builder().build(
                repos_config="test/__files__/test_repos.ini",
                remotes_config="test/__files__/test_remote.ini"
                )

        self.assertEqual(
                "~/.config/dotfiles",
                interactor.as_dict()["dotfiles"]["path"]
                )
