from mgit.ui.cli import CLI
from mgit.interactor import Builder
from mgit.ui.commands.commands import MgitCommand

repos_config  ="test/__files__/test_repos.ini"
remotes_config="test/__files__/test_remote.ini"

# repos_config  =".config/mgit/repos.ini"
# remotes_config=".config/mgit/remote.ini"

def main(args=None):
    interactor = Builder().build(
                repos_config=repos_config,
                remotes_config=remotes_config
                )
    ui = CLI(interactor, MgitCommand())
    return ui.run(args)

