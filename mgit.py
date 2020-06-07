#!/usr/bin/env pipenv-shebang

from abc import ABC

from mgit import commands
from mgit.args import parse_args

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
    generally infer repo from current dir

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

# Repo specific, single repo multiple remotes

def main(args):
    kwargs = vars(args)
    COMMAND = kwargs.pop("command")

    # General Commands:
    if COMMAND == "update": #create a new repo
        commands.update(**kwargs)
    elif COMMAND == "sanity": #Checks if all remotes match the configs
        if args.action == "check":
            commands.sanity(fix=False, **kwargs)
        elif args.action == "fix":
            commands.sanity(**kwargs)
    elif COMMAND == "config": #Manages the remotes of one or multiple repos
        commands.config(**kwargs)
    elif COMMAND == "init": #create a new repo
        commands.init(args.path, args.remote)
    elif COMMAND == "track": # directory, name
        commands.track(args.path, args.name, args.category)
    elif COMMAND == "show": # show info on the configured repo
        commands.show(args.name)
    elif COMMAND == "move": # move a repo to another path
        commands.move(args.recursive, args.path, args.verbose, args.name)
    elif COMMAND == "remove": # stop tracking a repo
        commands.remove(args.name)
    elif COMMAND == "rename": # rename the repo in the config
        commands.rename(args.name, args.new_name)
    elif COMMAND == "archive": # archive the current repo
        commands.archive(args.name)
    elif COMMAND == "unarchive": # archive the current repo
        commands.unarchive(args.name)
    elif COMMAND == "install": # install projects
        commands.install(args.names)
    elif COMMAND == "category": # install projects
        if args.action == "list":
            commands.category_list()
        elif args.action == "show":
            commands.category_show(args.category)
        elif args.action == "add":
            commands.category_add(args.project, args.category)
        elif args.action == "remove":
            commands.category_remove(args.project, args.category)
    elif COMMAND == "remote": # install projects
        if args.action == "list":
            commands.remote_list(args.project, args.verbose)
        elif args.action == "add":
            commands.remote_add(args.project, args.remote, args.name)
        elif args.action == "remove":
            commands.remote_remove()
        elif args.action == "origin":
            commands.remote_origin()
    elif COMMAND == "remotes": #Manages the remotes of one or multiple repos
        if args.action == "list":
            commands.remotes_list(args.default, args.verbose)
        elif args.action == "add":
            commands.remotes_add(args.default, args.name, args.url)
        elif args.action == "remove":
            commands.remotes_remove(args.remote)
    elif COMMAND == "fetch": #Fetch from all
        commands.fetch()
    elif COMMAND == "pull": #Fetch from all, and merge latest, or raise conflict
        commands.pull()
    elif COMMAND == "push": #Fetch from all, and push latest, or raise conflict (check first for conflicts on all, before pushing any)
        commands.push()
    elif COMMAND == "create": #Create repos from files
        commands.create()
    elif COMMAND == "dirty": #If any dirty
        commands.dirty(args.local)
    elif COMMAND == "status":
        commands.status(args.local, args.recursive, args.name, args.dirty, args.missing)
    elif COMMAND == "list": # List existing repos
        commands.list_repos(args.installed, args.missing, args.untracked, args.archived, args.remotes, args.path)
    elif COMMAND == "clone": #Clones the listed repos from one remote to another
        commands.clone()

if __name__ == '__main__':
    args = parse_args()
    exit(main(args) or 0)
