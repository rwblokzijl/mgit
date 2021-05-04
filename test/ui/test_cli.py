from mgit.ui.cli               import CLI
from mgit.ui.cli               import AbstractLeafCommand, AbstractNodeCommand
from mgit.ui.commands._mgit    import MgitCommand

import unittest
from unittest.mock import Mock


@MgitCommand.register
class CommandParent(AbstractNodeCommand):
    command = "parent"
    def run(self, **args):
        return "parent_res"

@CommandParent.register
class CommandChild(AbstractLeafCommand):
    command = "child"
    def build(self, parser):
        pass

    def run(self, **args):
        return "child_res"

class TestCommands(unittest.TestCase):
    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_nested_same_name(self):
        command = MgitCommand(Mock(), Mock(), Mock())
        self.assertEqual(
                CLI(command).run("parent".split()),
                "parent_res"
                )

    def test_nested_nested_nested(self):
        command = MgitCommand(Mock(), Mock(), Mock())
        self.assertEqual(
                CLI(command).run("parent child".split()),
                "child_res"
                )

