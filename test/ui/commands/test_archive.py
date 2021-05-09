import mgit.ui.commands.archive # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestArchiveCommand(MgitUnitTestBase):

    def test_rename(self):
        name="test_repo_1"

        # old name exists in config
        old = self.config.get_state(name=name)
        self.assertEqual(
                False,
                old.archived
                )

        self.run_command(f"archive -n {name}")

        new = self.config.get_state(name=name)
        self.assertEqual(
                True,
                new.archived
                )

