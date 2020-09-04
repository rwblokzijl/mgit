from main import main

from pathlib import Path

from git import Repo

import unittest
import shutil

class TestAcceptance(unittest.TestCase):

    """This class tests every command for real on the system"""

    """ Commands to add acceptance tests for:
        "general"
        update    | update properties about the repos that can be infered
        sanity    | full sanity check of all repos/remotes/configs
        config    | commands for handling the configs

        "repo"
        add       |        | path, name              | add a repo (init remote?)
        move      |        | path, name              | move a repo to another path
        remove    |        | name                    | stop tracking a repo
        rename    |        | name, name              | rename the repo in the config
        archive   |        | name                    | add archive flag to
        unarchive |        | name                    | remove archive flag to
        install   |        | name                    | install a repo from remote by name (add listed remotes)
        clone     |        | name, remote            | clone a repo to an existing remote
        show      |        | name                    | show a repo by name

        "repo remote"
        remote    | add    | repo, remote, name      | add a remote to the repo, and vv
        remote    | remove | repo, remote, name      | remove a remote from the repo, and vv
        remote    | origin | repo, remote, name      | set a remote as origin, and vv

        "mass repo"
        list      | -l -r [remotes] | list repos, (missing remote)
        dirty     | repos           | is any repo dirty
        status    | repos           | show status of all repos (clean up ordering)
        fetch     | repos, remotes  | mass fetch
        pull      | repos, remotes  | mass pull
        push      | repos, remotes  | mass push (after shutdown)

        "remotes"
        remotes   | list   |                | list remotes
        remotes   | add    | name, url      | add a remote
        remotes   | remove | name           | remove a remote
        remotes   | init   | name, remote   | init repo in remote
        remotes   | delete | name, remote   | remove repo from remote, maybe not implement for safety!!!
        remotes   | clone  | repos, remote  | clone to remotes to another https://stackoverflow.com/questions/7818927/git-push-branch-from-one-remote-to-another
        remotes   | show   | name           | show the remote and its repos
        remotes   | check  | repos, remotes | find non up to date repos across all remotes
        remotes   | sync   | repos, remotes | fix non up to date repos across all remotes

    """

    def setUp(self):
        self.repos_config           = "./test/__files__/test_repos_acceptance.ini"
        self.remotes_config         = "./test/__files__/test_remote_acceptance.ini"

        self.default_repos_config   = "./test/__files__/test_repos_acceptance_default.ini"
        self.default_remotes_config = "./test/__files__/test_remote_acceptance_default.ini"

        self.test_dir               = Path("/tmp/mgit/acceptance/")

    def create_test_dir(self, child=""):
        (self.test_dir/child).mkdir(parents=True, exist_ok=True)

    def setUpFullTestDir(self):
        self.create_test_dir("local/test_repo_1")
        self.create_test_dir("test_remote_1/test_repo_1")

        self.create_test_dir("local/test_repo_2")
        self.create_test_dir("test_remote_1/test_repo_2")

        self.create_test_dir("local/test_repo_2/test_repo_3")
        self.create_test_dir("test_remote_1/test_repo_3")

        self.create_test_dir("local/test_repo_2/test_repo_3/test_repo_5")
        self.create_test_dir("test_remote_1/test_repo_5")

    def clear_test_dir(self):
        shutil.rmtree("/tmp/mgit/acceptance/", ignore_errors=True)

    def tearDown(self):
        self.reset_configs()
        self.clear_test_dir()

    def reset_configs(self):
        shutil.copy(self.default_remotes_config, self.remotes_config)
        shutil.copy(self.default_repos_config, self.repos_config)

    def run_test_command(self, command):
        return main(
                repos_config   = self.repos_config,
                remotes_config = self.remotes_config,
                args           = command.split(),
                silent         = True
                )

    "category list # lists all categories"
    def test_category_list(self):
        cats = self.run_test_command("category list")
        self.assertEqual(
                ["category1", "category2"],
                cats)

    "category show [category] # show the category and children"
    def test_category_show(self):
        ans = self.run_test_command("category show category1")
        self.assertEqual(
                ans["category1"],
                ["test_repo_1"]
                )

    "category add [repo] [category] # add category"
    def test_category_add(self):
        ans = self.run_test_command("category show category3")
        self.assertEqual(
                ans["category3"],
                []
                )

        self.run_test_command("category add test_repo_1 category3")

        ans = self.run_test_command("category show category3")
        self.assertEqual(
                ans["category3"],
                ["test_repo_1"]
                )

    "category remove [repo] [category] # remote category"
    def test_category_remove(self):
        ans = self.run_test_command("category show category1")
        self.assertEqual(
                ans["category1"],
                ["test_repo_1"]
                )

        self.run_test_command("category remove test_repo_1 category1")

        ans = self.run_test_command("category show category1")
        self.assertEqual(
                ans["category1"],
                []
                )

    "init [--path path] [--name name] [--remotes [remote[:repo_name]].. ] # init a repo local and remote"
    # TODO test no remotes (use default)
    # TODO specify origin??
    def test_repo_init(self):
        self.create_test_dir("test_remote_1")

        test_repo = self.test_dir / "local/test_repo_4"
        self.run_test_command(f"init -y --name test_repo_4_alt --path {test_repo} --remotes test_remote_1:test_repo_4_alt_remote")

        self.assertTrue(
                Repo(test_repo)
                )

        self.assertTrue(
                Repo(self.test_dir / "test_remote_1" / 'test_repo_4_alt_remote')
                ) # testing the remote, locally

        #Test that its added to the file
        self.run_test_command("category add test_repo_4_alt category3")

        ans = self.run_test_command("category show category3")
        self.assertEqual(
                ans["category3"],
                ["test_repo_4_alt"]
                )

    "list      | [[remote]...] | list repos, (missing remote)"
    # TODO use defaults(or local??!!) if empty
    # probs local needs a different command that takes path into account
    # unix philosophy bla bla, maybe make 'list' local and
    # 'query' or something else remote
    def test_list_local(self):
        self.setUpFullTestDir()

        ans = self.run_test_command("list test_remote_1")
        self.assertIn(
                "test_remote_1",
                ans
                )
        self.assertSetEqual(
                set([ 'test_repo_1', 'test_repo_2']),
                set(ans["test_remote_1"].keys())
                )
        self.assertSetEqual(
                set([ 'test_repo_3']),
                set(ans["test_remote_1"]['test_repo_2'])
                )
        self.assertSetEqual(
                set([ 'test_repo_5']),
                set(ans["test_remote_1"]['test_repo_2']['test_repo_3'])
                )
