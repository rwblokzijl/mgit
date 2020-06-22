#!/usr/bin/env pipenv-shebang

from main import main

if __name__ == '__main__':
    repos_config  ="~/.config/mgit/repos.ini"
    remotes_config="~/.config/mgit/remotes.ini"
    print(main( repos_config=repos_config, remotes_config=remotes_config ))
    exit()
