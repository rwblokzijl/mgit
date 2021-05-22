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

        merged = CommandUpdate(**self.interactors).merge(config_state, system_state)
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

    @parameterized.expand([ "test_repo_3", "test_repo_5", ])
    def test_merge_parent(self, name="test_repo_3"):
        names = self.config.get_all_repo_names()
        self.init_repos(names, commit=True)

        config_state = self.config.get_state(name=name)
        system_state = self.system.get_state(path=config_state.path)

        merged = CommandUpdate(**self.interactors).merge(config_state, system_state)

        self.assertEqual(
                merged.parent.repo_id,
                system_state.parent.repo_id
                )

        self.assertEqual(
                merged.parent.path,
                system_state.parent.path
                )

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_merge_remotes_equal(self, name="test_repo_1"):
        # remotes that are the same should return that same remote
        # unname vs named that are the same should return the named
        config_state, system_state, merged = self.merge_test_setup(name)
        system_remotes = {self.config.resolve_remote(r) for r in system_state.remotes}

        self.assertEqual(
                config_state.remotes,
                merged.remotes
                )

        self.assertEqual(
                system_remotes,
                merged.remotes
                )

    # @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_merge_remotes_wrong_name(self, name="test_repo_1"):
        # same named remotes, with different urls should error
        # remotes with the same url, but different names should take the name of the config
        # remotes in one, but not the other
        pass
