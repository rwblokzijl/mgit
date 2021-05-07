import mgit.ui.commands.rename # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestRenameCommand(MgitUnitTestBase):

    def test_rename(self):
        name="test_repo_1"
        new_name="new_name"

        # old name exists in config
        self.assertIsNotNone(self.config.get_state(name=name))
        # new name doesnt exist in config
        with self.assertRaises(self.config.ConfigError):
            self.config.get_state(name=new_name)

        self.run_command(f"rename {name} {new_name}")

        # old name doesnt exist in config
        with self.assertRaises(self.config.ConfigError):
            self.config.get_state(name=name)
        # new name exists in config
        self.assertIsNotNone(self.config.get_state(name=new_name))



