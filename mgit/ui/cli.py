from mgit.ui.ui import UI

from mgit.state.config_state_interactor import ConfigStateInteractor
from mgit.state.system_state_interactor import SystemStateInteractor

import argparse

from typing import *

from abc import ABC, abstractmethod

class AbstractCommand(ABC):
    command: Optional[str] = None
    help:    Optional[str] = None
    def __init__(self, *args, **kwargs):
        self.interactor = kwargs.get("interactor")
        self.config_state_interactor: ConfigStateInteractor = kwargs.get("config_state_interactor")
        self.system_state_interactor: SystemStateInteractor = kwargs.get("system_state_interactor")

        assert self.command is not None
        self.unique_key = str(id(self))

    @abstractmethod
    def build(self, parser):
        pass

    def run_command(self, args):
        if self.unique_key in args:
            command = args.pop(self.unique_key)
            obj = self.sub_commands.get(command, None)
            return obj.run_command(args)
        else:
            raise self.NotImplementedError("This feature is not yet implemented")

    class NotImplementedError(Exception):
        pass

class AbstractNodeCommand(AbstractCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_commands = {COMMAND_CLASS.command:COMMAND_CLASS(*args, **kwargs) for COMMAND_CLASS in self.get_sub_commands()}

    @abstractmethod
    def get_sub_commands(self):
        pass

    def build(self, parser):
        subparsers = parser.add_subparsers(dest=self.unique_key, metavar=self.command)
        subparsers.required = True
        for command in self.sub_commands.values():
            p = subparsers.add_parser(command.command, help=command.help)
            command.build(p)

    class ParseError(Exception):
        pass

class AbstractLeafCommand(AbstractCommand):
    @abstractmethod
    def build(self, parser):
        pass

class CLI(UI):
    def __init__(self, command):
        self.command = command

    def run(self, args):
        return self.command.run(args=args)
        # self.map[args[0]](args[1:])

