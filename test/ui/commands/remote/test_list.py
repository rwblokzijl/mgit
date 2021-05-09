import mgit.ui.commands.remote.list # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestRemoteListCommand(MgitUnitTestBase):

    def test_remote_list(self):
        self.run_command_raw("remote list test_remote_1")

