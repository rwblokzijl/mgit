#!/usr/bin/env pipenv-shebang

from mgit.main import main_cli

if __name__ == '__main__':
    repos_config  ="~/.config/mgit/repos.ini"
    remotes_config="~/.config/mgit/remotes.ini"
    settings_config="~/.config/mgit/settings.ini"
    exit(
        bool(
            # main(
            main_cli(
                repos_config   = repos_config,
                remotes_config = remotes_config,
                settings_config = settings_config
                )
            )
        )
