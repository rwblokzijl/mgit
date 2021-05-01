from mgit.state             import RepoState, RemoteRepo, NamedRemoteRepo
from mgit.ui.cli            import AbstractLeafCommand
from mgit.ui.cli_utils      import query_yes_no
from mgit.ui.commands._mgit import MgitCommand

from typing import List, Sequence, Set, Iterable

from pathlib import Path
import os

@MgitCommand.register
class CommandInit(AbstractLeafCommand):
    command = "init"
    help="Create a new local/remote repo pair"

    def remote_repo(self, s):
        if ":" in s:
            return s.split(":", 1)
        else:
            return s, None

    def build(self, parser):
        parser.add_argument("name", help="Name of the project", nargs="?", default=None, type=str)
        parser.add_argument("--path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("--remotes", help="Name of remote repo", metavar="REMOTE[:REPO]", nargs="?", default=None, type=lambda x: self.remote_repo(x))
        parser.add_argument("--categories", help="Categories for the repo", nargs="+", default=[], type=str)

        # TODO: what to do with origin gets removed??
        # parser.add_argument("--origin", help="Name of remote to be default push", metavar="REMOTE", type=lambda x: self.remote_repo(x))

        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')

    def assert_path_available(self, path: Path):
        existing_system_state = self.system_state_interactor.get_state(path=path)
        if (existing_system_state and
                existing_system_state.path is not None and
                existing_system_state.path.absolute == path.absolute):
            raise self.InputError(f"'{path}' is already a git repo use 'mgit add' instead")

    def assert_name_available(self, name: str):
        existing_config_state = self.config_state_interactor.get_state(name=name)
        if existing_config_state:
            raise self.InputError(f"'{name}' already exists in the config")

    def _split_remote_and_repo(self, default_name:str, remote_repo_name:str):
        if ':' in remote_repo_name:
            return remote_repo_name.split(":")
        else:
            return remote_repo_name, default_name

    def parse_remote_input(self, default_name: str, remote_repo_name: str) -> NamedRemoteRepo:
        remote_name, name = self._split_remote_and_repo(default_name, remote_repo_name)
        remote = self.config_state_interactor.get_remote(remote_name)
        if not remote:
            raise self.InputError(f"'{remote_name}' is not a known remote")
        return NamedRemoteRepo(remote=remote, project_name=name)

    def _get_default_remote_repos(self, name: str) -> Set[NamedRemoteRepo]:
        remotes = self.config_state_interactor.get_default_remotes()
        remote_repos = {NamedRemoteRepo(remote=remote, project_name=name) for remote in remotes}
        return remote_repos

    def _path_relative_to_home(self, path):
        try:
            return Path("~") / Path(path).absolute().relative_to(Path('~').expanduser())
        except:
            return Path(path).absolute()

    def resolve_remotes(self, default_name, remote_names) -> Set[NamedRemoteRepo]:
        # TODO: Allow UnnamedRemoteRepo?
        if remote_names is None:
            return self._get_default_remote_repos(default_name)
        return {self.parse_remote_input(default_name, remote) for remote in remote_names}

    def assert_remotes_available(self, remote_repos: Set[NamedRemoteRepo]):
        for remote_repo in remote_repos:
            if remote_repo.project_name in self.remote_interactor.list_remote(remote_repo.remote):
                raise self.InputError(f"'{remote_repo.project_name}' already exists in '{remote_repo.remote.name}'")

    def create_remotes(self, remote_repos: Set[NamedRemoteRepo]):
        for remote_repo in remote_repos:
            self.remote_interactor.init_repo(remote_repo)

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
                path=self._path_relative_to_home(path),
                remotes=self.resolve_remotes(name, remotes),
                auto_commands=None,
                archived=None,
                categories=set(categories),
                parent=self.system_state_interactor.get_state(Path(path))
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
        self.system_state_interactor.set_state(new_state, init=True)

        yield "Adding to config"
        self.config_state_interactor.set_state(new_state)

        yield "Done"

        if new_state.parent:
            yield "TODO: register new submodule for parent"

