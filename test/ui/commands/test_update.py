import mgit.ui.commands.update # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestUpdateCommand(MgitUnitTestBase):

    def test_status(self):

        # TODO: test better

        self.init_repos(["test_repo_1"])

        ans = self.run_command_raw("update -n test_repo_1")

        # config_state = self.config.get_state("")
        # system_state = self.system.get_state("")

        # self.assertEqual(
        #         config_state,
        #         system_state
        #         )

