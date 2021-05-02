import mgit.ui.commands.install
from test.test_util import MgitUnitTestBase
from git import GitError

from parameterized import parameterized

import unittest

class TestInstallCommand(MgitUnitTestBase):

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_install(self, name):
        config = self.config_state_interactor.get_state(name=name)

        self.init_remotes_for_test_repos([name])

        path=config.path

        # not exists in system
        self.assertIsNone(self.system_state_interactor.get_state(path=path))

        self.run_command(f"install -y {name}")

        # exists in system
        self.assertIsNotNone(self.system_state_interactor.get_state(path=path))

    def test_install_from_remote(self):
        config = self.config_state_interactor.get_state(name="test_repo_1")

        remote1, remote2 = list(config.remotes)

        self.remote_interactor.init_repo(remote1)

        # force install from non-existant remote raises
        with self.assertRaises(self.remote_interactor.RemoteError):
            self.run_command(f"install -y test_repo_1 --remote {remote2.remote.name}")

        # not exists in system
        self.assertIsNone(
                self.system_state_interactor.get_state(path=config.path)
                )

        # force install from existant remote succeeds
        self.run_command(f"install -y test_repo_1 --remote {remote1.remote.name}")

        # exists in system
        self.assertIsNotNone(
                self.system_state_interactor.get_state(path=config.path)
                )

