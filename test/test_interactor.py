from mgit.interactor import Builder
from mgit.interactor import MgitInteractor

from mgit.remotes.remotes_builder    import RemotesBuilder
from mgit.remotes.remotes_collection import RemotesCollection

from mgit.repos.repos_builder        import ReposBuilder
from mgit.repos.repos_collection     import ReposCollection

from test.test_util import MockPersistence

import unittest
from unittest.mock import Mock, MagicMock

class TestInteractor(unittest.TestCase):

    """Test case docstring."""

    def get_file_test_interactor(self):
        return Builder().build(
                repos_config="test/__files__/test_repos.ini",
                remotes_config="test/__files__/test_remote.ini"
                )

    def get_memory_test_interactor(self,
            remotes_con=None,
            repo_con=None,

            remote_persistence_file=None,
            repo_persistence_file=None,

            remotes_builder=RemotesBuilder(),
            repos_builder=ReposBuilder(),

            local_system_interactor=None):
        self.remotes_data =  {
            "test" : {
                "name" : "test",
                "url" : "test@example.com",
                "path" : "/test/path",
                "type" : "ssh",
                "port" : "22",
                "is_default" : False,
                },
            "test2" : {
                "name" : "test2",
                "url" : "test2@example.com",
                "path" : "/test2/path",
                "type" : "ssh",
                "port" : "22",
                "is_default" : True
                }
            }
        remotes_persistence = MockPersistence(remotes_con or self.remotes_data, remote_persistence_file)
        remotes = RemotesCollection(persistence=remotes_persistence, builder=remotes_builder)

        self.repos_data = {
            "example" : {
                "name" : "example",
                "path" : "example",
                "parent" : "example2",
                "origin" : "test",
                "categories" : ["config"],
                "test-repo" : "example-name-in-home",
                "test2-repo" : "different-example-name",
                "repo_id" : "1234567890f39a8a19a8364fbed2fa317108abe6",
                "archived" : True,
                },
            "example2" : {
                "name" : "example2",
                "path" : "/tmp/mgit_path/example2",
                "originurl" : "bloodyfool2@git.bloodyfool.family:/direct_repo",
                "categories" : ["school"],
                "test-repo" : "example-name-in-test",
                "test2-repo" : "different-example-name",
                "repo_id" : "1234567890f39a8a19a8364fbed2fa317112342",
                "archived" : False,
                }
            }
        repos_persistence = MockPersistence(repo_con or self.repos_data, repo_persistence_file)
        repos  = ReposCollection(persistence=repos_persistence, builder=repos_builder, remotes=remotes)

        return MgitInteractor(repos, remotes, local_system_interactor or Mock())

    def get_remote_mock_builder(self,
            keys=["test", "test2" ],
            remote_mock=None):
        rmb = Mock()
        if not remote_mock:
            remote_mock = MagicMock()
            remote_mock.__contains__.return_value = False
            remote_mock.get_url.return_value = "TESTURL"
        self.remote_mocks = {r : remote_mock for r in keys}
        rmb.build.return_value = self.remote_mocks
        return rmb

