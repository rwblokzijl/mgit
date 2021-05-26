import mgit.ui.commands.update # pylint: disable=W0611 #import important for decorators to run
from mgit.local.state import *

from test.test_util import MgitUnitTestBase

from parameterized import parameterized

class TestUpdateCommand(MgitUnitTestBase):

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_no_change(self, name="test_repo_1"):
        self.init_repos([name])

        before_config_state = self.config.get_state(name=name)
        before_system_state = self.system.get_state(path=before_config_state.path)

        self.run_command(f"update -ycs -n {name}")

        after_config_state = self.config.get_state(name=name)
        after_system_state = self.system.get_state(path=after_config_state.path)

        self.assertEqual(
                before_config_state,
                after_config_state
                )

        self.assertEqual(
                before_system_state,
                after_system_state
                )

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_change_system_only(self, name="test_repo_1"):
        self.init_repos([name])

        config_state = self.config.get_state(name=name)
        config_state.remotes.add(UnnamedRemoteRepo("new", "new"))
        self.config.set_state(config_state)

        before_config_state = self.config.get_state(name=name)
        before_system_state = self.system.get_state(path=before_config_state.path)

        self.run_command(f"update -ys -n {name}")

        after_config_state = self.config.get_state(name=name)
        after_system_state = self.system.get_state(path=after_config_state.path)

        self.assertEqual(
                before_config_state,
                after_config_state
                )

        self.assertNotEqual(
                before_system_state,
                after_system_state
                )

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_change_config_only(self, name="test_repo_1"):
        self.init_repos([name])

        before_config_state = self.config.get_state(name=name)
        before_config_state.remotes.pop()
        self.config.set_state(before_config_state)

        before_config_state = self.config.get_state(name=name)
        before_system_state = self.system.get_state(path=before_config_state.path)

        self.run_command(f"update -yc -n {name}")

        after_config_state = self.config.get_state(name=name)
        after_system_state = self.system.get_state(path=after_config_state.path)

        self.assertNotEqual(
                before_config_state,
                after_config_state
                )

        self.assertEqual(
                before_system_state,
                after_system_state
                )

