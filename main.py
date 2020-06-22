from mgit.ui.cli import CLI
from mgit.interactor import Builder
from mgit.ui.commands.commands import MgitCommand

def main(repos_config, remotes_config, args=None):
    interactor = Builder().build(
                repos_config   = repos_config,
                remotes_config = remotes_config
                )
    ui = CLI(MgitCommand(interactor))
    out = ui.run(args)
    return out

