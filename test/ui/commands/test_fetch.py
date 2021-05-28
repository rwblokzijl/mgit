import mgit.ui.commands.fetch # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

import os

from git import Repo
from pathlib import Path

from parameterized import parameterized

class TestFetchCommand(MgitUnitTestBase):

    # @parameterized.expand([ "test_repo_1", "test_repo_2", "test_repo_3", "test_repo_5", "test_repo_6" ])
    def test_fetch(self, name="test_repo_1"):
        self.init_repos([name])
        self.init_remotes_for_test_repos([name])

        config = self.config.get_state(name=name)
        system = self.system.get_state(config.path)

        remote = list(system.remotes)[0]

        self.commit_in_repo(remote.url)

        # commit exists in remote
        remote_commit = Repo(remote.url).branches.master.commit

        # no local commit
        self.assertFalse(Repo(system.path).remotes[remote.name].refs)

        # fetch
        self.run_command_raw(f"fetch -n {name}")

        # local commit exists
        local_commit = Repo(system.path).remotes[remote.name].refs.master.commit
        self.assertEqual(remote_commit, local_commit)

