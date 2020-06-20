from mgit.repos.repos import Repo
from mgit.repos.repo_remotes import DerivedRepoRemote
from mgit.repos.repo_remotes import UnnamedRepoOrigin

import unittest
from unittest.mock import Mock

class TestDerivedRepoRemote(unittest.TestCase):
    def setUp(self):
        self.remote_mock = Mock()
        self.remote_mock.get_url.return_value = "bloodyfool@git.bloodyfool.family"
        self.drr = DerivedRepoRemote(self.remote_mock, "repo")

    def test_init(self):
        DerivedRepoRemote(Mock(), "repo")

    def test_get_url(self):
        self.remote_mock.get_url.return_value = "remote"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        url = drr.get_url()

        self.assertEqual("remote/repo", url)

    def test_get_relative_url(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        url = drr.get_url()

        self.assertEqual("bloodyfool@git.blokzijl.family:repo", url)

    def test_get_absolute_url(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:"
        drr = DerivedRepoRemote(self.remote_mock, "/repo")
        url = drr.get_url()

        self.assertEqual("bloodyfool@git.blokzijl.family:/repo", url)

    def test_get_relative_to_relative_url(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:/test/kek"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        url = drr.get_url()

        self.assertEqual("bloodyfool@git.blokzijl.family:/test/kek/repo", url)

    def test_get_relative_to_relative_url_trailing(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:/test/kek/"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        url = drr.get_url()

        self.assertEqual("bloodyfool@git.blokzijl.family:/test/kek/repo", url)

    def test_get_relative_to_relative_url_trailing(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:/test/kek/"
        with self.assertRaises(DerivedRepoRemote.InvalidPathError):
            DerivedRepoRemote(self.remote_mock, "/repo")

    def test_get_name(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:/test/kek/"
        self.remote_mock.name = "home"
        drr = DerivedRepoRemote(self.remote_mock, "repo")
        self.assertEqual(
                "home",
                drr.get_name()
                )

    def test_as_dict(self):
        self.remote_mock.get_url.return_value = "bloodyfool@git.blokzijl.family:/test/kek/"
        self.remote_mock.name = "home"
        drr = DerivedRepoRemote(self.remote_mock, "repo")

        self.assertDictEqual(
                {
                    "name": "home",
                    "url" : "bloodyfool@git.blokzijl.family:/test/kek/repo"
                    },
                drr.as_dict())

class TestUnnamedRepoOrigin(unittest.TestCase):
    def test_init(self):
        UnnamedRepoOrigin("urlll")

    def test_get_url(self):
        url = "urlll"
        self.assertEqual(
                url,
                UnnamedRepoOrigin(url).get_url()
                )

        url = "urlll2"
        self.assertEqual(
                url,
                UnnamedRepoOrigin(url).get_url()
                )

    def test_get_name(self):
        urr = UnnamedRepoOrigin("urlll")
        self.assertEqual(
                "origin",
                urr.get_name()
                )

    def test_as_dict(self):
        urr = UnnamedRepoOrigin("urlll")
        self.assertDictEqual(
                {
                    "name": "origin",
                    "url" : "urlll"
                    },
                urr.as_dict())
