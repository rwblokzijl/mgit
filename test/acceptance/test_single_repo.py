# import os
# os.environ["ACCEPTANCE"] = "yes"

from test.acceptance.AcceptanceBase import AcceptanceBase


class SingleRepoAcceptanceTests(AcceptanceBase):

    def test_install(self):
        with self.assertRaises(ValueError):
            self.run_test_command("show test_repo_1")
        self.run_test_command("install -y test_repo_1")
        self.assertEqual(
                self.run_test_command("show test_repo_1").source,
                ""
                )

