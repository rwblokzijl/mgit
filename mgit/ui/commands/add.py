from mgit.ui.cli            import AbstractLeafCommand
from mgit.ui.cli_utils      import query_yes_no, path_relative_to_home
from mgit.ui.parsers        import RemoteParser
from mgit.ui.commands._mgit import MgitCommand
from mgit.local.state       import *
from typing                 import *

from pathlib import Path
import os

@MgitCommand.register
class CommandAdd(AbstractLeafCommand):
    command = "add"
    help="Create a new local/remote repo pair"

    def build(self, parser):
        parser.add_argument("name", help="Name of the project", nargs="?", default=None, type=str)
        parser.add_argument("--path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("--remotes", help="Name of remote repo", metavar="REMOTE[:REPO]", nargs="*", default=None, type=str)
        parser.add_argument("--tags", help="Categories for the repo", nargs="+", default=[], type=str)

        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')

    def assert_name_available(self, name: str):
        try:
            self.config.get_state(name=name)
            raise self.InputError(f"'{name}' already exists in the config")
        except self.config.ConfigError:
            pass

    def assert_remotes_available(self, remote_repos: Set[NamedRemoteRepo]):
        for remote_repo in remote_repos:
            if remote_repo.project_name in self.remote_system.list_remote(remote_repo.remote):
                raise self.InputError(f"'{remote_repo.project_name}' already exists in '{remote_repo.remote.name}'")

    def create_remotes(self, remote_repos: Set[NamedRemoteRepo]):
        for remote_repo in remote_repos:
            self.remote_system.init_repo(remote_repo)

    def run(self, y, name, path, remotes, tags):
        """ Prepares the details to init a repo """

        if not name:
            name = os.path.basename(Path('.').absolute())

        self.assert_name_available(name)

        # raise

        try:
            system_parent=self.system.get_state(Path(path))
            parent = self.config.get_state(system_parent)
        except (self.system.SystemError, self.config.ConfigError):
            parent=None

        new_state = RepoState(
                source="new repo",
                name=name,
                repo_id=None,
                path=path_relative_to_home(path),
                remotes=RemoteParser(self.config).parse(name, remotes),
                auto_commands=None,
                archived=None,
                tags=set(tags),
                parent=parent
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

