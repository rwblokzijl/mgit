from mgit.ui.cli               import CLI
from mgit.ui.commands._mgit import MgitCommand

from mgit.printing import pretty_string

from mgit.config_state_interactor  import ConfigStateInteractor
from mgit.system_state_interactor  import SystemStateInteractor
from mgit.general_state_interactor import GeneralStateInteractor
from mgit.local_system_interactor  import LocalSystemInteractor
from mgit.remote_interactor        import RemoteInteractor

from pathlib import Path

import sys

def import_commands():
    """
    Imports all files in mgit.ui.commands.*

    This allows the registering of an argparse command with the @ParentNode.register decorator
    """
    import os
    import importlib

    current_dir = Path(__file__).parent
    files = [p for p in (current_dir / "ui/commands").rglob("*.py") if os.path.isfile(p) and not str(p).endswith("__init__.py")]
    modules = [str(m.relative_to(current_dir.parent))[:-3].replace('/', '.') for m in files]
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            print(f"Module: {module}")
            raise e

import_commands()

def main(repos_config, remotes_config, args=None):
    config_state_interactor = ConfigStateInteractor(
            remotes_file = remotes_config,
            repos_file   = repos_config,
            )
    local_system_interactor = LocalSystemInteractor()
    remote_interactor = RemoteInteractor()
    system_state_interactor = SystemStateInteractor()
    general_state_interactor = GeneralStateInteractor(
            config_state_interactor = config_state_interactor,
            system_state_interactor = system_state_interactor,
            local_system_interactor = local_system_interactor,
            remote_interactor       = remote_interactor,
            )
    ui = CLI(MgitCommand(
        config_state_interactor=config_state_interactor,
        system_state_interactor=system_state_interactor,
        general_state_interactor=general_state_interactor,
        local_system_interactor = local_system_interactor,
        remote_interactor       = remote_interactor,
        ))
    return ui.run(args)

def main_cli(*args, **kwargs):
    try:
        out = main(*args, **kwargs)
        if out is not None:
            for step in pretty_string(out): # is a generator
                print(step)
        return 0
    except Exception as e:
        if str(e):
            print(e, file=sys.stderr)
            raise e #TODO remove when done
        return 1

