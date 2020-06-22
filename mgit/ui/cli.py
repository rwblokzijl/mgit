from mgit.ui.ui import UI

import argparse

from abc import ABC, abstractmethod

class AbstractCommand(ABC):
    command = None
    help = None
    def __init__(self, interactor):
        self.interactor = interactor
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
        self.sub_commands = {c.command:c for c in self.get_sub_commands()}

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

