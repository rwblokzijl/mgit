from mgit.state.state import RepoState, RemoteRepo, NamedRemoteRepo, UnnamedRemoteRepo, Remote, AutoCommand, RemoteBranch, LocalBranch, RemoteType

from pathlib import Path
from git import Repo

import unittest

class TestState(unittest.TestCase):

    """
    AutoCommand
    RemoteBranch
    LocalBranch
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_nothing(self):
        pass

    def test_repo(self):
        n_repo = NamedRemoteRepo(
                project_name="name",
                remote=Remote(
                            name="remote_name",
                            url='url',
                            path='path',
                            remote_type=RemoteType.SSH))
        u_repo = UnnamedRemoteRepo(
                remote_name="remote_name",
                url="url")
        RepoState(   repo_id="ID",
                source="none",
                name="name",
                path="path",
                # origin=n_repo,
                archived=False,
                categories=[],
                remotes=[ n_repo, u_repo ],
                auto_commands=[
                    AutoCommand(
                        local_branch=LocalBranch(ref="master"),
                        remote_branches=[
                            RemoteBranch(
                                remote_repo=n_repo,
                                ref="master"
                                )
                            ],
                        )
                    ],
                parent=None)

    def test_compare_remote_repos(self):
        self.assertTrue(
                UnnamedRemoteRepo(
                    remote_name="remote_name",
                    url="the_url.com:/kek"
                    ).compare(
                        NamedRemoteRepo(
                            project_name="kek",
                            remote=Remote(
                                name="remote_name",
                                url="the_url.com",
                                path="/",
                                remote_type=RemoteType.SSH
                                ))
                    ))

    def test_add_repo_state_add(self):
        n_repo = NamedRemoteRepo(
                project_name="name",
                remote=Remote(
                            name="remote_name",
                            url='url',
                            path='path',
                            remote_type=RemoteType.SSH)
                )

        u_repo = UnnamedRemoteRepo(
                remote_name="remote_name",
                url="url:path/name")

        parent=RepoState(
            source="config",
            repo_id="id2",
            name="parent",
            path=Path("parentPath"),
            # origin=None,
            archived=False,
            categories={"1"},
            remotes=set(),
            auto_commands=None,
            parent=None
            )

        self.assertTrue(
                u_repo.compare(
                n_repo)
                )

        con_repo = RepoState(
                source="config",
                repo_id="ID",
                name="name",
                path=Path("path1"),
                # origin=n_repo,
                archived=False,
                categories={"2", "3"},
                remotes={n_repo},
                auto_commands=[],
                parent=parent
                )

        sys_repo = RepoState(
                source="system",
                repo_id="ID",
                name=None,
                path=Path("path1"),
                # origin=u_repo,
                archived=None,
                categories=None,
                remotes={u_repo},
                auto_commands=None,
                parent=None
                )

        compare = sys_repo.compare(con_repo)
        self.assertEqual(
                compare,
                []
                )

        comb1 = sys_repo + con_repo
        comb2 = con_repo + sys_repo

        self.assertEqual(comb1, comb2)

        self.assertIsInstance(comb1, RepoState)
        self.assertIsInstance(comb2, RepoState)

        self.assertEqual( comb1.parent, parent)
        self.assertEqual( comb1.repo_id, "ID")
        self.assertEqual( comb1.name, "name")
        self.assertEqual( comb1.path, Path("path1"))
        # self.assertIsInstance( comb1.origin, NamedRemoteRepo)
        # self.assertIsInstance( comb2.origin, NamedRemoteRepo)
        self.assertEqual( comb1.archived, False)
        self.assertEqual( comb2.archived, False)
        self.assertEqual( len(comb1.remotes), 1)
        self.assertIsInstance( list(comb1.remotes)[0], NamedRemoteRepo)
        self.assertEqual( len(comb2.remotes), 1)
        self.assertIsInstance( list(comb2.remotes)[0], NamedRemoteRepo)
        self.assertEqual( comb1.categories, {"2", "3"})
        self.assertEqual( comb2.categories, {"2", "3"})

    # def test_ref(self):
    #     reader = Repo("~/devel/mgit").config_reader()
    #     remote = reader.sections()[2]
    #     for k, v in reader.items_all(remote):
    #         print(k, v)

    def test_subpath(self):
        remote=Remote(
                    name="remote_name",
                    url='url',
                    path='path',
                    remote_type=RemoteType.SSH)

        n_repo = NamedRemoteRepo(
                project_name="name",
                remote=remote
                )

        u_repo = UnnamedRemoteRepo(
                remote_name="remote_name",
                url="url:path/name")

        self.assertIn(n_repo, remote)
        self.assertIn(u_repo, remote)

        u_repo = UnnamedRemoteRepo(
                remote_name="remote_name",
                url="url:pathh/name")

        self.assertNotIn(u_repo, remote)
