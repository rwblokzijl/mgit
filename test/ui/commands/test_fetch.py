import mgit.ui.commands.fetch # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

import os

from pygit2 import Repository, GIT_BRANCH_REMOTE
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

        # commit exists in remote
        self.commit_in_repo(remote.url)
        remote_commit_hex = Repository(remote.url).branches["master"].target.hex # remote hash exists

        self.assertEqual(len(remote_commit_hex), 40) # Is a proper hash
        self.assertEqual( Repository(system.path).branches.get(f"{remote.name}/master"), None ) # Branch does not exist locally

        # fetch
        self.run_command_raw(f"fetch -n {name}")

        self.assertEqual( Repository(system.path).branches[f"{remote.name}/master"].target.hex, remote_commit_hex ) # Branch exists locally and has same hash as remote
        self.assertEqual( Repository(system.path).branches.get(f"master"), None ) # Local master is not overwritten on fetch

