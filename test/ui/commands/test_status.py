import mgit.ui.commands.status # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase
import pygit2

class TestStatusCommand(MgitUnitTestBase):


    def test_status(self):

        self.init_repos([ 'test_repo_1', 'test_repo_2', ])
        self.init_repos([ 'test_repo_6', ], commit=True)

        self.make_dirty(['test_repo_1', 'test_repo_6'])

        ans = self.run_command_raw("status -cdul /tmp/mgit")

        self.assertEqual(
                ans,
                2)

    def test_local_repo_status(self):
        pass

