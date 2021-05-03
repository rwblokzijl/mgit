from mgit.state              import RepoState, RemoteRepo, NamedRemoteRepo
from mgit.ui.cli             import AbstractLeafCommand
from mgit.ui.cli_utils       import query_yes_no, path_relative_to_home
from mgit.ui.parsers         import RemoteParser
from mgit.ui.commands._mgit  import MgitCommand

from typing import List, Sequence, Set, Iterable

from pathlib import Path
import os

@MgitCommand.register
class CommandInit(AbstractLeafCommand):
    command = "init"
    help="Create a new local/remote repo pair"

    def build(self, parser):
        parser.add_argument("name", help="Name of the project", nargs="?", default=None, type=str)
        parser.add_argument("--path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("--remotes", help="Name of remote repo", metavar="REMOTE[:REPO]", nargs="*", default=None, type=str)
        parser.add_argument("--categories", help="Categories for the repo", nargs="+", default=[], type=str)

        # TODO: what to do with origin gets removed??
        # parser.add_argument("--origin", help="Name of remote to be default push", metavar="REMOTE", type=lambda x: self.type_remote_repo(x))

        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')

    def assert_path_available(self, path: Path):
        existing_system_state = self.system.get_state(path=path)
        if (existing_system_state and
                existing_system_state.path is not None and
                existing_system_state.path.absolute == path.absolute):
            raise self.InputError(f"'{path}' is already a git repo use 'mgit add' instead")

    def assert_name_available(self, name: str):
        existing_config_state = self.config.get_state(name=name)
        if existing_config_state:
            raise self.InputError(f"'{name}' already exists in the config")

    def assert_remotes_available(self, remote_repos: Set[NamedRemoteRepo]):
        for remote_repo in remote_repos:
            if remote_repo.project_name in self.remote_system.list_remote(remote_repo.remote):
                raise self.InputError(f"'{remote_repo.project_name}' already exists in '{remote_repo.remote.name}'")

    def create_remotes(self, remote_repos: Set[NamedRemoteRepo]):
        for remote_repo in remote_repos:
            self.remote_system.init_repo(remote_repo)

    def run(self, y=False, name=None, path='.', remotes=None, categories=[]):
        """ Prepares the details to init a repo """

        if not name:
            name = os.path.basename(Path('.').absolute())

        self.assert_name_available(name)
        self.assert_path_available(Path(path))

        new_state = RepoState(
                source="new repo",
                name=name,
                repo_id=None,
                path=path_relative_to_home(path),
                remotes=RemoteParser(self.config).parse(name, remotes),
                auto_commands=None,
                archived=None,
                categories=set(categories),
                parent=self.system.get_state(Path(path))
                )

        if not y and not query_yes_no(f"Do you want to init with the following values: \n name={new_state.represent()}"):
            return "Doing nothing"

        self.assert_remotes_available(new_state.remotes)

        return self.init_repo(new_state)

    def init_repo(self, new_state):
        yield "Creating remote repos"
        self.create_remotes(new_state.remotes)

        # yield "Adding submodule to parent"
        yield "Creating local repo"
        self.system.set_state(new_state, init=True)

        yield "Adding to config"
        self.config.set_state(new_state)

        yield "Done"

        if new_state.parent:
            yield "TODO: register new submodule for parent"

