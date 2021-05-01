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

from mgit.config_state_interactor  import ConfigStateInteractor
from mgit.system_state_interactor  import SystemStateInteractor
from mgit.remote_interactor        import RemoteInteractor
from mgit.general_state_interactor import GeneralStateInteractor
from mgit.local_system_interactor  import LocalSystemInteractor

from typing import Union, List, Optional

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

    def _assert_local_path(self, path: Optional[Union[Path, str]]):
        if path is None:
            assert False, f"{path} not in test dir"
        "will error if not in test dir"
        Path(path).expanduser().absolute().relative_to(self.test_dir.expanduser().absolute())

    def get_all_local_repos_in_path(self, path: Union[Path, str], ignore_paths=None) -> List[RepoState]:
        self._assert_local_path(path)
        return super(MockSystemStateInteractor, self).get_all_local_repos_in_path(path)

    def set_state(self, repo_state: RepoState, init=False):
        self._assert_local_path(repo_state.path)
        return super(MockSystemStateInteractor, self).set_state(repo_state, init)

    def get_state(self, path: Union[Path, str]) -> Optional[RepoState]:
        self._assert_local_path(path)
        return super(MockSystemStateInteractor, self).get_state(path)

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

    def reset_configs(self):
        shutil.copy(self.default_remotes_config, self.remotes_config)
        shutil.copy(self.default_repos_config, self.repos_config)

