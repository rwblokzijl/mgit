from mgit.util import *
from mgit.repos import RepoTree
from mgit.remotes import Remotes

import os

REMOTE="git.blokzijl.family"
USERNAME="bloodyfool"
REMOTE_PROJECT_DIR="/data/git/projects/"
REMOTE_BASE_URL = USERNAME+"@"+REMOTE+":"+REMOTE_PROJECT_DIR

CONFIG_DIR="~/.config/mgit/"
REMOTES_CONFIG_FILE= os.path.join( CONFIG_DIR, "remotes.ini" )
REPOS_CONFIG_FILE= os.path.join( CONFIG_DIR, "repos.ini" )
SETTINGS_CONFIG_FILE= os.path.join( CONFIG_DIR, "settings.ini" )

def update(all, name, path): #create a new repo
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if all:
            for repo in repos:
                repo.set_id()
        elif name:
            if name in repos:
                repos[name].set_id()
        elif path:
            abspath = os.path.abspath(os.path.expanduser(path))
            repo = repos.get_from_path(abspath)
            if repo:
                repo.set_id()
            else:
                print(f"'{abspath}' is not a managed repo")

def sanity(fix=False): #Checks if all remotes match the configs

    print("Not yet implemented")
    pass

def config(config): #Manages the remotes of one or multiple repos
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes:
        if config == "show":
            repos = RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes)
            print(repos)
        elif config == "remotes": # Perform config sanity check
            print(remotes)
        elif config == "check": # Perform config sanity check
            return not perform_config_check(repos_config=REPOS_CONFIG_FILE, remotes_config=REMOTES_CONFIG_FILE)

def init(path, remote, REMOTE=REMOTE): #create a new repo
    abspath = os.path.abspath(os.path.expanduser(path))
    basename = remote or os.path.basename(abspath)
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

def track(path, name, category): # directory, name
    path = os.path.abspath(os.path.expanduser(path))
    name = name or os.path.basename(path)
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        repos.add(name, path, category or "")

def show(name): # show info on the configured repo
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if name in repos:
            print(repos[name])

def move(recursive, path, verbose, name): # move a repo to another path
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if recursive:
            exclude = get_ignore_paths(SETTINGS_CONFIG_FILE)
            for path in get_local_git_paths(path, exclude):
                move_repo(path, None, repos, verbose=verbose)
        else:
            move_repo(path, name, repos, verbose=True)

def remove(name): # stop tracking a repo
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if name in repos:
            repos.remove(name)
        else:
            log_error(f"'{name}' is not a project")
            return 1

def rename(name, new_name): # rename the repo in the config
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if name in repos:
            repos.rename(name, new_name)
        else:
            log_error(f"'{name}' is not a project")
            return 1

def archive(name): # archive the current repo
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if name in repos:
            repos[name].archive(True)
        else:
            log_error(f"'{name}' is not a project")
            return 1

def unarchive(name): # archive the current repo
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if name in repos:
            repos[name].archive(False)
        else:
            log_error(f"'{name}' is not a project")
            return 1

def install(names): # install projects
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        exit = False
        for name in names:
            if name not in repos:
                log_error(f"'{name}' is not a project")
                exit = True
        if exit:
            return 1

        for name in names:
            print(f"Installing '{name}'")
            repos[name].install()
        return 0

def category_list(): #
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        for category in repos.categories:
            print(category)

def category_show(category): #
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        return repos.print_cat(category)

def category_add(project, category): #
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if project in repos:
            repos[project].add_category(category)

def category_remove(project, category): #
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if project in repos:
            repos[project].remove_category(category)

def remote_list(project, verbose): #
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if project in repos:
            for remote in repos[project].remotes.values():
                if verbose:
                    print(remote)
                else:
                    print(remote["name"])

def remote_add(project, remote, name): #
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        if not project in repos:
            log_error(f"'{project}' is not a project")
            return 1
        if not remote in remotes:
            log_error(f"'{remote}' is not a known remote, choose one of the options options:")
            for remote in remotes:
                print(f' {remote["name"]}')
            print(f"Or add it with: 'mgit remotes add {remote} [url]'")
            return 1

        project = repos[project]
        remote = remotes[remote]
        if name:
            name = name
        else:
            name = project

        print(project.name)
        print(remote["name"])
        print(name)

        log_error("Not yet fully implemented")
        return 1

def remote_remove(): #
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        pass

def remote_origin(): #
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
        pass

def remotes_list(default, verbose): #Manages the remotes of one or multiple repos
    with Remotes(remotes_config=REMOTES_CONFIG_FILE, default=bool(default) or False) as remotes:
        remotes.print(verbose)

def remotes_add(default, name, url): #Manages the remotes of one or multiple repos
    with Remotes(remotes_config=REMOTES_CONFIG_FILE, default=bool(default) or False) as remotes:
        name = name
        if name in remotes:
            print(f"Remote '{name}' already exists, use 'update' instead")
            return 1
        url, path = url.split(":")
        remotes[name] = {
                'name' : name,
                'url' : url,
                'path' : path,
                'type' : None,
                'is_default' : bool(default)
                }

def remotes_remove(remote): #Manages the remotes of one or multiple repos
    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes:
        remotes.remove(remote)

# Repo general, multiple repos multiple remotes

def fetch(): #Fetch from all
    print("Not yet implemented")
    pass

def pull(): #Fetch from all, and merge latest, or raise conflict
    print("Not yet implemented")
    pass

def push(): #Fetch from all, and push latest, or raise conflict (check first for conflicts on all, before pushing any)
    print("Not yet implemented")
    pass

def create(): #Create repos from files
    return 1
    # with Remotes(remotes_config=REMOTES_CONFIG_FILE, default=False) as remotes:
    #     repos, missing = get_repos_from_args(args, repos_config=REPOS_CONFIG_FILE, remotes=remotes)
    #     print("Will clone:", "To:")
    #     for path,remote in missing:
    #         print(remote, "\n  in", path)
    #     if query_yes_no("Do you want to clone all these repos to their specified location?"):
    #         for path,remote in missing:
    #             os.system("git clone " + remote + " " + path)

def dirty(local): #If any dirty
    if local:
        repos = get_all_repos_from_local(local)
    else:
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes:
            repos, _ = RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes).get_repos()

    for repo in repos:
        if repo.is_dirty():
            # print(f"{repo.working_dir} is dirty")
            return 0
    return 1

def status(local, recursive, name, dirty, missing):
    if not local:
        with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
        RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:
            if recursive:
                if name:
                    repos.status(name, category=False, recursive=True, dirty=dirty, missing=missing)
                else:
                    repos.status(".", category=False, recursive=True, dirty=dirty, missing=missing)
            else:
                if name:
                    repos.status(name, category=True, recursive=True, dirty=dirty, missing=missing)
                else:
                    repos.status("~", category=False, recursive=True, dirty=dirty, missing=missing)
                # log_error(f"'{name}' is not a project")
        return 0
    else:
        repos = get_all_repos_from_local(local)

        for repo in repos:
            if repo.is_dirty():
                print("dirty  ", repo.working_dir)
            else:
                if not dirty:
                    print("clean  ", repo.working_dir)

def list_repos(installed, missing, untracked, archived, remotes, path): # List existing repos
    if not (installed or
            missing or
            untracked or
            remotes):
        inc_all = True
    else:
        inc_all = False

    with Remotes(remotes_config=REMOTES_CONFIG_FILE) as remotes, \
    RepoTree(repos_config=REPOS_CONFIG_FILE, remotes=remotes) as repos:

        if remotes is not None:
            # rems = remotes or remotes.default
            for remote in remotes:
                if remote in remotes:
                    print(remote)
            return 0

        if untracked or inc_all:
            exclude = get_ignore_paths(SETTINGS_CONFIG_FILE)
            repo_strings = get_local_git_paths(path, exclude)
            untracked, unarchived_missing, archived_missing, installed = \
                    tag_repo_strings(repo_strings, repos)
        else:
            untracked = []
            unarchived_missing, archived_missing, installed = \
                    tag_repos(repos, root=path)

        if installed or inc_all:
            for repo in installed:
                print("installed  " + repo)

        if missing or inc_all:
            for repo in unarchived_missing:
                print("missing    " + repo)
            if archived or inc_all:
                for repo in archived_missing:
                    print("missing(a) " + repo)

        if untracked or inc_all:
            for repo in untracked:
                print("untracked  " + repo)

def clone(): #Clones the listed repos from one remote to another
    print("Not yet implemented")
    pass

