from mgit.ui.cli import AbstractNodeCommand

import argparse

class MgitCommand(AbstractNodeCommand):
    command = "mgit"

    def run(self, args):
        parser = argparse.ArgumentParser()
        self.build(parser)
        pargs = parser.parse_args(args)
        return self.run_command(dict(vars(pargs)))
