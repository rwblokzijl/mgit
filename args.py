import argparse
from config import RepoTree
from util import *

def parse_args():
    parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # Management

    # ---- Config

    cmd_config            = subparsers.add_parser("config", help="Commands relating to the config")
    cmd_config_subparsers = cmd_config.add_subparsers(dest="config")
    cmd_config_list       = cmd_config_subparsers.add_parser("show", help="List all repos and their remotes")
    cmd_config_check      = cmd_config_subparsers.add_parser("check", help="List remotes")

    cmd_config_subparsers.required = True

    cmd_config_list.add_argument("-v", "--verbose", help="Show details", action="store_true")

    # Repo specific, single repo multiple remotes

    # ---- Init

    cmd_init = subparsers.add_parser("init", help="Create a new local/remote repo pair")
    cmd_init.add_argument("path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
    cmd_init.add_argument("remote", help="Name of remote repo", metavar="remote", nargs="?", type=str)

    # ---- Install

    cmd_install = subparsers.add_parser("install", help="Install a remote repo")
    cmd_install.add_argument("remote", help="name of remote repo", metavar="remote", type=str)
    cmd_install.add_argument("path", help="Path to install", metavar="DIR", nargs="?", type=str)


    # Repo general, multiple repos multiple remotes

    # ---- Remotes

    cmd_remotes            = subparsers.add_parser("remotes", help="Manage remotes")
    cmd_remotes_subparsers = cmd_remotes.add_subparsers(dest="remotes")
    cmd_remotes_list       = cmd_remotes_subparsers.add_parser("list", help="List remotes")
    cmd_remotes_add        = cmd_remotes_subparsers.add_parser("add", help="Add a remote")
    cmd_remotes_remove     = cmd_remotes_subparsers.add_parser("remove", help="Remove remotes")

    cmd_remotes_subparsers.required = True

    cmd_remotes_list.add_argument("-d", "--default", help="List default remotes only", action="store_true")
    cmd_remotes_list.add_argument("-v", "--verbose", help="Show details", action="store_true")

    cmd_remotes_add.add_argument("name", help="Name of remote", type=str)
    cmd_remotes_add.add_argument("url", help="Remote url", type=str)
    cmd_remotes_add.add_argument("-d", "--default", help="Add as/Make default", action="store_true")

    cmd_remotes_remove.add_argument("remote", help="Remotes to remove", metavar="REMOTE", nargs="+", type=str)

    # ---- Create


    cmd_create = subparsers.add_parser("create", help="Create missing repos from files")
    cmd_create.add_argument("-f", dest="files", help="Files specifying repos to monitor", metavar="FILE", nargs="*",
                    type=lambda x: valid_file(parser, x))

    # ---- List

    cmd_list = subparsers.add_parser("list", help="List remote repos")
    cmd_list.add_argument("-l", "--local", help="List from local path instead", metavar="DIR", nargs="?", default=None,
            const=".", type=str)

    # ---- Status

    cmd_status = subparsers.add_parser("status", help="Print the status of listed repos")
    cmd_status.add_argument("repos", help="Path to local repos", metavar="DIR", nargs="*",
                    type=lambda x: valid_dir(parser, x))
    cmd_status.add_argument("-f", dest="files", help="Files specifying repos to monitor", metavar="FILE", nargs="*",
                    type=lambda x: valid_file(parser, x))
    cmd_status.add_argument("-a", "--all", help="Include all locally installed repos", metavar="DIR", nargs="?", default=None,
            const="~", type=str)
    cmd_status.add_argument("--dirty", "-d", help="Include dirty only", action="store_true")

    # ---- Dirty

    cmd_dirty = subparsers.add_parser("dirty", help="Returns true if there is at lease one dirty repo")
    cmd_dirty.add_argument("repos", help="Path to local repos", metavar="DIR", nargs="*",
                    type=lambda x: valid_dir(parser, x))
    cmd_dirty.add_argument("-f", dest="files", help="Files specifying repos to monitor", metavar="FILE", nargs="*",
                    type=lambda x: valid_file(parser, x))
    cmd_dirty.add_argument("-a", "--all", help="Include all locally installed repos", metavar="DIR", nargs="?", default=None,
            const="~", type=str)

    # ----

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
def get_repos_from_args(args, repos_config, remotes):
    if not (
            "repos" in args and args.repos or
            "files" in args and args.files or
            "all"     in args and args.all):
        return RepoTree(repos_config, remotes).get_repos()

    repos = list()
    missing = list()

    if "repos" in args and args.repos:
        # l_repos, l_missing =
        repos += get_repos_from_string_list(args.repos)
        # missing += l_missing

    # if args.files:
    #     l_repos, l_missing = process_files(args.files)
    #     repos += l_repos
    #     missing += l_missing

    if "all" in args and args.all:
        l_repos = get_all_repos_from_local(args.all)
        repos += l_repos

    return repos, missing
