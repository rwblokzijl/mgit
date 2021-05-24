import mgit.ui.commands.update # pylint: disable=W0611 #import important for decorators to run
from mgit.ui.commands.update import CommandUpdate
from test.test_util import MgitUnitTestBase

from parameterized import parameterized

from dataclasses import replace

from mgit.local.state import *

class TestUpdateCommand(MgitUnitTestBase):

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_no_change(self, name="test_repo_1"):
        self.init_repos([name])

        before_config_state = self.config.get_state(name=name)
        before_system_state = self.system.get_state(path=before_config_state.path)

        self.run_command_raw(f"update -ycs -n {name}")

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

        self.run_command_raw(f"update -ys -n {name}")

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

        self.run_command_raw(f"update -yc -n {name}")

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

class TestMerge(MgitUnitTestBase):

    def merge(self, config, system):
        return CommandUpdate(**self.interactors).merge(config, system)

    def merge_test_setup(self, name):
        self.init_repos([name])

        config_state = self.config.get_state(name=name)
        system_state = self.system.get_state(path=config_state.path)

        self.commit_in_repo(system_state)
        system_state = self.system.get_state(path=config_state.path)

        merged = self.merge(config_state, system_state)
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
        _, system_state, merged = self.merge_test_setup(name)

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

        merged = self.merge(config_state, system_state)

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

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_merge_remotes_different_name(self, name="test_repo_1"):
        """
        remotes with the same url, but different names should take the name of the config
        """
        # init config to system
        self.init_repos([name])
        # self.commit_in_repo(system_state)

        # Change remote name in config
        config_state = self.config.get_state(name=name)
        named  = config_state.remotes.pop()
        new_remote = replace(named.remote, name="new_name")
        new_rr     = replace(named, remote=new_remote)
        config_state.remotes.add(new_rr)
        self.config.set_state(config_state)

        system_state = self.system.get_state(path=config_state.path)

        # merge
        merged = self.merge(config_state, system_state)

        # see if merged has the new name from config
        config_state = self.config.get_state(name=name)
        self.assertEqual(
                config_state.remotes,
                merged.remotes)

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_merge_remotes_different_url(self, name="test_repo_1"):
        """
        same named remotes, with different urls should take url of system, or error
        """
        # init config to system
        self.init_repos([name])

        config_state = self.config.get_state(name=name)
        system_state = self.system.get_state(path=config_state.path)

        # change the url in system
        system_state.remotes = {self.config.resolve_remote(r) for r in system_state.remotes}
        remote_repo = system_state.remotes.pop()
        self.assertIsInstance(remote_repo, NamedRemoteRepo)
        new_rr     = UnnamedRemoteRepo(remote_repo.name, url="NEW_URL")
        system_state.remotes.add(new_rr)

        # merge
        merged = self.merge(config_state, system_state)

        # see if merged has the new url from system
        self.assertEqual(
                system_state.remotes,
                merged.remotes)

    @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_merge_remotes_differing_both(self, name="test_repo_1"):
        """
        remotes in one, but not the other, just include both
        """
        # init config to system
        self.init_repos([name])

        config_state = self.config.get_state(name=name)
        system_state = self.system.get_state(path=config_state.path)
        system_state.remotes = {self.config.resolve_remote(r) for r in system_state.remotes}

        # add url to system
        system_state.remotes.add(UnnamedRemoteRepo(
            remote_name="some_system_name",
            url="some_system_url"
            ))
        # add url to config
        config_state.remotes.add(
                NamedRemoteRepo(
                    project_name="some_config_path_suffix",
                    remote=Remote(
                        name="some_config_name",
                        url="some_sytem_url",
                        path="some_sytem_path_prefix",
                        type=RemoteType.LOCAL)
                    )
                )

        # merge
        merged = self.merge(config_state, system_state)

        # see if merged has the new remote from system
        self.assertTrue(
                config_state.remotes.issubset(merged.remotes))
        # see if merged has the new remote from config
        self.assertTrue(
                system_state.remotes.issubset(merged.remotes))

