import sys
from contextlib import contextmanager
from io import StringIO
import copy
import shutil
import os

import test

from unittest.mock import Mock
import unittest

from pathlib import Path

from mgit.state import Remote, NamedRemoteRepo, RemoteType, RepoState

from mgit.ui.cli import CLI
from mgit.ui.commands._mgit import MgitCommand
from mgit.printing import pretty_string

from mgit.config_state_interactor  import ConfigStateInteractor
from mgit.system_state_interactor  import SystemStateInteractor
from mgit.remote_interactor        import RemoteInteractor
from mgit.general_state_interactor import GeneralStateInteractor
from mgit.local_system_interactor  import LocalSystemInteractor

from typing import Union, List, Optional
from types import GeneratorType

class MockRemoteInteractor(RemoteInteractor):
    "Makes sure we never test using a remote repo"

    def __init__(self, test_dir):
        self.test_dir = Path(test_dir)
        super(MockRemoteInteractor, self).__init__()

    def _assert_local_path(self, path: str):
        "will error if not in test dir"
        Path(path).expanduser().absolute().relative_to(self.test_dir.expanduser().absolute())

    def _get_interactor(self, remote: Remote) -> 'RemoteInteractor':
        assert remote.remote_type == RemoteType.LOCAL
        self._assert_local_path(remote.get_url())
        return super(MockRemoteInteractor, self)._get_interactor(remote)

class MockSystemStateInteractor(SystemStateInteractor):
    "Makes sure we never test repos outside the test dir"

    def __init__(self, test_dir):
        self.test_dir = Path(test_dir)
        super(MockSystemStateInteractor, self).__init__()

    def _assert_local_path(self, path):
        if path is None:
            assert False, f"{path} not in test dir"
        "will error if not in test dir"
        Path(path).expanduser().absolute().relative_to(self.test_dir.expanduser().absolute())

    def get_all_local_repos_in_path(self, *args, **kwargs) -> List[RepoState]:
        self._assert_local_path(kwargs.get("path") or args[0])
        return super(MockSystemStateInteractor, self).get_all_local_repos_in_path(*args, **kwargs)

    def set_state(self, *args, **kwargs):
        self._assert_local_path((kwargs.get("repo_state") or args[0]).path)
        return super(MockSystemStateInteractor, self).set_state(*args, **kwargs)

    def get_state(self, *args, **kwargs) -> Optional[RepoState]:
        self._assert_local_path(kwargs.get("path") or args[0])
        return super(MockSystemStateInteractor, self).get_state(*args, **kwargs)

class MgitUnitTestBase(unittest.TestCase):
    def setUp(self):
        self.repos_config           = "./test/__files__/test_repos_acceptance.ini"
        self.remotes_config         = "./test/__files__/test_remote_acceptance.ini"

        self.default_repos_config   = "./test/__files__/test_repos_acceptance_default.ini"
        self.default_remotes_config = "./test/__files__/test_remote_acceptance_default.ini"

        self.test_dir               = Path("/tmp/mgit/")

        self.config_state_interactor  = ConfigStateInteractor(repos_file=self.repos_config, remotes_file=self.remotes_config)
        self.system_state_interactor  = MockSystemStateInteractor(self.test_dir)
        self.remote_interactor        = MockRemoteInteractor(self.test_dir)
        self.local_system_interactor  = LocalSystemInteractor() #read only
        self.general_state_interactor = GeneralStateInteractor(
                config_state_interactor = self.config_state_interactor,
                system_state_interactor = self.system_state_interactor,
                local_system_interactor = self.local_system_interactor,
                remote_interactor       = self.remote_interactor,
                )

        self.interactors = {
                'config_state_interactor':  self.config_state_interactor,
                'system_state_interactor':  self.system_state_interactor,
                'remote_interactor':        self.remote_interactor,
                'general_state_interactor': self.general_state_interactor,
                'local_system_interactor':  self.local_system_interactor
                }

        os.makedirs(self.test_dir / "acceptance/test_remote_1")
        os.makedirs(self.test_dir / "acceptance/test_remote_2")

    def tearDown(self):
        self.reset_configs()
        self.clear_test_dir()

    def clear_test_dir(self):
        shutil.rmtree("/tmp/mgit/", ignore_errors=True)

    def get_repo_states(self, names: List[str]=[]):
        if names:
            return [ self.config_state_interactor.get_state(name=r) for r in names ]
        else:
            return self.config_state_interactor.get_all_repo_state()

    def init_repos(self, names: List[str]=[]):
        all_repos = self.get_repo_states(names)
        for repo in all_repos:
            self.system_state_interactor.set_state(repo)

    def init_remotes_for_test_repos(self, names: List[str]=[]):
        all_repos = self.get_repo_states(names)
        for repo in all_repos:
            for remote_repo in repo.remotes:
                self.remote_interactor.init_repo(remote_repo)

    def reset_configs(self):
        shutil.copy(self.default_remotes_config, self.remotes_config)
        shutil.copy(self.default_repos_config, self.repos_config)

    def run_command_raw(self, command: str):
        return CLI(MgitCommand(**self.interactors)).run(filter(None, command.split(" "))) # can be many things including generators

    def run_command(self, command: str):
        output = self.run_command_raw(command)
        generator = pretty_string(output)
        ans = list(generator)
        return ans

