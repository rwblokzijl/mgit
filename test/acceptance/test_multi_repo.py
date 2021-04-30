# import os
# os.environ["ACCEPTANCE"] = "yes"

from test.acceptance.AcceptanceBase import AcceptanceBase

class MultiRepoAcceptanceTests(AcceptanceBase):

    def test_status(self):
        """
        positional arguments:
          name                  Name of the project
        optional arguments:
          -l [DIR], --local [DIR]
                                Path to recursively explore
          -u, --untracked       List directories with untracked files as dirty
          -r, --recursive       Include subrepos
          -d, --dirty           Only show dirty repos
          -p, --remotes         Include unpushed/pulled in dirty
          -c, --count           Only return the amount of output
        """

        repo = self.config_state_interactor.get_state(name="test_repo_1")
        self.init_test_repos("test_repo_1")
        os.chdir(repo.path)
        self.run_test_command("status -h")
