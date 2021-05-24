from mgit.ui.base_commands  import SingleRepoCommand
from mgit.ui.commands._mgit import MgitCommand
from mgit.ui.cli_utils      import query_yes_no

from mgit.local.state import *

from copy    import deepcopy
from pathlib import Path
import sys

from typing import *

T = TypeVar('T')

@MgitCommand.register
class CommandUpdate(SingleRepoCommand):
    command = "update"
    help="Updates the config based on the system or vice versa"

    combine = False

    def build(self, parser):
        parser.add_argument("-c", "--config", help="Update the config based on the system", action="store_true")
        parser.add_argument("-s", "--system", help="Update the system based on the config", action="store_true")

        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')

    def one_or_other(self, config, system):
        # One is missing
        if config is None:
            return system
        return config

    def merge_vals(self, config: Optional[T], system: Optional[T]) -> Optional[T]:
        if config is None or system is None:
            return self.one_or_other(config, system)
        # Both exist
        if config != system:
            raise ValueError(f"{config} != {system}")
        return config

    def merge_parents(self, config: Optional[RepoState], system: Optional[RepoState]):
        if config is None or system is None:
            return self.one_or_other(config, system)
        # Both exist
        return self.merge(config, system)

    def _remove_existing(self, remote_repos, merged, key):
        for rr in list(remote_repos):
            for m in merged:
                if key(rr) == key(m):
                    remote_repos.remove(rr)
                    break

    def _add(self, remote_repo: RemoteRepo, result: Set[RemoteRepo]):
        for rr in result:
            if remote_repo.name == rr.name:
                return
            if remote_repo.url == rr.url:
                return
        result.add(remote_repo)

    def _merge_same_remotes(self, config: Set[RemoteRepo], system: Set[RemoteRepo], result: Set[RemoteRepo]):
        for con_r in list(config):
            for sys_r in list(system):
                if con_r == sys_r:
                    config -= {con_r}
                    system -= {sys_r}
                    self._add(con_r, result)

    def _merge_same_urls(self, config: Set[RemoteRepo], system: Set[RemoteRepo], result: Set[RemoteRepo]):
        for con_r in list(config):
            for sys_r in list(system):
                if con_r.url == sys_r.url:
                    config -= {con_r}
                    system -= {sys_r}
                    self._add(con_r, result) # use the config url

    def _merge_same_names(self, config: Set[RemoteRepo], system: Set[RemoteRepo], result: Set[RemoteRepo]):
        for con_r in list(config):
            for sys_r in list(system):
                if con_r.name == sys_r.name:
                    config -= {con_r}
                    system -= {sys_r}
                    sys.stderr.write(f"WARNING: Two remotes with the same name: {sys_r}, {con_r}\n")
                    self._add(con_r, result) # use the system url

    def _remove_duplicates(self, config, system, merged):
        self._remove_existing(config, merged, lambda x: x.url)
        self._remove_existing(system, merged, lambda x: x.url)
        self._remove_existing(config, merged, lambda x: x.name)
        self._remove_existing(system, merged, lambda x: x.name)

    def _merge_remaining(self, config, system, result):
        for c in list(config):
            config.remove(c)
            self._add(c, result)
        for s in list(system):
            system.remove(s)
            self._add(s, result)

    def merge_remotes(self, config: Set[RemoteRepo], system: Set[RemoteRepo]):
        config = deepcopy(config)
        system = deepcopy(system)

        system = {self.config.resolve_remote(r,True) for r in system}

        result: Set[RemoteRepo] = set()

        self._merge_same_remotes( config, system, result)
        self._merge_same_names(   config, system, result)
        self._merge_same_urls(    config, system, result)
        self._merge_remaining(    config, system, result)

        assert not config, config
        assert not system, system

        return result

    def relative_to_home(self, path: Path):
        if not path.expanduser().is_absolute():
            raise ValueError(f"{path} is relative")
        elif str(path.expanduser()).startswith(str(Path("~").expanduser())):
            return Path("~") / path.expanduser().relative_to(Path("~").expanduser())
        else:
            return path

    def merge_paths(self, config: Optional[Path], system: Optional[Path]):
        if config:
            config = self.relative_to_home(config)
        if system:
            system = self.relative_to_home(system)
        return self.merge_vals(config, system)

    def merge(self, config_state: RepoState, system_state: RepoState):
        return RepoState(
                source        = "",
                name          = self.merge_vals(config_state.name, system_state.name),
                repo_id       = self.merge_vals(config_state.repo_id, system_state.repo_id),
                path          = self.merge_paths(config_state.path, system_state.path),
                parent        = self.merge_parents(config_state.parent, system_state.parent),
                remotes       = self.merge_remotes(config_state.remotes, system_state.remotes),
                auto_commands = None,
                archived      = self.merge_vals(config_state.archived, system_state.archived),
                categories    = (config_state.categories or set()) | (system_state.categories or set())
                )

    def run(self, config_state, system_state, config, system, y):
        if not (config or system): # if none then both
            config = True
            system = True
        repo_state = self.merge(config_state, system_state)
        if config:
            print(f"old config={config_state.represent()}")
        if system:
            print(f"old system={system_state.represent()}")
        if not y and not query_yes_no(
                "Do you want to update with the following values: \n" +
                f"name={repo_state.represent()}"):
            return "Doing nothing"

        if config and system:
            self.config.set_state(repo_state)
            self.system.set_state(repo_state)
        elif system:
            self.system.set_state(repo_state)
        elif config:
            self.config.set_state(repo_state)
        return repo_state

