#!/usr/bin/env pipenv-shebang
from util import *
from args import *
from repos import RepoTree
from remotes import Remotes

import os

""" On this project:
    .     !######################!         .
    .     !##                  ##!         .
    The   !## >>    mgit    << ##!   project
    .     !##                  ##!         .
    .     !######################!         .

    It once stood for manage-git, briefly monitor-git, but now i lean towards multiple-git. It doens't matter tho, all are
    correct.

    The purpose of this script is to manage all the git repositories in my life, in bulk.

    ## Configs:

    - live in CONFIG_DIR
    - or in .mgit files inside an existing git repo (or not??)

    They specify the repos to manage

    # Features for later:
    infer repo from current dir

    # Commands so far:

    General:
    |------+--------+----------------------------------------------------------------------------|
    |      | update | update properties about the repos that can be infered                      |
    | TODO | sanity | full sanity check of all repos/remotes/configs                             |
    | TODO | config | commands for handling the configs                                          |
    | TODO |        | where to back them up and keep them consistent across remotes and machines |

    repo config actions:
    |------+-----------+--------+-------------------------+---------------------------------------------------------|
    |      | show      |        | name                    | show a repo by name                                     |
    | TODO | init      |        | path, [[remote name]..] | init a repo local and remote                            |
    |      | add       |        | path, name              | add a repo (init remote?)                               |
    |      | move      |        | path, name              | move a repo to another path                             |
    |      | remove    |        | name                    | stop tracking a repo                                    |
    |      | rename    |        | name, name              | rename the repo in the config                           |
    |      | archive   |        | name                    | add archive flag to                                     |
    |      | unarchive |        | name                    | remove archive flag to                                  |
    | TODO | install   |        | name                    | install a repo from remote by name (add listed remotes) |
    |      | category  |        |                         | category actions                                        |
    |      |           | list   |                         | lists all categories                                    |
    |      |           | show   | category                | show the category and children                          |
    |      |           | add    | repo, category          | add category                                            |
    |      |           | remove | repo, category          | remote category                                         |
    | TODO | remote    |        |                         | Repo remote actions                                     |
    | TODO |           | add    | repo, remote, name      | add a remote to the repo, and vv                        |
    | TODO |           | remove | repo, remote, name      | remove a remote from the repo, and vv                   |
    | TODO |           | origin | repo, remote, name      | set a remote as origin, and vv                          |

    mutli repo actions:
    |------+--------+----------------+----------------------------------------------|
    | TODO | list   |                | list repos, (missing remote)                 |
    |      | dirty  | repos          | is any repo dirty                            |
    | TODO | status | repos          | show status of all repos (clean up ordering) |
    |------+--------+----------------+----------------------------------------------|
    | TODO | fetch  | repos, remotes | mass fetch                                   |
    | TODO | pull   | repos, remotes | mass pull                                    |
    | TODO | push   | repos, remotes | mass push (after shutdown)                   |

    remote actions:
    |------+---------+--------+----------------+--------------------------------------------------------------------------------------------------------------------|
    | TODO | remotes |        |                | manage remotes                                                                                                     |
    |------+---------+--------+----------------+--------------------------------------------------------------------------------------------------------------------|
    |      |         | list   |                | list remotes                                                                                                       |
    |      |         | add    | name, url      | add a remote                                                                                                       |
    |      |         | remove | name           | remove a remote                                                                                                    |
    |------+---------+--------+----------------+--------------------------------------------------------------------------------------------------------------------|
    | TODO |         | init   | name, remote   | init repo in remote                                                                                                |
    | TODO |         | delete | name, remote   | remove repo from remote, maybe not implement for safety!!!                                                         |
    | TODO |         | clone  | repos, remote  | clone to remotes to another https://stackoverflow.com/questions/7818927/git-push-branch-from-one-remote-to-another |
    |------+---------+--------+----------------+--------------------------------------------------------------------------------------------------------------------|
    | TODO |         | show   | name           | show the remote and its repos                                                                                      |
    | TODO |         | check  | repos, remotes | find non up to date repos across all remotes                                                                       |
    | TODO |         | sync   | repos, remotes | fix non up to date repos across all remotes                                                                        |

"""


REMOTE="git.blokzijl.family"
USERNAME="bloodyfool"
REMOTE_PROJECT_DIR="/data/git/projects/"
CONFIG_DIR="~/.config/mgit/"

REMOTES_CONFIG_FILE= os.path.join( CONFIG_DIR, "remotes.ini" )
REPOS_CONFIG_FILE= os.path.join( CONFIG_DIR, "repos.ini" )
SETTINGS_CONFIG_FILE= os.path.join( CONFIG_DIR, "settings.ini" )

REMOTE_BASE_URL = USERNAME+"@"+REMOTE+":"+REMOTE_PROJECT_DIR

args = parse_args()
COMMAND = args.command

# Repo specific, single repo multiple remotes

def main():


    # General Commands:
    if COMMAND == "update": #create a new repo
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.all:
                for repo in repos:
                    repo.set_id()
            elif args.name:
                if args.name in repos:
                    repos[args.name].set_id()
            elif args.path:
                abspath = os.path.abspath(os.path.expanduser(args.path))
                repo = repos.get_from_path(abspath)
                if repo:
                    repo.set_id()
                else:
                    print(f"'{abspath}' is not a managed repo")

    elif COMMAND == "sanity": #Checks if all remotes match the configs
        """
        Should implement sanity checkes for:
            1. remtes

        """


        print("Not yet implemented")
        pass

    elif COMMAND == "config": #Manages the remotes of one or multiple repos
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes:
            if args.config == "show":
                repos = RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes)
                print(repos)
            elif args.config == "remotes": # Perform config sanity check
                print(remotes)
            elif args.config == "check": # Perform config sanity check
                return not perform_config_check(repos_config=REPOS_CONFIG_FILE, remotes_config=REMOTES_CONFIG_FILE)


    # Repo / config management
    elif COMMAND == "init": #create a new repo
        abspath = os.path.abspath(os.path.expanduser(args.path))
        basename = args.remote or os.path.basename(abspath)
        print("will create local git repo:", abspath)
        print("With new remote:", REMOTE_BASE_URL+basename)
        if not query_yes_no("Do you want to continue?"):
            print("Doing nothing")
            return
        try:
            remote = init_remote(basename, remote=REMOTE, username=USERNAME, remote_project_dir=REMOTE_PROJECT_DIR)
            init_local(abspath, remote)
        except:
            return 1
        return 0

    elif COMMAND == "add": # directory, name
        path = os.path.abspath(os.path.expanduser(args.path))
        name = args.name or os.path.basename(path)
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            repos.add(name, path, args.category or "")

    elif COMMAND == "show": # show info on the configured repo
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.name in repos:
                print(repos[args.name])

    elif COMMAND == "move": # move a repo to another path
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.recursive:
                exclude = get_ignore_paths(SETTINGS_CONFIG_FILE)
                for path in get_local_git_paths(args.path, exclude):
                    move_repo(path, None, repos, verbose=args.verbose)
            else:
                move_repo(args.path, args.name, repos, verbose=True)

    elif COMMAND == "remove": # stop tracking a repo
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.name in repos:
                repos.remove(args.name)
            else:
                log_error(f"'{args.name}' is not a project")
                return 1

    elif COMMAND == "rename": # rename the repo in the config
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.name in repos:
                repos.rename(args.name, args.new_name)
            else:
                log_error(f"'{args.name}' is not a project")
                return 1

    elif COMMAND == "archive": # archive the current repo
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.name in repos:
                repos[args.name].archive(True)
            else:
                log_error(f"'{args.name}' is not a project")
                return 1

    elif COMMAND == "unarchive": # archive the current repo
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.name in repos:
                repos[args.name].archive(False)
            else:
                log_error(f"'{args.name}' is not a project")
                return 1

    elif COMMAND == "install": # install projects
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            exit = False
            for name in args.names:
                if name not in repos:
                    log_error(f"'{name}' is not a project")
                    exit = True
            if exit:
                return 1

            for name in args.names:
                print(f"Installing '{name}'")
                repos[name].install()
            return 0

    elif COMMAND == "category": # install projects
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.action == "list":
                for category in repos.categories:
                    print(category)
            elif args.action == "show":
                return repos.print_cat(args.category)
            elif args.action == "add":
                if args.project in repos:
                    repos[args.project].add_category(args.category)
            elif args.action == "remove":
                if args.project in repos:
                    repos[args.project].remove_category(args.category)

    elif COMMAND == "remote": # install projects
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if args.action == "list":
                if args.project in repos:
                    for remote in repos[args.project].remotes.values():
                        if args.verbose:
                            print(remote)
                        else:
                            print(remote["name"])
            elif args.action == "add":
                if not args.project in repos:
                    log_error(f"'{args.project}' is not a project")
                    return 1
                if not args.remote in remotes:
                    log_error(f"'{args.remote}' is not a known remote, choose one of the options options:")
                    for remote in remotes:
                        print(f' {remote["name"]}')
                    print(f"Or add it with: 'mgit remotes add {args.remote} [url]'")
                    return 1

                project = repos[args.project]
                remote = remotes[args.remote]
                if args.name:
                    name = args.name
                else:
                    name = args.project

                print(project.name)
                print(remote["name"])
                print(name)

                log_error("Not yet fully implemented")
                return 1


            elif args.action == "remove":
                pass
            elif args.action == "origin":
                pass

    elif COMMAND == "remotes": #Manages the remotes of one or multiple repos
        if args.action == "list":
            with Remotes(remotes_config=REMOTES_CONFIG_FILE, default=bool(args.default) or False) as remotes:
                remotes.print(args.verbose)

        elif args.action == "add":
            with Remotes(remotes_config=REMOTES_CONFIG_FILE, default=bool(args.default) or False) as remotes:
                name = args.name
                if name in remotes:
                    print(f"Remote '{name}' already exists, use 'update' instead")
                    return 1
                url, path = args.url.split(":")
                remotes[name] = {
                        'name' : name,
                        'url' : url,
                        'path' : path,
                        'type' : None,
                        'is_default' : bool(args.default)
                        }

        elif args.action == "remove":
            with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes:
                remotes.remove(args.remote)

    # Repo general, multiple repos multiple remotes

    elif COMMAND == "fetch": #Fetch from all
        print("Not yet implemented")
        pass

    elif COMMAND == "pull": #Fetch from all, and merge latest, or raise conflict
        print("Not yet implemented")
        pass

    elif COMMAND == "push": #Fetch from all, and push latest, or raise conflict (check first for conflicts on all, before pushing any)
        print("Not yet implemented")
        pass

    elif COMMAND == "create": #Create repos from files
        return 1
        # with Remotes(remotes_config=REMOTES_CONFIG_FILE, default=False) as remotes:
        #     repos, missing = get_repos_from_args(args, repos_config=REPOS_CONFIG_FILE, remotes=remotes)
        #     print("Will clone:", "To:")
        #     for path,remote in missing:
        #         print(remote, "\n  in", path)
        #     if query_yes_no("Do you want to clone all these repos to their specified location?"):
        #         for path,remote in missing:
        #             os.system("git clone " + remote + " " + path)

    elif COMMAND == "dirty": #If any dirty
        if args.local:
            repos = get_all_repos_from_local(args.local)
        else:
            with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes:
                repos, _ = RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes).get_repos()

        for repo in repos:
            if repo.is_dirty():
                # print(f"{repo.working_dir} is dirty")
                return 0
        return 1

    elif COMMAND == "status":
        if not args.local:
            with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
            RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
                if args.recursive:
                    if args.name:
                        repos.status(args.name, category=False, recursive=True, dirty=args.dirty, missing=args.missing)
                    else:
                        repos.status(".", category=False, recursive=True, dirty=args.dirty, missing=args.missing)
                else:
                    if args.name:
                        repos.status(args.name, category=True, recursive=True, dirty=args.dirty, missing=args.missing)
                    else:
                        repos.status("~", category=False, recursive=True, dirty=args.dirty, missing=args.missing)
                    # log_error(f"'{args.name}' is not a project")
            return 0
        else:
            repos = get_all_repos_from_local(args.local)

            for repo in repos:
                if repo.is_dirty():
                    print("dirty  ", repo.working_dir)
                else:
                    if not args.dirty:
                        print("clean  ", repo.working_dir)

    elif COMMAND == "list": # List existing repos
        if not (args.installed or
                args.missing or
                args.untracked or
                args.remotes):
            inc_all = True
        else:
            inc_all = False

        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:

            if args.remotes is not None:
                # rems = args.remotes or remotes.default
                for remote in args.remotes:
                    if remote in remotes:
                        print(remote)
                return 0

            if args.untracked or inc_all:
                exclude = get_ignore_paths(SETTINGS_CONFIG_FILE)
                repo_strings = get_local_git_paths(args.path, exclude)
                untracked, unarchived_missing, archived_missing, installed = \
                        tag_repo_strings(repo_strings, repos)
            else:
                untracked = []
                unarchived_missing, archived_missing, installed = \
                        tag_repos(repos, root=args.path)

            if args.installed or inc_all:
                for repo in installed:
                    print("installed  " + repo)

            if args.missing or inc_all:
                for repo in unarchived_missing:
                    print("missing    " + repo)
                if args.archived or inc_all:
                    for repo in archived_missing:
                        print("missing(a) " + repo)

            if args.untracked or inc_all:
                for repo in untracked:
                    print("untracked  " + repo)

    elif COMMAND == "list_retired": # List existing repos (old)
        if args.local:
            for path, remote in get_all_repos_from_local_and_their_remotes(args.local):
                print(path, remote)
        else:
            print("Remotes:")
            for repo in get_all_repos_from_remote(remote=REMOTE, username=USERNAME, remote_project_dir=REMOTE_PROJECT_DIR):
                print(repo)

    elif COMMAND == "clone": #Clones the listed repos from one remote to another
        print("Not yet implemented")
        pass

if __name__ == '__main__':
    exit(main() or 0)
