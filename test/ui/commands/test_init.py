import mgit.ui.commands.init # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

from pathlib import Path

class TestInitCommand(MgitUnitTestBase):

    def test_init(self):
        name="test"
        path=Path("/tmp/mgit/kek")

        # doesnt exist in config
        self.assertIsNone(self.config.get_state(name=name))
        # doesnt exist in system
        self.assertIsNone(self.system.get_state(path=path))

        self.run_command(f"init -y {name} --path {path} --remotes")

        # exists in config
        self.assertIsNotNone(self.config.get_state(name=name))
        # exists in system
        self.assertIsNotNone(self.system.get_state(path=path))

    def test_init_explicit_remotes(self):
        name="test"
        path=Path("/tmp/mgit/kek")
        remotes="test_remote_1 test_remote_2:test_repo_name"

        self.run_command(f"init -y {name} --path {path} --remotes {remotes}")

        repo = self.config.get_state(name=name)
        remote1, remote2 = sorted(repo.remotes, key=lambda x: x.project_name)

        # Remote 1 instantiated
        self.assertIn(
                name,
                self.remote_system.list_remote(remote1.remote)
                )

        # Remote 2 instantiated
        self.assertIn(
                "test_repo_name",
                self.remote_system.list_remote(remote2.remote)
                )

    def test_init_implicit(self):
        "Tests that when --remotes is not specified, the defaults are used"
        name="test"
        path=Path("/tmp/mgit/kek")

        self.run_command(f"init -y {name} --path {path}")

        # init worked
        self.assertIsNotNone(
                self.config.get_state(name=name)
                )

        remote1, remote2 = sorted(
                self.config.get_all_remotes_from_config(),
                key=lambda x: x.name)

        # Remote 1 instantiated (default)
        self.assertIn(
                name,
                self.remote_system.list_remote(remote1)
                )

        # Remote 2 not instantiated
        self.assertNotIn(
                "test_repo_name",
                self.remote_system.list_remote(remote2)
                )

    def test_init_no_remotes(self):
        "Tests that when --remotes is specified without anything, no remotes are inited"
        name="test"
        path=Path("/tmp/mgit/kek")
        remotes=""

        self.run_command(f"init -y {name} --path {path} --remotes {remotes}")

        # init worked
        self.assertIsNotNone(
                self.config.get_state(name=name)
                )
        remote1, remote2 = sorted(
                self.config.get_all_remotes_from_config(),
                key=lambda x: x.name)

        # Remote 1 not instantiated
        self.assertNotIn(
                name,
                self.remote_system.list_remote(remote1)
                )

        # Remote 2 instantiated
        self.assertNotIn(
                "test_repo_name",
                self.remote_system.list_remote(remote2)
                )

