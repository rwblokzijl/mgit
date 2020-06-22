from mgit.repos.repos import Repo

import unittest
from unittest.mock import Mock

class TestRepo(unittest.TestCase):

    def test_init(self):
        Repo(
                "name",
                "path",
                "parent",
                "origin",
                "categories",
                "remotes"
                ,
                "archived",
                "repo_id",
                {}
                )

    def test_to_dict(self):
        github_dict = {
                "name" : "github",
                "url" : "git@github.com/Bloodyfool"
                }
        remote_github = Mock()
        remote_github.as_dict.return_value = github_dict

        home_dict = {
                "name" : "home",
                "url" : "bloodyfool@git.blokzijl.family:/test"
                }
        remote_home = Mock()
        remote_home.as_dict.return_value = home_dict

        name        = "repoName"
        path        = "~/sdf/sdf/sdf"
        parent      = Mock()
        parent.name = "test2"
        origin      = remote_home
        categories  = ["a", "b", "123"]
        remotes     = {
                "home" : remote_home,
                "github" : remote_github
                }
        archived    = False
        repo_id     = "asdf"

        expected = {
                "name":       "repoName",
                "path":       "~/sdf/sdf/sdf",
                "parent":     "test2",
                "origin":     home_dict,
                "categories": ["a", "b", "123"],
                "remotes":    {
                    "home":   home_dict,
                    "github": github_dict,
                    },
                "archived":   False,
                "repo_id":    "asdf"
                }

        as_dict = Repo(
                name,
                path,
                parent,
                origin,
                categories,
                remotes,
                archived,
                repo_id,
                {}).as_dict()

        self.maxDiff = None
        self.assertEqual(
                as_dict,
                expected
                )

    def test_to_dict_no_parent(self):
        github_dict = {
                "name" : "github",
                "url" : "git@github.com/Bloodyfool"
                }
        remote_github = Mock()
        remote_github.as_dict.return_value = github_dict

        home_dict = {
                "name" : "home",
                "url" : "bloodyfool@git.blokzijl.family:/test"
                }
        remote_home = Mock()
        remote_home.as_dict.return_value = home_dict

        name        = "repoName"
        path        = "~/sdf/sdf/sdf"
        parent      = None
        origin      = remote_home
        categories  = ["a", "b", "123"]
        remotes     = {
                "home" : remote_home,
                "github" : remote_github
                }
        archived    = False
        repo_id     = "asdf"

        expected = {
                "name":       "repoName",
                "path":       "~/sdf/sdf/sdf",
                "origin":     home_dict,
                "categories": ["a", "b", "123"],
                "remotes":    {
                    "home":   home_dict,
                    "github": github_dict,
                    },
                "archived":   False,
                "repo_id":    "asdf"
                }

        as_dict = Repo(
                name,
                path,
                parent,
                origin,
                categories,
                remotes ,
                archived,
                repo_id,
                {}
                ).as_dict()

        self.maxDiff = None
        self.assertEqual(
                as_dict,
                expected
                )

