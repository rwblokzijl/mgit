import mgit.ui.commands.unarchive # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestUnarchiveCommand(MgitUnitTestBase):

    def test_unarchive(self):
        name="test_repo_6"

        old = self.config.get_state(name=name)
        self.assertEqual(
                True,
                old.archived
                )

        self.run_command(f"unarchive -n {name}")

        new = self.config.get_state(name=name)
        self.assertEqual(
                False,
                new.archived
                )

