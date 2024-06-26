"""
Sets up the base test class with test versions of all system components
"""

from mgit.local.config         import Config
from mgit.local.system         import System
from mgit.remote.remote_system import RemoteSystem
from mgit.ui.cli               import CLI
from mgit.ui.commands._mgit    import MgitCommand
from mgit.util.printing        import pretty_string
from mgit.local.state          import *

from pygit2 import Repository, GitError
from pathlib import Path
from typing  import *

import contextlib
import io
import os
import shutil
import sys
import unittest


class MockRemoteSystem(RemoteSystem):
    "Makes sure we never test using a remote repo"

    def __init__(self, test_dir):
        self.test_dir = Path(test_dir)
        super().__init__()

    def _assert_local_path(self, path: str):
        "will error if not in test dir"
        Path(path).expanduser().absolute().relative_to(self.test_dir.expanduser().absolute())

    def _get_interactor(self, remote: Remote) -> RemoteSystem:
        assert remote.type == RemoteType.LOCAL
        self._assert_local_path(remote.get_url())
        return super()._get_interactor(remote)

class MockSystem(System):
    "Makes sure we never test repos outside the test dir"

    def __init__(self, test_dir):
        self.test_dir = Path(test_dir)
        super().__init__()

    def _assert_local_path(self, path):
        if path is None:
            assert False, f"{path} not in test dir"
        # will error if not in test dir
        Path(path).expanduser().absolute().relative_to(self.test_dir.expanduser().absolute())

    def get_all_local_repos_in_path(self, *args, **kwargs) -> List[RepoState]:
        self._assert_local_path(kwargs.get("path") or args[0])
        return super().get_all_local_repos_in_path(*args, **kwargs)

    def set_state(self, *args, **kwargs):
        self._assert_local_path((kwargs.get("repo_state") or args[0]).path)
        return super().set_state(*args, **kwargs)

    def get_state(self, *args, **kwargs) -> RepoState: # type: ignore
        self._assert_local_path(kwargs.get("path") or args[0])
        return super().get_state(*args, **kwargs)

class MgitUnitTestBase(unittest.TestCase):
    """
    Base for all commands test.

    It inits a test version of all interactors
    """

    def setUp(self):
        self.repos_config           = "./test/__files__/test_repos_acceptance.ini"
        self.remotes_config         = "./test/__files__/test_remote_acceptance.ini"

        self.default_repos_config   = "./test/__files__/test_repos_acceptance_default.ini"
        self.default_remotes_config = "./test/__files__/test_remote_acceptance_default.ini"

        self.test_dir               = Path("/tmp/mgit/")

        self.config  = Config(repos_file=self.repos_config, remotes_file=self.remotes_config)
        self.system  = MockSystem(self.test_dir)
        self.remote_system        = MockRemoteSystem(self.test_dir)

        self.interactors = {
                'config':  self.config,
                'system':  self.system,
                'remote_system':        self.remote_system,
                }

        os.makedirs(self.test_dir / "acceptance/test_remote_1")
        os.makedirs(self.test_dir / "acceptance/test_remote_2")

    def tearDown(self):
        self.reset_configs()
        self.clear_test_dir()

    def clear_test_dir(self):
        shutil.rmtree("/tmp/mgit/", ignore_errors=True)

    def get_repo_states(self, names: List[str]=None):
        if names:
            return [ self.config.get_state(name=r) for r in names ]
        return self.config.get_all_repo_state()

    def init_repos(self, names: List[str]=None, commit=False):
        all_repos = self.get_repo_states(names)
        for repo in all_repos:
            self.system.set_state(repo, init=True)
            if commit:
                self.commit_in_repo(repo.path)

    def init_remotes_for_test_repos(self, names: List[str]=None, commit=False):
        all_repos = self.get_repo_states(names)
        for repo in all_repos:
            for remote_repo in repo.remotes:
                self.remote_system.init_repo(remote_repo)
                if commit:
                    self.commit_in_repo(remote_repo.path)

    def make_dirty(self, names: List[str]=None):
        all_repos = self.get_repo_states(names)
        for repo in all_repos:
            file_path = os.path.join(repo.path, 'new-fileee')
            os.system(f"echo something > {file_path}")

    def commit_in_repo(self, path: Path):
        repo = Repository(path)
        file_path = os.path.join(repo.workdir, 'new-file')
        try:
            ref = repo.head.name # throws is no head, this means there are no previous commits
            parents = [repo.head.target]
        except GitError:
            parents = [] # initial commit

        os.system(f"echo something > {file_path}")
        repo.index.add_all()
        repo.index.write()
        repo.create_commit(
            "HEAD",                  # reference_name
            repo.default_signature,  # author
            repo.default_signature,  # committer
            "Message",               # message
            repo.index.write_tree(), # tree
            parents                  # parents
        )

    def reset_configs(self):
        shutil.copy(self.default_remotes_config, self.remotes_config)
        shutil.copy(self.default_repos_config, self.repos_config)

    def run_command_raw(self, command: str):
        "Can many things including generators"
        return CLI(MgitCommand(**self.interactors)).run(
                filter(None, command.split(" "))
                )

    def run_command(self, command: str):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            output = self.run_command_raw(command)
            possible_generator = pretty_string(output)
            ans = "\n".join(list(possible_generator))
            return ans

