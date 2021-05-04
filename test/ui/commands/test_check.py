from mgit.ui.commands.check import CommandCheck
from test.test_util import MgitUnitTestBase

from dataclasses import replace

from mgit.state.state import NamedRemoteRepo, Remote

from pathlib import Path

import unittest

class TestCheckCommand(MgitUnitTestBase):

    def init_repo(self, name):
        config = self.config.get_state(name="test_repo_1")
        self.system.set_state(config, init=True)

    def test_check_raises_missing(self):
        with self.assertRaises(ValueError):
            self.run_command( f"check -n test_repo_1" )

    def test_check_nothing_if_equal(self):
        # init directly from config
        self.init_repo("test_repo_1")

        # no errors
        self.assertFalse(
                self.run_command( f"check -n test_repo_1" )
                )

    def test_check_something_if_differs(self):
        # init from config
        self.init_repo("test_repo_1")

        # change config
        config = self.config.get_state(name="test_repo_1")

        original: NamedRemoteRepo = list(config.remotes)[0]
        changed: NamedRemoteRepo = replace(original, remote=replace(original.remote, name="new_name"))

        config.remotes.discard(original)
        config.remotes.add(changed)

        self.config.set_state(config)

        # check if mismatch is caught
        self.assertTrue(
                self.run_command( f"check -n test_repo_1" )
                )

    def test_all(self):
        self.init_repos()
        self.assertFalse(
                self.run_command( f"check -a" )
                )
