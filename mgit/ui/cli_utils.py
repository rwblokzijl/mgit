import sys
from pathlib import Path

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

def path_relative_to_home(path):
    try:
        return Path("~") / Path(path).absolute().relative_to(Path('~').expanduser())
    except:
        return Path(path).absolute()

