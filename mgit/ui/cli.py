from mgit.state.config_state_interactor  import ConfigStateInteractor
from mgit.state.system_state_interactor  import SystemStateInteractor
from mgit.state.general_state_interactor import GeneralStateInteractor
from mgit.state.local_system_interactor  import LocalSystemInteractor
from mgit.state.remote_interactor        import RemoteInteractor

import argparse

from typing import Optional, List, Type, Dict

from abc import ABC, abstractmethod

class AbstractCommand(ABC):
    command: Optional[str] = None
    help:    Optional[str] = None
    def __init__(self,
        config_state_interactor:ConfigStateInteractor,
        system_state_interactor:SystemStateInteractor,
        general_state_interactor:GeneralStateInteractor,
        local_system_interactor:LocalSystemInteractor,
        remote_interactor:RemoteInteractor
            ):
        self.config_state_interactor:  ConfigStateInteractor  = config_state_interactor
        self.system_state_interactor:  SystemStateInteractor  = system_state_interactor
        self.general_state_interactor: GeneralStateInteractor = general_state_interactor
        self.local_system_interactor:  LocalSystemInteractor  = local_system_interactor
        self.remote_interactor:        RemoteInteractor       = remote_interactor

        assert self.command is not None
        self.sub_commands = None

    @abstractmethod
    def build(self, parser):
        pass

    @abstractmethod
    def run_command(self, args):
        raise self.NotImplementedError("This feature is not yet implemented")

    def _has_run(self):
        run = getattr(self, "run", None)
        if callable(run):
            return True
        return False

    class NotImplementedError(Exception):
        pass

class AbstractNodeCommand(AbstractCommand):
    command_classes: Dict[int, List[Type[AbstractCommand]]] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_commands = self._init_child_commands(*args, **kwargs)
        self.unique_key = str(id(self))

    def _init_child_commands(self, *args, **kwargs):
        return { COMMAND_CLASS.command:COMMAND_CLASS(*args, **kwargs)
                for COMMAND_CLASS in self._get_commands() }

    @classmethod
    def _get_commands(cls):
        return cls.command_classes.get(id(cls), [])

    @classmethod
    def register(cls, COMMAND_CLASS):
        "Meant to be consumed as a decorator"
        # We store the classes as a list PER AbstractNodeCommand class
        # This is neccesary because command_classes is a static variable shared among all AbstractNodeCommand
        if not cls.command_classes.get(id(cls)):
            cls.command_classes[id(cls)] = []
        cls.command_classes[id(cls)].append(COMMAND_CLASS)
        return COMMAND_CLASS

    def build(self, parser):
        if not self.sub_commands and not self._has_run():
            raise self.NotImplementedError("This feature has no subcommands and no run function")
        subparsers = parser.add_subparsers(dest=self.unique_key, metavar=self.command)
        if not self._has_run():
            subparsers.required = True
        for command in self.sub_commands.values():
            p = subparsers.add_parser(command.command, help=command.help)
            command.build(p)

    def run_command(self, args):
        command = args.pop(self.unique_key)
        if command:
            obj = self.sub_commands.get(command, None)
            return obj.run_command(args)
        elif self._has_run():
            return self.run(**args) # pylint: disable=E1101 # error says run doesn't exist, it will
        raise self.NotImplementedError("This feature is not yet implemented")

class AbstractLeafCommand(AbstractCommand):
    def repo_by_path_name_or_infer(self, parser):
        me_group = parser.add_mutually_exclusive_group()
        me_group.add_argument("-n", "--name", help="Process as name", type=str) # if set: definitely name
        me_group.add_argument("-p", "--path", help="Process as path", type=str) # if set: definitely path
        me_group.add_argument("repo", help="Name or path of the project", nargs="?", type=str) # else: try to infer
        return me_group

    def repo_by_path_name_or_infer_or_all(self, parser):
        me_group = self.repo_by_path_name_or_infer(parser)
        me_group.add_argument("-a", "--all", help="All repos in config", action="store_true") # all repos in config
        return me_group

    @abstractmethod
    def build(self, parser):
        pass

    @abstractmethod
    def run(self, **args):
        pass

    def run_command(self, args):
        return self.run(**args)

class CLI:
    def __init__(self, command):
        self.command = command

    def run(self, args):
        return self.command.run(args=args)
        # self.map[args[0]](args[1:])

