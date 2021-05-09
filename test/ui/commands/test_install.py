import mgit.ui.commands.install # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

from parameterized import parameterized

class TestInstallCommand(MgitUnitTestBase):

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_install(self, name):
        config = self.config.get_state(name=name)

        self.init_remotes_for_test_repos([name])

        path=config.path

        # not exists in system
        with self.assertRaises(self.system.SystemError):
            self.system.get_state(path=path)

        self.run_command(f"install -y -n {name}")

        # exists in system
        self.assertIsNotNone(self.system.get_state(path=path))

    def test_install_from_remote(self):
        config = self.config.get_state(name="test_repo_1")

        remote1, remote2 = list(config.remotes)

        self.remote_system.init_repo(remote1)

        # force install from non-existant remote raises
        with self.assertRaises(self.remote_system.RemoteError):
            self.run_command(f"install -y -n test_repo_1 --remote {remote2.remote.name}")

        # not exists in system
        with self.assertRaises(self.system.SystemError):
            self.system.get_state(path=config.path)

        # force install from existant remote succeeds
        self.run_command(f"install -y -n test_repo_1 --remote {remote1.remote.name}")

        # exists in system
        self.assertIsNotNone(
                self.system.get_state(path=config.path)
                )

