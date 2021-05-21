import mgit.ui.commands.update # pylint: disable=W0611 #import important for decorators to run
from mgit.ui.commands.update import CommandUpdate
from test.test_util import MgitUnitTestBase

from parameterized import parameterized

class TestUpdateCommand(MgitUnitTestBase):

    # # @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    # def test_no_change(self, name="test_repo_1"):

    #     # TODO: test better

    #     self.init_repos([name])

    #     # ans = self.run_command_raw(f"update -n {name}")

    #     config_state = self.config.get_state(name=name)
    #     system_state = self.system.get_state(path=config_state.path)

    #     self.assertEqual(
    #             config_state,
    #             system_state
    #             )

    def merge_test_setup(self, name):
        self.init_repos([name])

        config_state = self.config.get_state(name=name)
        system_state = self.system.get_state(path=config_state.path)

        self.commit_in_repo(system_state)
        system_state = self.system.get_state(path=config_state.path)

        merged = CommandUpdate.merge(config_state, system_state)
        return config_state, system_state, merged

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_merge_name(self, name="test_repo_1"):
        config_state, system_state, merged = self.merge_test_setup(name)
        self.assertIsNone(system_state.name)
        self.assertIsNotNone(config_state.name)

        self.assertEqual(
                config_state.name,
                merged.name
                )

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_merge_repo_id(self, name="test_repo_1"):
        config_state, system_state, merged = self.merge_test_setup(name)

        self.assertNotEqual(config_state.repo_id, system_state.repo_id)
        self.assertEqual(
                system_state.repo_id,
                merged.repo_id
                )

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_merge_path(self, name="test_repo_1"):
        config_state, system_state, merged = self.merge_test_setup(name)

        self.assertEqual(
                system_state.path,
                merged.path
                )

    # def test_merge_parent(self):
    #     self.init_repos()

    #     self.assertEqual(
    #             system_state.path,
    #             merged.path
    #             )
