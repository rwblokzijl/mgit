from mgit.ui.cli            import AbstractLeafCommand
import sys
from abc import ABC, abstractmethod

from mgit.state import RepoState

class ParseGroup(ABC):
    def __init__(self, parser):
        self._parser = parser
        self.args = []
        self.build()

    def add_argument(self, *args, add_to=None, **kwargs):
        if add_to is None:
            self._parser.add_argument(*args, **kwargs)
        else:
            add_to.add_argument(*args, **kwargs)
        self.args.append(kwargs['dest']) #dest must be specified

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def parse(self, *args, **kwargs):
        pass

class ArgRepoState(ParseGroup):
    def __init__(self, *args, general_state_interactor, **kwargs):
        self.general_state_interactor = general_state_interactor
        super(ArgRepoState, self).__init__(*args, **kwargs)

    def build(self):
        me_group = self._parser.add_mutually_exclusive_group()
        self.add_argument("-n", "--name", add_to=me_group, dest="MGIT_NAME",help="Name of the repo", type=str) # if set: definitely name
        self.add_argument("-p", "--path", add_to=me_group, dest="MGIT_PATH", help="Path of the repo", type=str) # if set: definitely path
        self.add_argument(dest="repo",    add_to=me_group, help="Name or path of the repo", nargs="?", type=str) # else: try to infer
        return me_group

    def parse(self, MGIT_NAME, MGIT_PATH, repo): #type: ignore # idfk how to solve the error
        if MGIT_NAME:
            config_state, system_state = self.general_state_interactor.get_both_from_name(MGIT_NAME)
        elif MGIT_PATH:
            config_state, system_state = self.general_state_interactor.get_both_from_path(MGIT_PATH)
        else: #infer
            config_state, system_state = self.general_state_interactor.get_both_from_name_or_path(repo)
        combined = config_state + system_state
        return {'repo_state': combined}

class ArgRepoStateOrAll(ArgRepoState):
    def build(self):
        me_group = super(ArgRepoStateOrAll, self).build()
        self.add_argument("-a", "--all", add_to=me_group, dest="MGIT_ALL", help="All repos in config", action="store_true") # all repos in config

    def parse(self, MGIT_NAME, MGIT_PATH, repo, MGIT_ALL): #type: ignore # idfk how to solve the error
        if MGIT_ALL:
            return {'all': True, 'repo_state': None}
        else:
            ans = {'all': False}
            ans.update(super(ArgRepoStateOrAll, self).parse(MGIT_NAME, MGIT_PATH, repo))
            return ans

class MgitLeafCommand(AbstractLeafCommand):
    def __init__(self, *args, **kwargs):
        super(MgitLeafCommand, self).__init__(*args, **kwargs)
        self.parse_args_map = []

    def add_parse_group(self, group):
        self.parse_args_map.append(group)

    def run_command(self, args):
        for parse_group in self.parse_args_map:
            args_to_pass = {k:v for k, v in args.items() if k in parse_group.args}
            args = {k:v for k, v in args.items() if k not in parse_group.args}
            new_args = parse_group.parse(**args_to_pass)
            for arg, val in new_args.items():
                assert arg not in args, f"'{arg}' already in args"
                args[arg] = val
        return self.run(**args)

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
        prompt = "[y/n] "
    elif default == "yes":
        prompt = "[Y/n] "
    elif default == "no":
        prompt = "[y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    if '\n' in question:
        prompt = '\n' + prompt
    else:
        prompt = ' ' + prompt

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

