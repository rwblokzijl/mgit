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

def log_error(*args, **kwargs):
    print("ERROR:", *args, file=sys.stderr, **kwargs)

### Util helpers:
def get_repo_id_from_path(path):
    try:
        Repo(path)
    except:
        assert False, "Git repo doesn't exist"
    git_id = "".join([str(x.strip().decode("utf-8")) for x in run_command(f"cd {path} && git rev-list --parents HEAD | tail -1")])
    if ' ' in git_id: #Git repo exists, but has no commits yet
        return None
    return(git_id)

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
    repos = list()
    missing = list()

    for path in paths:
        l_repos, l_missing = get_repo_or_none(path)
        repos += l_repos
        missing += l_missing

    return repos, missing

def get_local_git_paths(path="~"):
    command = "find "+path+" -name '.git' | grep -v /.vim"
    result = run_command(command)
    repos = list()
    for line in result:
        try:
            repos.append(line.strip().decode("utf-8")[:-4])
        except:
            pass
    return repos

def get_all_repos_from_local(path="~"):
    command = "find "+path+" -name '.git' | grep -v /.vim"
    result = run_command(command)
    repos = list()
    for line in result:
        try:
            repos.append(Repo(line.strip().decode("utf-8")+'/..'))
        except:
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

def exists_remote(remote_path, username, remote):
    ans = run_ssh('[ -d "'+remote_path+'" ]', username=username, remote=remote)
    if ans.return_code is 0:
        return True
    else:
        return False

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

### Functions with side effects

### Local edits

def init_local(path, remote_path=None, ):
    abspath = os.path.abspath(path)
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

def run_ssh(*args, username, remote, **kwargs):
    with Connection(remote, user=username) as ssh:
        return ssh.run(*args, warn=True, **kwargs)

def init_remote(project_name, remote, username, remote_project_dir):
    remote_path = os.path.join(remote_project_dir, project_name)
    remote_url = username+"@"+remote+":"+remote_path
    if exists_remote(remote_path, username=username, remote=remote):
        # print("Remote folder already exists, not creating remote repo")
        return remote_url
    print("Creating remote: " + remote_url)
    if not run_ssh('mkdir ' + remote_path, username=username, remote=remote):
        log_error("Couldn't create folder, check permissions")
        raise
    if not run_ssh('git init --bare ' + remote_path, username=username, remote=remote):
        log_error("Created folder but could not init repo, manual action required")
        raise
    return remote_url

### Config stuff

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

