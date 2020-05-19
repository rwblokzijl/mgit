import argparse
import os
import subprocess
import sys

from fabric import Connection
from git import Repo
from git.exc import InvalidGitRepositoryError

def log_error(*args, **kwargs):
    print("ERROR:", *args, file=sys.stderr, **kwargs)

def parse_args():
    parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
    subparsers = parser.add_subparsers(dest="command")

    p1 = subparsers.add_parser("init", help="Create a new local/remote repo pair")
    p1.add_argument("repo", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
    p1.add_argument("remote", help="Name of remote repo", metavar="remote", nargs="?", type=str)

    p2 = subparsers.add_parser("install", help="Install a remote repo")
    p2.add_argument("remote", help="name of remote repo", metavar="remote", type=str)
    p2.add_argument("path", help="Path to install", metavar="DIR", nargs="?", type=str)

    p3 = subparsers.add_parser("list", help="List remote repos")
    p3.add_argument("-l", "--local", help="List from local path instead", metavar="DIR", nargs="?", default=None,
            const="~", type=str)

    # Monitor based commands

    p4 = subparsers.add_parser("status", help="Print the status of listed repos")
    p4.add_argument("repos", help="Path to local repos", metavar="DIR", nargs="*",
                    type=lambda x: valid_dir(parser, x))
    p4.add_argument("-f", dest="files", help="Files specifying repos to monitor", metavar="FILE", nargs="*",
                    type=lambda x: valid_file(parser, x))
    p4.add_argument("-a", "--all", help="Include all locally installed repos", metavar="DIR", nargs="?", default=None,
            const="~", type=str)
    p4.add_argument("-d", help="Include dirty only", action="store_true")

    p5 = subparsers.add_parser("create", help="Create missing repos from files")
    p5.add_argument("-f", dest="files", help="Files specifying repos to monitor", metavar="FILE", nargs="*",
                    type=lambda x: valid_file(parser, x))

    p6 = subparsers.add_parser("dirty", help="Returns true if there is at lease one dirty repo")
    p6.add_argument("repos", help="Path to local repos", metavar="DIR", nargs="*",
                    type=lambda x: valid_dir(parser, x))
    p6.add_argument("-f", dest="files", help="Files specifying repos to monitor", metavar="FILE", nargs="*",
                    type=lambda x: valid_file(parser, x))
    p6.add_argument("-a", "--all", help="Include all locally installed repos", metavar="DIR", nargs="?", default=None,
            const="~", type=str)

    return parser.parse_args()

### TYPES ###
def command(s):
    commands = ["status", "dirty", "install", "list"]
    if s in commands:
        return s
    raise argparse.ArgumentTypeError(s + " not in " + commands)

def valid_file(parser, arg):
    if not os.path.isfile(arg):
        parser.error("No file called %s found!" % arg)
    else:
        return arg

def valid_dir(parser, arg):
    if not os.path.isdir(arg):
        parser.error("No directory called %s found!" % arg)
    else:
        return arg

def valid_path(parser, arg):
    if not os.path.exists(arg):
        parser.error("No file or directory called %s found!" % arg)
    else:
        return arg

### Arg processing
def process_args(args, config_dir):
    if not (
            "repos" in args and args.repos or
            "files" in args and args.files or
            "all"     in args and args.all):
        return process_files(get_config_files(config_dir))

    repos = list()
    missing = list()

    if "repos" in args and args.repos:
        # l_repos, l_missing =
        repos += get_repos_from_string_list(args.repos)
        # missing += l_missing

    if args.files:
        l_repos, l_missing = process_files(args.files)
        repos += l_repos
        missing += l_missing

    if "all" in args and args.all:
        l_repos = get_all_repos_from_local(args.all)
        repos += l_repos

    return repos, missing

def get_config_files(config_dir):
    path = os.path.expanduser(config_dir)
    if os.path.exists(path):
        return [path+f for f in os.listdir(path)]
    else:
        log_error(config_dir, "doesn't exist")
        return []

def get_repos_from_string_list(paths):
    return [x for x in [get_repo_or_string(path) for path in paths] if x]
    repos = list()
    missing = list()

    for path in paths:
        l_repos, l_missing = get_repo_or_string(path)
        repos += l_repos
        missing += l_missing

    return repos, missing

def get_local_git_paths(path="~"):
    command = "find "+path+" -name '.git' | grep -v /.vim | grep -v /.local"
    result = run_command(command)
    repos = list()
    for line in result:
        try:
            repos.append(line.strip().decode("utf-8")[:-4])
        except:
            pass
    return repos

def get_all_repos_from_local(path="~"):
    command = "find "+path+" -name '.git' | grep -v /.vim | grep -v /.local"
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
        # return [Repo(path)], []
        return Repo(path)
    except:
        return None
        # return [], [(path, remote)]

def process_line(line):
    try:
        s = [x for x in line.split(' ') if x]
        path = os.path.expanduser(s[0])
        if path[0] not in ['/', '~']:
            log_error(path + " is not absolute", file=sys.stderr)
            return None
        if len(s) == 2:
            remote = s[1]
        else:
            raise

        if os.path.isdir(path):
            try:
                return Repo(path)
            except:
                if os.listdir(path):
                    log_error("path exists but is not a valid git directory and is not empty")
                    return None
                else:
                    "Path exists but is empty"
                    return path, remote
        else:
            "path doesnt exist"
            return path, remote
    except:
        log_error("Couldn't process line")
        return None

def process_files(files=None):
    processed_lines = list()
    for f in files:
        if not os.path.isfile(f):
            log_error("Not a file:", f)
            exit(1)
        with open(f, 'r') as conf:
            processed_line = [process_line(l.strip()) for l in conf]
            processed_lines += [x for x in processed_line if x ]

    repos   = [x for x in processed_lines if type(x) is not tuple]
    missing = [x for x in processed_lines if type(x) is tuple]

    return repos, missing


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
    ans = run_ssh('[ -d "'+remote_path+'" ]', username, remote)
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
    if exists_remote(remote_path, username, remote):
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

