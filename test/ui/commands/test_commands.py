from mgit.ui.cli          import CLI
from mgit.ui.commands.commands import MgitCommand

import unittest
from unittest.mock import Mock

class TestArgs(unittest.TestCase):
    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        CLI(interactor=Mock(), command=MgitCommand())

    def test_config_called(self):
        interactor=Mock()
        ui = CLI(interactor=interactor, command=MgitCommand())
        args = "category list".split()
        self.assertEqual(
                ui.run(args),
                "list"
                )

    def test_category_called(self):
        interactor=Mock()
        ui = CLI(interactor=interactor, command=MgitCommand())
        args = "category show".split()
        self.assertEqual(
                ui.run(args),
                "show"
                )

