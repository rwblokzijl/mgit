from mgit.main import main
from mgit.config_state_interactor import ConfigStateInteractor
from mgit.system_state_interactor import SystemStateInteractor
from test.test_util import MgitUnitTestBase

from pathlib import Path

from git import Repo # type: ignore
from git.exc import NoSuchPathError # type: ignore

import unittest
import shutil
import os

from typing import List


@unittest.skipUnless(os.environ.get("ACCEPTANCE"), "acceptance tests run slow")
class AcceptanceBase(MgitUnitTestBase):
    """
    This is the baseclass that allows testing of every command for real on the system

        repo
        remote
        auto

        Commands to add acceptance tests for:
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

    def assertRepoNotExists(self, path):
        with self.assertRaises(NoSuchPathError):
            Repo(path)

    def assertRepoExists(self, path):
        self.assertTrue(
                Repo(path)
                )

    def init_remotes_for_test_repos(self, names: List[str]=[]):
        all_repos = self.config_state_interactor.get_all_repo_state()
        if names: #only init relevant repos
            all_repos = [r for r in all_repos if r.name in names]
        for repo in all_repos:
            for remote in repo.remotes:
                _, path = remote.get_url().rsplit(':', 1)
                self.assertTrue(path.startswith('/tmp/mgit'))
                Path(path).mkdir(parents=True, exist_ok=False)

    def init_test_repos(self, names: List[str]=[]):
        all_repos = self.config_state_interactor.get_all_repo_state()
        if names: #only init relevant repos
            all_repos = [r for r in all_repos if r.name in names]
        for repo in all_repos:
            self.assertTrue(repo.path.startswith('/tmp/mgit'))
            self.system_state_interactor.set_state(repo)

    def run_test_command(self, command):
        return main(
                repos_config   = self.repos_config,
                remotes_config = self.remotes_config,
                args           = command.split()
                )

