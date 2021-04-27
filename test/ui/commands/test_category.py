from mgit.ui.cli          import CLI
from mgit.ui.commands.commands import MgitCommand

import unittest
from unittest.mock import Mock

class TestCategory(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        self.interactor=Mock()
        self.ui = CLI(command=MgitCommand(interactor=self.interactor))

    def tearDown(self):
        pass

    def test_category_list(self):
        args = "category list".split()
        self.ui.run(args)
        self.interactor.categories_list.assert_called_with()

    def test_category_show(self):
        args = "category show school config".split()
        self.ui.run(args)
        self.interactor.categories_show.assert_called_with(categories=["school", "config"])

    def test_category_add(self):
        args = "category add mgit school".split()
        self.ui.run(args)
        self.interactor.categories_add.assert_called_with(project='mgit', category='school')

    def test_category_remove(self):
        args = "category remove mgit school".split()
        self.ui.run(args)
        self.interactor.categories_remove.assert_called_with(project='mgit', category='school')

