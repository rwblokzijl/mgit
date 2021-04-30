from mgit.ui.cli import AbstractLeafCommand
from mgit.ui.commands._mgit import MgitCommand

from mgit.ui.cli_utils import query_yes_no

from pathlib import Path
import json

@MgitCommand.register
class CommandSingleRepoInit(AbstractLeafCommand):
    command = "init"
    help="Create a new local/remote repo pair"

    def remote_repo(self, s):
        if ":" in s:
            return s.split(":", 1)
        else:
            return s, None

    def build(self, parser):
        parser.add_argument("-y", help="Skip asking for confirmation", action='store_true')
        parser.add_argument("-d", "--no-default", help="Do not add any default remotes", action='store_true')
        parser.add_argument("--name", help="Name of the project", type=str)
        parser.add_argument("--path", help="Path to local repo", metavar="DIR", nargs="?", default=".", type=str)
        parser.add_argument("--remotes", help="Name of remote repo", metavar="REMOTE[:REPO]", nargs="+", type=lambda x: self.remote_repo(x))
        parser.add_argument("--origin", help="Name of remote to be default push", metavar="REMOTE", type=lambda x: self.remote_repo(x))

    def run(self, **args):
        raise NotImplementedError("Deleted the interactor becuase it stinks and this code is ugly too")
        """ Prepares the details to init a repo """
        was_abs = Path(args["path"]).is_absolute()
        path = Path(args["path"]).absolute()
        abspath = path
        if args["name"] is None:
            args["name"] = path.name

        if not was_abs:
            args["path"] = str(path).replace(str(Path.home()), "~")

        parent = self.interactor.resolve_best_parent(path)

        if parent:
            args["parent"] = parent.name
            args["path"] = str(path.relative_to(self.interactor.abspath(parent.path)))

        args["remotes"] = dict(args["remotes"] or (
                [] if args["no_default"]
                else [(remote.name, None) for remote in self.interactor.get_default_remotes()]
                ))

        del(args["no_default"])

        if args["origin"]:
            if args["origin"][0] not in args["remotes"]:
                args["remotes"][args["origin"][0]] = args["origin"][1] or args["name"]
            else:
                assert (
                        not args["origin"][1] or
                        args["origin"][1] == args["remotes"][args["origin"][0]]
                        )
            args["origin"] = args["origin"][0]
        else:
            del(args["origin"])

        args["remotes"] = { k:v or args["name"] for k,v in args["remotes"].items() }

        if args.pop('y') or self.interactor.test_mode or query_yes_no("Do you want to init with the following values:" + json.dumps(args, indent = 1)):
            args["abspath"] = str(abspath)
            return self.interactor.repo_init(**args)
        else:
            return "Doing nothing"

