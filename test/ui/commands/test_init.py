from mgit.ui.commands.init import CommandInit
from test.test_util import MgitUnitTestBase

from unittest.mock import Mock

from pathlib import Path

import unittest

class TestInitCommand(MgitUnitTestBase):

    def test_init(self):
        name="test"
        path=Path("/tmp/mgit/kek")

        # doesnt exist in config
        self.assertIsNone(self.config_state_interactor.get_state(name=name))
        # doesnt exist in system
        self.assertIsNone(self.system_state_interactor.get_state(path=path))

        list(CommandInit(**self.interactors).run(
                y=True,
                name=name,
                path=path,
                remotes=set(),
                categories=set()
                ))

        # exists in config
        self.assertIsNotNone(self.config_state_interactor.get_state(name=name))
        # exists in system
        self.assertIsNotNone(self.system_state_interactor.get_state(path=path))

    def test_init_remotes(self):
        name="test"
        path=Path("/tmp/mgit/kek")

        list(CommandInit(**self.interactors).run(
                y=True,
                name=name,
                path=path,
                remotes=["test_remote_1", "test_remote_2:test_repo_name"],
                categories=set()
                ))

        repo = self.config_state_interactor.get_state(name=name)
        remote1, remote2 = sorted(repo.remotes, key=lambda x: x.project_name)

        # Remote 1 instantiated
        self.assertIn(
                name,
                self.remote_interactor.list_remote(remote1.remote)
                )

        # Remote 2 instantiated
        self.assertIn(
                "test_repo_name",
                self.remote_interactor.list_remote(remote2.remote)
                )
