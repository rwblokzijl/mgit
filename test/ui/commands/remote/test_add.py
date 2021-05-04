import mgit.ui.commands.remote.add #import important for decorators to run
from test.test_util import MgitUnitTestBase

from pathlib import Path

class TestInitCommand(MgitUnitTestBase):

    def test_remote_add(self):
        self.init_repos(["test_repo_1"])
        self.run_command("remote add -n test_repo_1 test_remote_1")
