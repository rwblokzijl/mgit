from main import main
from test.test_util import captured_output

from shutil import copy, rmtree
import os

import unittest

""" On this project:
    .     !######################!         .
    .     !##                  ##!         .
    The   !## >>    mgit    << ##!   project
    .     !##                  ##!         .
    .     !######################!         .

    It once stood for manage-git, briefly monitor-git, but now i lean towards multiple-git. It doens't matter tho, all are
    correct.

    The purpose of this script is to manage all the git repositories in my life, in bulk.

    ## Configs:

    - live in CONFIG_DIR
    - or in .mgit files inside an existing git repo (or not??)

    They specify the repos to manage

    # Features for later:
    generally infer repo from current dir

    # Commands so far:

    General:
    |------+--------+----------------------------------------------------------------------------|
    |      | update | update properties about the repos that can be infered                      |
    | TODO | sanity | full sanity check of all repos/remotes/configs                             |
    | TODO | config | commands for handling the configs                                          |
    | TODO |        | where to back them up and keep them consistent across remotes and machines |

    repo config actions:
    |------+-----------+--------+-------------------------+---------------------------------------------------------|
    |      | show      |        | name                    | show a repo by name                                     |
    | TODO | init      |        | path, [[remote name]..] | init a repo local and remote                            |
    |      | add       |        | path, name              | add a repo (init remote?)                               |
    |      | move      |        | path, name              | move a repo to another path                             |
    |      | remove    |        | name                    | stop tracking a repo                                    |
    |      | rename    |        | name, name              | rename the repo in the config                           |
    |      | archive   |        | name                    | add archive flag to                                     |
    |      | unarchive |        | name                    | remove archive flag to                                  |
    | TODO | install   |        | name                    | install a repo from remote by name (add listed remotes) |
    |      | category  |        |                         | category actions                                        |
    |      |           | list   |                         | lists all categories                                    |
    |      |           | show   | category                | show the category and children                          |
    |      |           | add    | repo, category          | add category                                            |
    |      |           | remove | repo, category          | remote category                                         |
    | TODO | remote    |        |                         | Repo remote actions                                     |
    | TODO |           | add    | repo, remote, name      | add a remote to the repo, and vv                        |
    | TODO |           | remove | repo, remote, name      | remove a remote from the repo, and vv                   |
    | TODO |           | origin | repo, remote, name      | set a remote as origin, and vv                          |

    mutli repo actions:
    |------+--------+----------------+----------------------------------------------|
    | TODO | list   |                | list repos, (missing remote)                 |
    |      | dirty  | repos          | is any repo dirty                            |
    | TODO | status | repos          | show status of all repos (clean up ordering) |
    |------+--------+----------------+----------------------------------------------|
    | TODO | fetch  | repos, remotes | mass fetch                                   |
    | TODO | pull   | repos, remotes | mass pull                                    |
    | TODO | push   | repos, remotes | mass push (after shutdown)                   |

    remote actions:
    |------+---------+--------+----------------+--------------------------------------------------------------------------------------------------------------------|
    | TODO | remotes |        |                | manage remotes                                                                                                     |
    |------+---------+--------+----------------+--------------------------------------------------------------------------------------------------------------------|
    |      |         | list   |                | list remotes                                                                                                       |
    |      |         | add    | name, url      | add a remote                                                                                                       |
    |      |         | remove | name           | remove a remote                                                                                                    |
    |------+---------+--------+----------------+--------------------------------------------------------------------------------------------------------------------|
    | TODO |         | init   | name, remote   | init repo in remote                                                                                                |
    | TODO |         | delete | name, remote   | remove repo from remote, maybe not implement for safety!!!                                                         |
    | TODO |         | clone  | repos, remote  | clone to remotes to another https://stackoverflow.com/questions/7818927/git-push-branch-from-one-remote-to-another |
    |------+---------+--------+----------------+--------------------------------------------------------------------------------------------------------------------|
    | TODO |         | show   | name           | show the remote and its repos                                                                                      |
    | TODO |         | check  | repos, remotes | find non up to date repos across all remotes                                                                       |
    | TODO |         | sync   | repos, remotes | fix non up to date repos across all remotes                                                                        |
"""

class TestMain(unittest.TestCase):

    """
    These are the unittests making sure the ui is properly implemented and called
    system behaviour is not tested here
    """

    def run_command(self, command):
        repos_config   = "test/__files__/test_repos.ini"
        remotes_config = "test/__files__/test_remote.ini"

        with captured_output() as (out, err):
            return main(
                    repos_config   = repos_config,
                    remotes_config = remotes_config,
                    args           = command.split()
                    )

    def run_disk_write_command(self, command):
        old_repos_config   = "test/__files__/test_repos.ini"
        old_remotes_config = "test/__files__/test_remote.ini"

        config_path = "/tmp/mgit_tests/config"
        repos_config   = os.path.join(config_path, "repos.ini")
        remotes_config = os.path.join(config_path, "remotes.ini")

        os.makedirs(config_path, exist_ok=True)
        copy(repos_config, repos_config)
        copy(remotes_config, remotes_config)

        with captured_output() as (out, err):
            return main(
                    repos_config   = repos_config,
                    remotes_config = remotes_config,
                    args           = command.split()
                    )

    def tearDown(self):
        rmtree("/tmp/mgit_tests/")

    def test_update(self):
        pass
        # self.run_command("update")

    """ todos
        "general"
        "update    | update properties about the repos that can be infered                      |"
        "sanity    | full sanity check of all repos/remotes/configs                             |"
        "config    | commands for handling the configs                                          |"

        "repo"
        "init      |        | path, [[remote name]..] | init a repo local and remote                            |"
        "add       |        | path, name              | add a repo (init remote?)                               |"
        "move      |        | path, name              | move a repo to another path                             |"
        "remove    |        | name                    | stop tracking a repo                                    |"
        "rename    |        | name, name              | rename the repo in the config                           |"
        "archive   |        | name                    | add archive flag to                                     |"
        "unarchive |        | name                    | remove archive flag to                                  |"
        "install   |        | name                    | install a repo from remote by name (add listed remotes) |"
        "clone     |        | name, remote            | clone a repo to an existing remote"

        "repo remote"
        "remote    | add    | repo, remote, name      | add a remote to the repo, and vv                        |"
        "remote    | remove | repo, remote, name      | remove a remote from the repo, and vv                   |"
        "remote    | origin | repo, remote, name      | set a remote as origin, and vv                          |"

        "mass repo"
        "list      |                | list repos, (missing remote)                 |"
        "dirty     | repos          | is any repo dirty                            |"
        "status    | repos          | show status of all repos (clean up ordering) |"
        "fetch     | repos, remotes | mass fetch                                   |"
        "pull      | repos, remotes | mass pull                                    |"
        "push      | repos, remotes | mass push (after shutdown)                   |"

        "remotes"
        "remotes   | list   |                | list remotes                                                                                                       |"
        "remotes   | add    | name, url      | add a remote                                                                                                       |"
        "remotes   | remove | name           | remove a remote                                                                                                    |"
        "remotes   | init   | name, remote   | init repo in remote                                                                                                |"
        "remotes   | delete | name, remote   | remove repo from remote, maybe not implement for safety!!!                                                         |"
        "remotes   | clone  | repos, remote  | clone to remotes to another https://stackoverflow.com/questions/7818927/git-push-branch-from-one-remote-to-another |"
        "remotes   | show   | name           | show the remote and its repos                                                                                      |"
        "remotes   | check  | repos, remotes | find non up to date repos across all remotes                                                                       |"
        "remotes   | sync   | repos, remotes | fix non up to date repos across all remotes                                                                        |"
    """

    def setUp(self):
        os.makedirs("/tmp/mgit_tests/", exist_ok=True)

    "category | list   |                | lists all categories"
    "category | show   | category       | show the category and children"
    "category | add    | repo, category | add category"
    "category | remove | repo, category | remote category"

    def test_category_list(self):
        pass

    def test_category_show(self):
        pass

    def test_category_add(self):
        pass

    def test_category_remove(self):
        pass

    "show      |        | name                    | show a repo by name                                     |"

    def test_main(self):
        self.run_command("category list")

