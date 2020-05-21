#!/usr/bin/env pipenv-shebang
from util import *

""" On this project:
          !######################!
          !##                  ##!
    The   !## >>    mgit    << ##!   project
          !##                  ##!
          !######################!

    It once stood for manage-git, briefly monitor-git, but now i lean towards multiple-git. It doens't matter tho, all are
    correct.

    The purpose of this script is to manage all the git repositories in my life, in bulk.

    # Features

    - Init repos with a remote (currently remote is hardcoded)

    ## To add:

    - Multiple remote support:
        - mgit shouldn't look at origin, but on specific remotes it manages
        - Directly copying repos elsewhere
            https://stackoverflow.com/questions/7818927/git-push-branch-from-one-remote-to-another
    - Manage configs from mgit directly
        - mgit should be able to add a project to manage with a single command

    # Docs:

    ## Commands:

    ### Repo specific
    init [local] [[remotes]:default in configs]


    ## Configs:

    - will live in .config/mgit
    - or in .mgit files inside an existing git repo

    They specify the repos to manage
"""

REMOTE="git.blokzijl.family"
USERNAME="bloodyfool"
REMOTE_PROJECT_DIR="/data/git/projects/"
# REMOTE_PROJECT_DIR="/home/bloodyfool/testing/"
CONFIG_DIR="~/.config/mgit/"

REMOTES_CONFIG_FILE= os.path.join( CONFIG_DIR, "remotes.ini" )
REPOS_CONFIG_FILE= os.path.join( CONFIG_DIR, "repos.ini" )

REMOTE_BASE_URL = USERNAME+"@"+REMOTE+":"+REMOTE_PROJECT_DIR

args = parse_args()
COMMAND = args.command

# Repo specific, single repo multiple remotes

if COMMAND == "init": #create a new repo
    abspath = os.path.abspath(args.path)
    basename = args.remote or os.path.basename(abspath)
    print("Will create local git repo:", abspath)
    print("With new remote:", REMOTE_BASE_URL+basename)
    if not query_yes_no("Do you want to continue?"):
        print("Doing nothing")
        exit(0)
    remote = init_remote(basename, remote=REMOTE, username=USERNAME, remote_project_dir=REMOTE_PROJECT_DIR)
    init_local(abspath, remote)

elif COMMAND == "install": # directory, name
    basename = args.remote
    abspath = os.path.abspath(args.path or args.remote)
    remotes = get_all_repos_from_remote(remote=REMOTE, username=USERNAME, remote_project_dir=REMOTE_PROJECT_DIR)
    if basename not in remotes:
        log_error(basename, "not in remotes:")
        for repo in remotes:
            print(repo)
        exit (1)
    print("Will create local git repo:", abspath)
    print("With remote:", REMOTE_BASE_URL+basename)
    if not query_yes_no("Do you want to continue?"):
        print("doing nothing")
        exit(0)
    remote = REMOTE_BASE_URL+basename
    init_local(abspath, remote)

elif COMMAND == "fetch": #Fetch from all
    print("Not yet implemented")
    pass

elif COMMAND == "pull": #Fetch from all, and merge latest, or raise conflict
    print("Not yet implemented")
    pass

elif COMMAND == "push": #Fetch from all, and push latest, or raise conflict (check first for conflicts on all, before pushing any)
    print("Not yet implemented")
    pass

# Repo general, multiple repos multiple remotes

elif COMMAND == "create": #Create repos from files
    repos, missing = get_repos_from_args(args, config_dir=CONFIG_DIR)
    print("Will clone:", "To:")
    for path,remote in missing:
        print(remote, "\n  in", path)
    if query_yes_no("Do you want to clone all these repos to their specified location?"):
        for path,remote in missing:
            os.system("git clone " + remote + " " + path)

elif COMMAND == "dirty": #If any dirty
    repos, missing = get_repos_from_args(args, config_dir=CONFIG_DIR)
    for repo in repos:
        if repo.is_dirty():
            exit(0)
    exit(1)

if COMMAND == "status":
    repos, missing = get_repos_from_args(args, config_dir=CONFIG_DIR)
    for repo in repos:
        if repo.is_dirty():
            print("dirty  ", repo.working_dir)
        else:
            if not args.dirty:
                print("clean  ", repo.working_dir)
    if not args.dirty:
        for path,remote in missing:
            print("missing", path)

elif COMMAND == "list": # List existing repos
    if args.local:
        for path, remote in get_all_repos_from_local_and_their_remotes(args.local):
            print(path, remote)
    else:
        print("Remotes:")
        for repo in get_all_repos_from_remote(remote=REMOTE, username=USERNAME, remote_project_dir=REMOTE_PROJECT_DIR):
            print(repo)

elif COMMAND == "sanity": #Checks if all remotes match the configs
    print("Not yet implemented")
    print("Nor is the config structure ready for this")
    pass

elif COMMAND == "clone": #Clones the listed repos from one remote to another
    print("Not yet implemented")
    pass

elif COMMAND == "remotes": #Manages the remotes of one or multiple repos
    print("Not yet implemented")
    print("""
    Should implement:
    - Add
    - List
    """)
    pass
