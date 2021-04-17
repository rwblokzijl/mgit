from main import main

from pathlib import Path

from git import Repo
from git.exc import NoSuchPathError

import unittest
import shutil

class TestAcceptance(unittest.TestCase):

    """
    This class tests every command for real on the system
    """

    repo
    remote
    auto

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
        clone     |        | name, remote            | clone a repo to an existing remote

        show      |        | name                    | show a repo by name
        fix       |        | name                    | show a repo by name

        "repo remote"
        remote    | add    | repo, remote, name      | add a remote to the repo, and vv
        remote    | remove | repo, remote, name      | remove a remote from the repo, and vv
        remote    | origin | repo, remote, name      | set a remote as origin, and vv

        "mass repo"
        list      | -l -r [remotes] | list repos, (missing remote)
        fetch     | repos, remotes  | mass fetch
        pull      | repos, remotes  | mass pull
        push      | repos, remotes  | mass push (after shutdown)

        "automatic git functions" - stored: auto-[remote]-[branch] = [commit] [push] [pull] [fetch]
        auto      | add    | repo, branch, [commit] [push] [pull] [fetch], [[REMOTE]..] | add auto function to repo |
        auto      | remove | repo, branch, [commit] [push] [pull] [fetch], [[REMOTE]..] | remove auto function from branch |

        auto      | commit | commit branches with auto commit configured (warn when wrong branch is checked out)
        auto      | push   | push branches with auto push configured
        auto      | fetch  | fetch branches with auto fetch configured
        auto      | pull   | pull branches with auto pull configured

        "remotes"
        remotes   | show   | name           | show the remote and its repos
        remotes   | add    | name, url      | add a remote
        remotes   | remove | name           | remove a remote

        remotes   | list   |                | list remotes
        remotes   | clone  | repos, remote  | clone to remotes to another https://stackoverflow.com/questions/7818927/git-push-branch-from-one-remote-to-another

        "move to different command maybe"
        remotes   | check  | repos, remotes | find non up to date repos across all remotes
        remotes   | sync   | repos, remotes | fix non up to date repos across all remotes

        "maybe"
        remotes   | delete | name, remote   | remove repo from remote, maybe not implement for safety!!!
        remotes   | init   | name, remote   | init repo in remote

    """

    def setUp(self):
        self.repos_config           = "./test/__files__/test_repos_acceptance.ini"
        self.remotes_config         = "./test/__files__/test_remote_acceptance.ini"

        self.default_repos_config   = "./test/__files__/test_repos_acceptance_default.ini"
        self.default_remotes_config = "./test/__files__/test_remote_acceptance_default.ini"

        self.test_dir               = Path("/tmp/mgit/acceptance/")

    def assertRepoNotExists(self, path):
        with self.assertRaises(NoSuchPathError):
            Repo(path)

    def assertRepoExists(self, path):
        self.assertTrue(
                Repo(path)
                )

    def create_test_dir(self, child=""):
        (self.test_dir/child).mkdir(parents=True, exist_ok=True)

    def setUpFullTestDir(self):
        # normal
        self.create_test_dir("local/test_repo_1")
        self.create_test_dir("test_remote_1/test_repo_1")

        # nested
        self.create_test_dir("local/test_repo_2")
        self.create_test_dir("test_remote_1/test_repo_2")

        self.create_test_dir("local/test_repo_2/test_repo_3")
        self.create_test_dir("test_remote_1/test_repo_3")

        self.create_test_dir("local/test_repo_2/test_repo_3/test_repo_5")
        self.create_test_dir("test_remote_1/test_repo_5")

        # Not installed
        self.create_test_dir("test_remote_2/test_repo_6")

    def initGitForTestDir(self):

        #normal
        Repo.init(self.test_dir / "local/test_repo_1")
        Repo.init(self.test_dir / "test_remote_1/test_repo_1")

        #with commit
        (self.test_dir / 'local/test_repo_1/file.txt').touch()
        repo = Repo(self.test_dir / 'local/test_repo_1/')
        repo.git.add('--all')
        repo.index.commit("test")

        # recursive
        Repo.init(self.test_dir / "local/test_repo_2")
        Repo.init(self.test_dir / "test_remote_1/test_repo_2")

        Repo.init(self.test_dir / "local/test_repo_2/test_repo_3")
        Repo.init(self.test_dir / "test_remote_1/test_repo_3")

        Repo.init(self.test_dir / "local/test_repo_2/test_repo_3/test_repo_5")
        Repo.init(self.test_dir / "test_remote_1/test_repo_5")

        # not installed
        Repo.init(self.test_dir / "test_remote_2/test_repo_6")

    def makeDirty(self):
        with open(self.test_dir / 'local/test_repo_1/file.txt', 'w') as f:
            f.write("hi")

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
    # TODO test no remotes (use default) TEST
    # TODO specify origin?? TEST
    # TODO resolve parents TEST
    # TODO fail before asking confirmation
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

    def test_repo_init_remote(self):
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

    "remote list      | [[remote]...] | list repos, (missing remote)"
    # TODO use defaults if empty
    def test_remote_list(self):
        self.setUpFullTestDir()

        ans = self.run_test_command("remote list test_remote_1")
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

    "status    | [NAME] [-l/--local [PATH]] [-d] | show status of all repos (clean up ordering)"
    # TODO show unpushed and unpulled for all remotes for NON MASTER BRANCH!!! master is hardcoded in the code now
    def test_status_path(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()
        self.makeDirty()

        ans = list(self.run_test_command(f"status -l {self.test_dir / 'local'} "))
        self.assertEqual(
                4,
                len(ans)
                )

    def test_status_path_dirty(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()
        self.makeDirty()

        ans = list(self.run_test_command(f"status -d -l {self.test_dir / 'local'} "))
        self.assertEqual(
                1,
                len(ans)
                )

    def test_status_name(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()
        self.makeDirty()

        ans = list(self.run_test_command(f"status test_repo_1"))
        self.assertEqual(
                1,
                len(ans)
                )

    def test_status_name_recursive(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()
        self.makeDirty()

        ans = dict(self.run_test_command(f"status -r test_repo_2"))
        self.assertEqual(
                1,
                len(ans)
                )
        self.assertEqual(
                1,
                len(list(ans.values())[0])
                )
        self.assertEqual(
                1,
                len(list(list(ans.values())[0].values())[0])
                )
        self.assertEqual(
                None,
                list(list(list(ans.values())[0].values())[0].values())[0]
                )

    def test_status_name_multiple(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()
        self.makeDirty()

        ans = list(self.run_test_command(f"status test_repo_1 test_repo_2"))
        self.assertEqual(
                2,
                len(ans)
                )

    def test_status_name_all(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()
        self.makeDirty()

        ans = list(self.run_test_command(f"status"))
        self.assertEqual(
                4,
                len(ans)
                )

    # def test_list(self):
    #     self.setUpFullTestDir()
    #     self.initGitForTestDir()

    #     ans = list(self.run_test_command(f"list"))
    #     print(ans)

    #     self.assertEqual(
    #             4,
    #             len(ans)
    #             )

    def test_list_installed(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()

        ans = list(self.run_test_command(f"list -i"))

        self.assertEqual(
                4,
                len(ans)
                )

    "dirty    | [NAME]... [-l/--local [PATH]] [-d] | succeeds if any specified repo is dirty"
    def test_dirty_true(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()
        self.makeDirty()

        ans = list(self.run_test_command(f"status -d -l {self.test_dir / 'local'} "))
        self.assertEqual(
                1,
                len(ans)
                )

    def test_dirty_false(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()

        with self.assertRaises(Exception):
            self.run_test_command( f"dirty -l {self.test_dir / 'local'} ")

        self.makeDirty()

        self.run_test_command( f"dirty -l {self.test_dir / 'local'} ")

    "install name [--remote REMOTE] | install a repo from remote by name (add listed remotes)"
    def test_install(self):
        self.setUpFullTestDir()
        self.initGitForTestDir()

        test_repo = self.test_dir / "local/test_repo_6"

        self.assertRepoNotExists(test_repo)

        self.run_test_command( f"install -y test_repo_6 ")

        self.assertRepoExists(test_repo)
