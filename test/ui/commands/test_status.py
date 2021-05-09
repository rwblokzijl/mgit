import mgit.ui.commands.status # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestStatusCommand(MgitUnitTestBase):


    def test_status(self):

        # TODO: test better

        self.init_repos([ 'test_repo_1', 'test_repo_2', 'test_repo_6', ])
        # self.make_dirty()

        ans = self.run_command_raw("status -cdul /tmp/mgit")

        self.assertEqual(
                ans,
                0)

    def test_local_repo_status(self):
        pass

