#!/usr/bin/env pipenv-shebang
from util import *

REMOTE="git.blokzijl.family"
USERNAME="bloodyfool"
REMOTE_PROJECT_DIR="/data/git/projects/"
# REMOTE_PROJECT_DIR="/home/bloodyfool/testing/"
CONFIG_DIR="~/.config/git_manager/"

REMOTE_BASE_URL = USERNAME+"@"+REMOTE+":"+REMOTE_PROJECT_DIR

args = parse_args()
COMMAND = args.command

# Info Commands
if COMMAND == "list":
    if args.local:
        for path, remote in get_all_repos_from_local_and_remotes(args.local):
            print(path, remote)
    else:
        print("Remotes:")
        for repo in get_all_repos_from_remote(remote=REMOTE, username=USERNAME, remote_project_dir=REMOTE_PROJECT_DIR):
            print(repo)

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

elif COMMAND == "init": #create a new repo
    abspath = os.path.abspath(args.repo)
    basename = args.remote or os.path.basename(abspath)
    print("Will create local git repo:", abspath)
    print("With new remote:", REMOTE_BASE_URL+basename)
    if not query_yes_no("Do you want to continue?"):
        print("doing nothing")
        exit(0)
    remote = init_remote(basename, remote=REMOTE, username=USERNAME, remote_project_dir=REMOTE_PROJECT_DIR)
    init_local(abspath, remote)

# Monitor Commands

if COMMAND == "status":
    repos, missing = process_args(args, config_dir=CONFIG_DIR)
    for repo in repos:
        if repo.is_dirty():
            print("dirty  ", repo.working_dir)
        else:
            if not args.d:
                print("clean  ", repo.working_dir)
    if not args.d:
        for path,remote in missing:
            print("missing", path)

elif COMMAND == "dirty": #If any dirty
    repos, missing = process_args(args, config_dir=CONFIG_DIR)
    for repo in repos:
        if repo.is_dirty():
            exit(0)
    exit(1)

elif COMMAND == "create": #If any dirty
    repos, missing = process_args(args, config_dir=CONFIG_DIR)
    print("Will clone:", "To:")
    for path,remote in missing:
        print(remote, "\n  in", path)
    if query_yes_no("Do you want to clone all these repos to their specified location?"):
        for path,remote in missing:
            os.system("git clone " + remote + " " + path)

