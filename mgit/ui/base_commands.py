from mgit.ui.cli import AbstractLeafCommand
from typing      import *
from mgit.local.state  import *

class AbstractMgitCommand(AbstractLeafCommand):
    """
    Base class for all special mgit commands
    """
    combine         = True
    config_required = True
    system_required = True

    def __init__(self, *args, **kwargs):
        self.args = []
        super().__init__(*args, **kwargs)

    @abstractmethod
    def pre_build(self):
        pass

    @abstractmethod
    def post_parse(self, args):
        pass

    def build_decorator(self, func):
        def wrapper(parser):
            self._parser = parser
            self.pre_build()
            return func(self, parser)
        return wrapper

    def add_argument(self, *args, add_to=None, **kwargs):
        if add_to is None:
            self._parser.add_argument(*args, **kwargs)
        else:
            add_to.add_argument(*args, **kwargs)
        self.args.append(kwargs['dest']) #dest must be specified

    def __getattribute__(self, name):
        if name == "build":
            func = getattr(type(self), "build")
            return self.build_decorator(func)
        else:
            return object.__getattribute__(self, name)

    def run_command(self, args):
        args_to_pass = {k:v for k, v in args.items() if k in self.args}
        args = {k:v for k, v in args.items() if k not in self.args}
        new_args = self.post_parse(**args_to_pass)
        for arg, val in new_args.items():
            assert arg not in args, f"'{arg}' already in args"
            args[arg] = val

        return self.run(**args)

class MgitBaseCommand(AbstractMgitCommand):
    """
    This is the base class for all special mgit commands
    """
    def _get_config(self, name) -> Optional[RepoState]:
        try:
            return self.config.get_state(name=name)
        except self.config.ConfigError as e:
            if self.config_required:
                raise e
            return None

    def _get_system(self, path):
        try:
            return self.system.get_state(path=path)
        except self.system.SystemError as e:
            if self.system_required:
                raise e
            return None

    def _get_config_from_system(self, system_state) -> Optional[RepoState]:
        config_state = None
        if system_state.repo_id:
            try:
                return self.config.get_state(repo_id=system_state.repo_id)
            except self.config.ConfigError:
                pass
        try:
            return self.config.get_state(path=system_state.path)
        except self.config.ConfigError as e:
            if self.config_required:
                raise e
        return config_state

    def _get_system_from_config(self, config_state) -> Optional[RepoState]:
        if not config_state.path:
            if self.config_required:
                raise ValueError(f"'{config_state.name}'' doesn't specify a path")
            return None
        else:
            try:
                return self.system.get_state(path=config_state.path)
            except self.system.SystemError as e:
                if self.system_required:
                    raise e
                return None
            return None

    def get_both_from_name(self, name) -> Tuple[Optional[RepoState], Optional[RepoState]]:
        config_state = self._get_config(name)
        system_state = self._get_system_from_config(config_state)
        return config_state, system_state

    def get_both_from_path(self, path) -> Tuple[Optional[RepoState], Optional[RepoState]]:
        system_state = self._get_system(path)
        config_state = self._get_config_from_system(system_state)
        return config_state, system_state

class SingleRepoCommand(MgitBaseCommand):
    """
    Base command for all commands that take a single repo
    """
    def pre_build(self):
        me_group = self._parser.add_mutually_exclusive_group()
        self.add_argument("-n", "--name", add_to=me_group, dest="MGIT_NAME", metavar="NAME", help="Name of the repo") # if set: definitely name
        self.add_argument("-p", "--path", add_to=me_group, dest="MGIT_PATH", metavar="PATH", help="Path of the repo") # if set: definitely path
        return me_group

    def _get_repo_states(self, MGIT_NAME, MGIT_PATH):
        if MGIT_NAME:
            config_state, system_state = self.get_both_from_name(MGIT_NAME)
        else:
            config_state, system_state = self.get_both_from_path(MGIT_PATH or ".")
        return config_state, system_state

    def post_parse(self, MGIT_NAME, MGIT_PATH): #type: ignore # idfk how to solve the error
        config_state, system_state = self._get_repo_states(MGIT_NAME, MGIT_PATH)

        if self.combine:
            if config_state and system_state:
                repo_state = config_state + system_state
            else:
                repo_state = config_state or system_state
            return {'repo_state': repo_state}
        else:
            return {'config_state': config_state, 'system_state': system_state}

class MultiRepoCommand(MgitBaseCommand):
    """
    Base command for all commands that take multple repos

    This class will set up all required arguments and return them as a list of repo_states
    """
    def pre_build(self):
        group    = self._parser.add_argument_group('repos')
        self.add_argument("-n", "--name", add_to=group, dest="MGIT_NAMES", metavar="NAME", action="append", default=[], help="Name of the repo") # if set: definitely name
        self.add_argument("-p", "--path", add_to=group, dest="MGIT_PATHS", metavar="PATH", action="append", default=[], help="Path of the repo") # if set: definitely path
        self.add_argument("-a", "--all",  add_to=group, dest="MGIT_ALL", help="All repos in config", action="store_true") # all repos in config

    def post_parse(self, MGIT_NAMES, MGIT_PATHS, MGIT_ALL):
        if MGIT_ALL:
            return {'all': True, 'repo_states': None}
        else:
            repo_states  = [self.get_both_from_name(name) for name in MGIT_NAMES]
            repo_states += [self.get_both_from_path(path) for path in MGIT_PATHS]
            if not repo_states:
                repo_states += [self.get_both_from_path(".")]
            if self.combine:
                repo_states = [config + system for config, system in repo_states]
            return {'all': False, 'repo_states': repo_states}
