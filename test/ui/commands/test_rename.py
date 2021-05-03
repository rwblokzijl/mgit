from test.test_util import MgitUnitTestBase
from mgit.ui.commands.rename import CommandRename
import unittest

class TestRenameCommand(MgitUnitTestBase):

    def test_rename(self):
        name="test_repo_1"
        new_name="new_name"

        # old name exists in config
        self.assertIsNotNone(self.config.get_state(name=name))
        # new name doesnt exist in config
        self.assertIsNone(self.config.get_state(name=new_name))

        self.run_command(f"rename {name} {new_name}")

        # old name doesnt exist in config
        self.assertIsNone(self.config.get_state(name=name))
        # new name exists in config
        self.assertIsNotNone(self.config.get_state(name=new_name))



