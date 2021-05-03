import mgit.ui.commands.show #import important for decorators to run
from test.test_util import MgitUnitTestBase

from dataclasses import replace

from mgit.state import NamedRemoteRepo, Remote

class TestShowCommand(MgitUnitTestBase):

    def test_show_missing_all(self):
        name = "test_repo_1"

        ans = self.run_command_raw(f"show -a")

        self.assertIn(
                name,
                ans['missing']
                )

    def test_show_installed_all(self):
        name = "test_repo_1"
        self.init_repos([name])

        ans = self.run_command_raw(f"show -a")

        self.assertIn(
                name,
                ans['installed']
                )

    def test_show_conflicting_all(self):
        name = "test_repo_1"

        # init from config
        self.init_repos([name])

        # change config
        config, = self.get_repo_states([name])

        original: NamedRemoteRepo = list(config.remotes)[0]
        changed: NamedRemoteRepo = replace(original, remote=replace(original.remote, name="new_name"))

        config.remotes.discard(original)
        config.remotes.add(changed)

        self.config.set_state(config)

        # check if mismatch is caught

        ans = self.run_command_raw(f"show -a")


        self.assertIn(
                name,
                ans['conficting']
                )

    def test_show_missing(self):
        name = "test_repo_1"

        ans = self.run_command_raw(f"show -vv {name}")

        self.assertIn( "test_repo_1", ans)

    def test_show_installed(self):
        name = "test_repo_1"
        self.init_repos([name])

        ans = self.run_command_raw(f"show {name}")

        self.assertIn( "test_repo_1", ans)

    def test_show_conflicting(self):
        name = "test_repo_1"

        # init from config
        self.init_repos([name])

        # change config
        config, = self.get_repo_states([name])

        original: NamedRemoteRepo = list(config.remotes)[0]
        changed: NamedRemoteRepo = replace(original, remote=replace(original.remote, name="new_name"))

        config.remotes.discard(original)
        config.remotes.add(changed)

        self.config.set_state(config)

        # check if mismatch is caught

        ans = self.run_command(f"show -vv {name}")

        self.assertIn( "Unnamed", ans[0])
