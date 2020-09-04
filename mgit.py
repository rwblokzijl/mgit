#!/usr/bin/env pipenv-shebang

from main import main_cli, main

if __name__ == '__main__':
    repos_config  ="~/.config/mgit/repos.ini"
    remotes_config="~/.config/mgit/remotes.ini"
    exit(
        bool(
            # main(
            main_cli(
                repos_config   = repos_config,
                remotes_config = remotes_config )
            )
        )
