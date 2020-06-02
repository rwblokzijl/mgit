import argparse
from util import *

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    add_general_commands(     subparsers)
    add_single_repo_commands( subparsers)
    add_multi_repo_commands(  subparsers)
    add_remotes_commands(     subparsers)
    add_category_commands(    subparsers)

    add_deprecated_commands(  subparsers)

    return parser.parse_args()

# Parsers, categorised:
def add_general_commands(subparsers):
    "General commands"

    # ---- Update
    cmd_update = subparsers.add_parser("update", help="Update repos based on some info")
    cmd_update.add_argument("path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
    cmd_update.add_argument("-a", "--all", help="Include all locally installed repos", action="store_true")
    cmd_update.add_argument("-n", "--name", help="Name of repo to update", type=str)

    # ---- Config
    cmd_config            = subparsers.add_parser("config", help="Commands relating to the config")
    cmd_config_subparsers = cmd_config.add_subparsers(dest="config")
    cmd_config_list       = cmd_config_subparsers.add_parser("show", help="List all repos and their remotes")
    cmd_config_list       = cmd_config_subparsers.add_parser("remotes", help="List all remotes")
    cmd_config_check      = cmd_config_subparsers.add_parser("check", help="List remotes")
    cmd_config_subparsers.required = True
    cmd_config_list.add_argument("-v", "--verbose", help="Show details", action="store_true")

def add_single_repo_commands(subparsers):
    "All Single repo commands"

    # ---- Show
    cmd_show = subparsers.add_parser("show", help="Show details on the current repo")
    cmd_show.add_argument("name", help="Name of the project", type=str)

    # ---- Init
    cmd_init = subparsers.add_parser("init", help="Create a new local/remote repo pair")
    cmd_init.add_argument("path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
    cmd_init.add_argument("remote", help="Name of remote repo", metavar="remote", nargs="?", type=str)

    # ---- Add
    cmd_add = subparsers.add_parser("add", help="Start managing the current repo")
    cmd_add.add_argument("category", help="management category", nargs="?", type=str)
    cmd_add.add_argument("path", help="Path to the repo", metavar="DIR", nargs="?", default=".", type=str)
    cmd_add.add_argument("name", help="Name of the project", nargs="?", default=False, type=str)

    # ---- Move
    cmd_move = subparsers.add_parser("move", help="Move the repo in the config")
    cmd_move.add_argument("path", help="New path", metavar="DIR", nargs="?", default=".", type=str)
    cmd_move.add_argument("name", help="Name of the project", nargs="?", default=False, type=str)
    cmd_move.add_argument("-r", "--recursive", help="All repos below the path", action="store_true")
    cmd_move.add_argument("-v", "--verbose", help="Show details", action="store_true")

    # ---- Remove
    cmd_remove = subparsers.add_parser("remove", help="Stop managing the current repo")
    cmd_remove.add_argument("name", help="Name of the project", nargs="?", default=False, type=str)

    # ---- Rename
    cmd_rename = subparsers.add_parser("rename", help="Move the repo in the config")
    cmd_rename.add_argument("name", help="Name of the project", nargs="?", default=False, type=str)
    cmd_rename.add_argument("new_name", help="New name of the project", nargs="?", default=False, type=str)

    # ---- Archive
    cmd_archive = subparsers.add_parser("archive", help="Archive the current project")
    cmd_archive.add_argument("name", help="Name of the project", nargs="?", default=False, type=str)

    # ---- Un-archive
    cmd_unarchive = subparsers.add_parser("unarchive", help="Un-archive the current project")
    cmd_unarchive.add_argument("name", help="Name of the project", nargs="?", default=False, type=str)

    # ---- Install
    cmd_install = subparsers.add_parser("install", help="Install a remote repo")
    # cmd_install.add_argument("remote", help="name of remote repo", nargs="?", type=str)
    cmd_install.add_argument("names", help="Name of remote repo", metavar="name", nargs="+", type=str)

def add_multi_repo_commands(subparsers):
    "All muli repo commands"

    # cmd_list_remote     = cmd_list_subparsers.add_parser("remote", help="List for remotes")
    # cmd_list_remote.add_argument("remotes", help="Name of remote to list", metavar="DIR", nargs="?", type=str)
    # # cmd_list_remote.add_argument("-a", "--archived",  help="Include archived", action="store_true")

    # ---- List
    cmd_list = subparsers.add_parser("list",   help="List remote repos")
    cmd_list.add_argument("path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
    cmd_list.add_argument("-i", "--installed", help="List installed", action="store_true")
    cmd_list.add_argument("-u", "--untracked", help="List local untracked", action="store_true")
    cmd_list.add_argument("-m", "--missing",   help="List missing", action="store_true")
    cmd_list.add_argument("-a", "--archived",  help="Include archived", action="store_true")
    cmd_list.add_argument("-r", "--remotes",   help="Remotes to list from", nargs="*", type=str)

    # ---- Status
    cmd_status = subparsers.add_parser("status", help="Print the status of listed repos")
    cmd_status.add_argument("name", help="Name of repo", metavar="DIR", nargs="?", type=str)
    cmd_status.add_argument("-l", "--local", help="Include all locally installed repos", metavar="DIR", nargs="?", default=None,
            const="~", type=str)
    cmd_status.add_argument("-d", "--dirty",   help="Include dirty only",   default=False,  action="store_true")
    cmd_status.add_argument("-m", "--missing", help="Include missing repos", default=False, action="store_true")
    cmd_status.add_argument("-r", "--recursive", help="Include subrepos", default=False, action="store_true")

    # ---- Dirty
    cmd_dirty = subparsers.add_parser("dirty", help="Returns true if there is at lease one dirty repo")
    cmd_dirty.add_argument("repos", help="Path to local repos", metavar="DIR", nargs="*",
                    type=lambda x: valid_dir(parser, x))
    cmd_dirty.add_argument("-l", "--local", help="Include all locally installed repos", metavar="DIR", nargs="?", default=None,
            const="~", type=str)

def add_remotes_commands(subparsers):
    "All remotes commands"

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

def add_category_commands(subparsers):
    cmd_category                     = subparsers.add_parser("category", help="Manage categories")
    cmd_category_subparsers          = cmd_category.add_subparsers(dest="action")
    cmd_category_subparsers.required = True

    cmd_category_list                = cmd_category_subparsers.add_parser("list", help="List known categories")

    cmd_category_show                = cmd_category_subparsers.add_parser("show", help="Show category and children")
    cmd_category_show.add_argument("category", help="Name of the category", type=str)

    cmd_category_add                 = cmd_category_subparsers.add_parser("add", help="Add a category to a repo")
    cmd_category_add.add_argument("project", help="Name of the project", type=str)
    cmd_category_add.add_argument("category", help="Name of the category", type=str)

    cmd_category_remove              = cmd_category_subparsers.add_parser("remove", help="Remove a category from a repo")
    cmd_category_remove.add_argument("project", help="Name of the project", type=str)
    cmd_category_remove.add_argument("category", help="Name of the category", type=str)

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
