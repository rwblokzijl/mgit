#!/usr/bin/env pipenv-shebang

from util import *

args = parse_args()

COMMAND = args.command

# Info Commands
if COMMAND == "list":
    print("Remotes:")
    for repo in get_all_repos_from_remote():
        print(repo)

elif COMMAND == "install": # directory, name
    basename = args.remote
    abspath = os.path.abspath(args.path or args.remote)
    remotes = get_all_repos_from_remote()
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
    remote = init_remote(basename)
    init_local(abspath, remote)

# Monitor Commands

if COMMAND == "status":
    repos, missing = process_args(args)
    for repo in repos:
        if repo.is_dirty():
            print("dirty  ", repo.working_dir)
        else:
            print("clean  ", repo.working_dir)
    for path in missing:
        print("missing", path)

elif COMMAND == "dirty": #If any dirty
    repos, missing = process_args(args)
    for repo in repos:
        if repo.is_dirty():
            exit(0)
    exit(1)
