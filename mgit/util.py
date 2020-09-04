import argparse
import configparser
import os
import subprocess
import sys
import tabulate

from fabric import Connection
from git import Repo
from git.exc import InvalidGitRepositoryError

# from config import RepoTree # Keep these imports to a minimum

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

def log_error(*args, verbose=True, **kwargs):
    if verbose:
        print("ERROR:", *args, file=sys.stderr, **kwargs)

def log_warning(*args, verbose=True, **kwargs):
    if verbose:
        print("WARNING:", *args, file=sys.stderr, **kwargs)

### Util helpers:

def relpath_list(paths, rel=os.getcwd()):
    return [os.path.relpath(path, rel) for path in paths]

def tag_repos(repos, root="~"):
    unarchived_missing  = list()
    archived_missing    = list()
    installed           = list()

    root = os.path.abspath(os.path.expanduser(root))
    for repo in repos:
        abspath = os.path.abspath(os.path.expanduser(repo.path))
        if root in abspath:
            if repo.missing:
                if repo.archived:
                    archived_missing   += [repo.name]
                else:
                    unarchived_missing += [repo.name]
            else:
                installed += [repo.name]

    # unarchived_missing  = relpath_list(unarchived_missing)
    # archived_missing    = relpath_list(archived_missing)
    # installed           = relpath_list(installed)

    return unarchived_missing, archived_missing, installed

def tag_repo_strings(repo_strings, repos):
    untracked           = [os.path.abspath(os.path.expanduser(rs)) for rs in repo_strings]
    unarchived_missing  = list()
    archived_missing    = list()
    installed           = list()
    for repo in repos:
        abspath = os.path.abspath(os.path.expanduser(repo.path))
        if repo.missing:
            if repo.archived:
                archived_missing   += [abspath]
            else:
                unarchived_missing += [abspath]
        else:
            if abspath in untracked:
                untracked.remove(abspath)
                installed += [abspath]

    untracked           = relpath_list(untracked)
    unarchived_missing  = relpath_list(unarchived_missing)
    archived_missing    = relpath_list(archived_missing)
    installed           = relpath_list(installed)

    return untracked, unarchived_missing, archived_missing, installed

def move_repo(path, name, repos, verbose=False):
    abspath = os.path.abspath(os.path.expanduser(path))
    rid = get_repo_id_from_path(abspath)

    if not get_repo_or_none(abspath):
        log_error(f"'{abspath}' is not a git repo", verbose=verbose)
        return 1

    if name:
        conf_repo = repos[name]
        if not conf_repo:
            log_error(f"Counldn't find a project called '{name}'", verbose=verbose)
            return 1
        rid_repo = repos.get_from_id(rid)
        if rid_repo is not conf_repo:
            log_error(f"Found '{rid_repo.name}' while you specified '{name}'", verbose=verbose)
            return 1
    else:
        conf_repo = repos.get_from_id(rid)
        if not conf_repo:
            log_error("Counldn't infer project, please specify name", verbose=verbose)
            return 1

    path_repo = repos.get_from_path(abspath)
    if path_repo:
        if path_repo is conf_repo:
            print("Filesystem and config are already consistent")
            return 0
        else:
            log_error(f"Repo '{conf_repo.name}' already exists here", verbose=verbose)
            return 1

    conf_repo.set_path(abspath)
    return 0

def collapse_user(path):
    user_prefix = os.path.expanduser("~")
    if path.startswith(user_prefix):
        return path.replace(user_prefix, "~")
    else:
        return path

def get_repo_id_from_path(path):
    try:
        Repo(path)
    except:
        return None
    git_id = "".join([str(x.strip().decode("utf-8")) for x in run_command(f"cd {path} && git rev-list --parents HEAD | tail -1")])
    if ' ' in git_id: #Git repo exists, but has no commits yet
        return None
    return(git_id)

def get_repo_id_from_paths(paths):
    return [get_repo_id_from_path(path) for path in paths]

def get_config_files(config_dir):
    path = os.path.expanduser(config_dir)
    if os.path.exists(path):
        return [path+f for f in os.listdir(path)]
    else:
        log_error(config_dir, "doesn't exist")
        return []

def get_repos_and_missing_from_paths(paths):
    repos = list()
    missing = list()

    for path in paths:
        l_repos, l_missing = get_repo_or_string(path)
        repos += l_repos
        missing += l_missing
    return repos, missing

def get_repos_from_string_list(paths):
    return [x for x in [get_repo_or_none(path) for path in paths] if x]
    # repos = list()
    # missing = list()

    # for path in paths:
    #     l_repos, l_missing = get_repo_or_none(path)
    #     repos += l_repos
    #     missing += l_missing

    # return repos, missing

def exclude(line, excludes):
    for exclude in excludes:
        if line.startswith(exclude):
            return False
    return True

def get_local_git_paths(path="~", ignore_paths=[]):
    excludes = [os.path.abspath(os.path.expanduser(path)) for path in ignore_paths]
    command  = "find "+path+" -xdev -name '.git'"
    result   = [os.path.abspath(os.path.expanduser(line.strip().decode("utf-8"))) for line in run_command(command)]
    result   = [line for line in result if exclude(line, excludes)]
    repos    = list()
    for line in result:
        try:
            repos.append(os.path.realpath(line[:-4]))
        except:
            pass
    return repos

def get_all_repos_from_local(path="~", ignore_paths=[]):
    repos=list()
    for line in get_local_git_paths(path, ignore_paths):
        try:
            repos.append(Repo(line))
        except Exception:
            pass
    return repos

def get_all_repos_from_local_and_their_remotes(path="~"):
    return [
            (repo.working_dir, repo.remotes["origin"].url if "origin" in repo.remotes else "")
            for repo in get_all_repos_from_local(path=path)]

def run_command(command):
    p = subprocess.Popen(command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def get_all_repos_from_remote(remote, username, remote_project_dir):
    command = "ls "+remote_project_dir
    return run_ssh(command, username=username, remote=remote, hide=True).stdout.strip().splitlines()

def get_repo_or_string(path, remote=None):
    try:
        return [Repo(path)], []
    except:
        return [], [(path, remote)]

def get_repo_or_none(path, remote=None):
    try:
        # return [Repo(path)], []
        return Repo(path)
    except:
        return None
        # return [], [(path, remote)]

### General helpers
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

### Function without side effects

def exists_local(path):
    return os.path.isdir(path)

def is_local_git(path):
    if not exists_local:
        return False
    try:
        _ = Repo(path).git_dir
        return True
    except InvalidGitRepositoryError:
        return False

def get_type_from_url(url):
    if "github" in url:
        return "github"
    elif "gitlab" in url:
        return "gitlab"
    elif "bitbucket" in url:
        return "bitbucket"
    else:
        return None

def section_get(section, field, default=None):
    if field in section:
        return section[field]
    else:
        return default


### Functions with side effects

### Local edits

def init_local(path, remote_path=None, ):
    abspath = os.path.abspath(os.path.expanduser(path))
    if not exists_local(path):
        print("Creating new local directory:", abspath)
        os.mkdir(path)
    # if is_local_git(path):
    #     print("Local repo exists:", abspath)
    #     return
    repo = Repo.init(path)
    if remote_path:
        if "origin" not in repo.remotes:
            print("Adding remote:", remote_path)
            origin = repo.create_remote("origin", remote_path)
            origin.fetch()
        else:
            log_error("Remote origin exists for", abspath)

### REMOTE edits

def run_ssh(*args, username, remote, port=22, **kwargs):
    with Connection(remote, user=username, port=port) as ssh:
        return ssh.run(*args, warn=True, **kwargs)

### Config stuff

def get_ignore_paths(settings_config):
    configPath = os.path.abspath(os.path.expanduser(settings_config))
    config = configparser.ConfigParser()
    config.read(configPath)
    if "settings" in config and "local-ignore" in config["settings"]:
        return config["settings"]["local-ignore"].split()

def pprint(data, header=None):
    if not header:
        header = data[0].keys()
    rows   = [x.values() for x in data]
    print(tabulate.tabulate(rows, header))

def perform_config_check(repos_config, remotes_config):
    print("""
    Not implemented, this should perform a number of sanity checks on the config:
    1. Does everything have a parent
    2. Does everything have an origin
    3. ...
    """)
    return True

