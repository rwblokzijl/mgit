from mgit.ui.ui import UI

from mgit.state.config_state_interactor  import ConfigStateInteractor
from mgit.state.system_state_interactor  import SystemStateInteractor
from mgit.state.general_state_interactor import GeneralStateInteractor

import argparse

from typing import Optional

from abc import ABC, abstractmethod

class AbstractCommand(ABC):
    command: Optional[str] = None
    help:    Optional[str] = None
    def __init__(self, *args, **kwargs):
        self.interactor = kwargs.get("interactor")
        self.config_state_interactor: ConfigStateInteractor = kwargs.get("config_state_interactor")
        self.system_state_interactor: SystemStateInteractor = kwargs.get("system_state_interactor")
        self.general_state_interactor: GeneralStateInteractor = kwargs.get("general_state_interactor")

        assert self.command is not None
        self.sub_commands = None
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

    def repo(self, parser):
        me = parser.add_mutually_exclusive_group()
        me.add_argument("-n", "--name", help="Process as name", type=str) # definitely name
        me.add_argument("-p", "--path", help="Process as path", type=str) # definitely path
        me.add_argument("repo", help="Name or path of the project", nargs="?", type=str) # try to infer
        return me

    def repo_or_all(self, parser):
        me = self.repo(parser)
        me.add_argument("-a", "--all", help="All repos in config", action="store_true") # all repos in config
        return me

    @abstractmethod
    def build(self, parser):
        pass

class CLI(UI):
    def __init__(self, command):
        self.command = command

    def run(self, args):
        return self.command.run(args=args)
        # self.map[args[0]](args[1:])

