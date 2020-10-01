from test.test_interactor import TestInteractor

from unittest.mock import Mock, MagicMock
import unittest

from pathlib import Path

class TestSingleRepoInteractions(TestInteractor):
    def test_repo_show(self):
        interactor = self.get_file_test_interactor()
        ans = interactor.repo_show("dotfiles")
        self.assertDictEqual(
                ans,
                {
                    'name': 'dotfiles',
                    'repo_id': '01fc02504c4be741f9b9407f48565ece042a31cb',
                    'path': '~/.config/dotfiles',
                    'categories': ['config'],
                    'archived': False,
                    'origin': {
                            'name': 'home',
                            'url': 'bloodyfool@git.blokzijl.family:/data/git/projects/dotfiles2',
                        },
                    'remotes': {
                        'home': {
                            'name': 'home',
                            'url': 'bloodyfool@git.blokzijl.family:/data/git/projects/dotfiles2',
                            }
                        },
                    }
                )

    def test_repo_show_not_exist(self):
        interactor = self.get_file_test_interactor()
        with self.assertRaises(interactor.RepoNotFoundError):
            interactor.repo_show("dotfilesssdfasdfaser")

    def test_init(self):
        system_mock = Mock()
        interactor = self.get_memory_test_interactor(
                local_system_interactor=system_mock,
                )
        m1 = MagicMock()
        m1.get_url_with_repo.return_value = "testurl1"
        m2 = MagicMock()
        m2.get_url_with_repo.return_value = "testurl2"
        interactor.remotes = { "test": m1, "test2": m2 }
        path = "/tmp/mgit_tests/example3"
        interactor.repo_init(
                name="example3",
                path=path,
                remotes={
                    "test": "t1name",
                    "test2": "t2name"
                    }
                )
        system_mock.init.assert_called_with(path=path, remotes={
            "test" : "testurl1",
            "test2" : "testurl2"
            },
            origin=None
            )

        m1.init.assert_called_with(name="t1name")
        m2.init.assert_called_with(name="t2name")

    @unittest.skip("defaults not implemented")
    def test_init_defaults(self):
        interactor = self.get_memory_test_interactor()
        interactor.repo_init( "example3" )

    def test_init_nameExists_throwsRepoExists(self):
        interactor = self.get_memory_test_interactor()
        with self.assertRaises(interactor.RepoExistsError):
            interactor.repo_init( "example2" , "/tmp/mgit_tests/example2")

    def test_init_pathNotAvailable_throwsPathUnavailableError(self):
        system_mock = Mock()
        system_mock.path_available.return_value = False
        interactor = self.get_memory_test_interactor(
                local_system_interactor=system_mock,
                remotes_builder=self.get_remote_mock_builder()
                )
        with self.assertRaises(interactor.PathUnavailableError):
            interactor.repo_init( name="example3", path="/tmp/mgit_tests/example3")

    def test_remotesDontExist_throwsError(self):
        interactor = self.get_memory_test_interactor()
        with self.assertRaises(interactor.MissingRemoteError):
            interactor.repo_init(
                    name="example3",
                    path="/tmp/mgit_tests/example3",
                    remotes={
                        "home": "homename",
                        "bagn": "bagnname"
                        }
                    )

    def test_remoteRepoExists_throwsError(self):
        interactor = self.get_memory_test_interactor()
        tmock = MagicMock()
        tmock.__contains__.return_value = True
        interactor.remotes = {
                "test"  : tmock,
                "test2" : tmock}
        with self.assertRaises(interactor.RemoteRepoExistsError):
            interactor.repo_init(
                    name="example3",
                    path="/tmp/mgit_tests/example3",
                    remotes={
                        "test": "example",
                        "test2": "example"
                        }
                    )

