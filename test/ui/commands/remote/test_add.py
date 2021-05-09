import mgit.ui.commands.remote.add # pylint: disable=W0611 #import important for decorators to run
import mgit.ui.commands.remote.list # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestRemoteAddCommand(MgitUnitTestBase):

    def test_remote_add(self):
        self.init_repos(["test_repo_2"])

        self.run_command("remote add -n test_repo_2 test_remote_2")

        #created in remote
        self.assertIn(
                "test_repo_2",
                self.run_command_raw("remote list test_remote_2")['test_remote_2']
                )
        # in config
        config = self.config.get_state(name="test_repo_2")
        config_remote, = [r for r in config.remotes if r.get_name() == 'test_remote_2']
        self.assertEqual(
                "test_repo_2",
                config_remote.project_name
                )
        # in system
        system = self.system.get_state(config.path)
        system_remote, = [r for r in system.remotes if r.get_name() == 'test_remote_2']
        self.assertEqual(
                system_remote.get_url(),
                config_remote.get_url()
                )

