from mgit.ui.cli import CLI
from mgit.interactor import Builder
from mgit.ui.commands.commands import MgitCommand

from mgit.state.config_state_interactor import ConfigStateInteractor
from mgit.state.system_state_interactor import SystemStateInteractor
from mgit.state.general_state_interactor import GeneralStateInteractor
from mgit.state.state import RepoState

import sys
import collections
import six
import dataclasses

def is_iterable(arg):
    return ( isinstance(arg, collections.Iterable) and not isinstance(arg, six.string_types))

def pretty_string(data, indent=0, step=2):
    ans = ""
    if isinstance(data, RepoState):
        ans += data.represent(indent, step=2) + '\n'
    elif isinstance(data, dict):
        for key, value in data.items():
            if '\n' not in pretty_string(value).strip():
                ans += ' ' * (indent) + str(key) + " = " + str(value or "") + '\n'
            else:
                ans += ' ' * (indent) + str(key) + ":" + '\n'
                ans += pretty_string(value, indent=indent+step, step=step) + '\n'
    elif is_iterable(data):
        for value in data:
            ans += pretty_string(value, indent=indent, step=step) + '\n'
    elif data is None:
        pass
    else:
        ans += ' ' * (indent) + str(data) + "\n"
    return ans.strip('\n')

def pperror(error):
    print(error, file=sys.stderr)

def main(repos_config, remotes_config, args=None, silent=False):
    # The interactor performs the business logic
    interactor = Builder().build(
                repos_config   = repos_config,
                remotes_config = remotes_config
                )
    config_state_interactor = ConfigStateInteractor(
            remotes_file = remotes_config,
            repos_file   = repos_config,
            )
    system_state_interactor = SystemStateInteractor()
    general_state_interactor = GeneralStateInteractor(
            config_state_interactor=config_state_interactor,
            system_state_interactor=system_state_interactor
            )
    # The CLI ui handles argparse and calls the interactor
    ui = CLI(MgitCommand(
        interactor=interactor,
        config_state_interactor=config_state_interactor,
        system_state_interactor=system_state_interactor,
        general_state_interactor=general_state_interactor
        ))
    out = ui.run(args)
    if out and not silent:
        print(pretty_string(out))
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

