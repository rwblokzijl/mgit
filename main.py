from mgit.ui.cli import CLI
from mgit.interactor import Builder
from mgit.ui.commands.commands import MgitCommand

import sys
# import inspect
# import itertools
import collections
import six

def is_iterable(arg):
    return ( isinstance(arg, collections.Iterable) and not isinstance(arg, six.string_types))

def pprint(to_print, indent=0, step=2):
    if isinstance(to_print, dict):
        for key, value in to_print.items():
            print(' ' * (indent) + str(key))
            pprint(value, indent=indent+step, step=step)
    elif is_iterable(to_print):
        for value in to_print:
            pprint(value, indent=indent, step=step)
    elif to_print is None:
        pass
    else:
        print(' ' * (indent) + str(to_print))

def pperror(error):
    print(error, file=sys.stderr)

def main(repos_config, remotes_config, args=None, silent=False):
    # The interactor performs the business logic
    interactor = Builder().build(
                repos_config   = repos_config,
                remotes_config = remotes_config
                )
    # The CLI ui handles argparse and calls the interactor
    ui = CLI(MgitCommand(interactor))
    out = ui.run(args)
    if out and not silent:
        pprint(out)
    return out

def main_cli(*args, **kwargs):
    try:
        main(*args, **kwargs)
        return 0
    except Exception as e:
        if str(e):
            pperror(e)
            raise e
        return 1

