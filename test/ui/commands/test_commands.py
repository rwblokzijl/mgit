from mgit.ui.cli               import CLI
from mgit.ui.commands.commands import MgitCommand

import unittest
from unittest.mock import Mock

class TestArgs(unittest.TestCase):
    """Test case docstring."""

    def setUp(self):
        self.interactor = Mock()
        command         = MgitCommand(self.interactor)
        self.ui         = CLI(command)

    def tearDown(self):
        pass

    def test_init(self):
        pass

