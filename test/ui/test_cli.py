from mgit.ui.cli               import CLI
from mgit.ui.cli               import AbstractLeafCommand, AbstractNodeCommand
from mgit.ui.commands.commands import MgitCommand

import unittest
from unittest.mock import Mock

class CommandCategoryCategory(AbstractLeafCommand):
    command = "category"
    def build(self, parser):
        pass
    def run_command(self, args):
        return "test"

class CommandCategoryCategoryP(AbstractNodeCommand):
    command = "category"
    def get_sub_commands(self):
        return [
                CommandCategoryCategory()
                ]

class TestCommands(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_nested_same_name(self):
        command = MgitCommand()
        command.sub_commands["category"].sub_commands["category"] = CommandCategoryCategory()
        self.assertEqual(
                CLI(Mock(), command).run("category category".split()),
                "test"
                )

    def test_nested_nested_nested(self):
        command = MgitCommand()
        command.sub_commands["category"].sub_commands["category"] = CommandCategoryCategoryP()
        self.assertEqual(
                CLI(Mock(), command).run("category category category".split()),
                "test"
                )

