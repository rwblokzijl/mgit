import sys
from contextlib import contextmanager
from io import StringIO
import copy

import test

from pathlib import Path

from mgit.state.config_state_interactor import ConfigStateInteractor

class File_var:
    def __init__(self):
        self.file = {}

    def set(self, data):
        self.file = copy.copy(data)

    def get(self):
        return copy.copy(self.file)

@contextmanager
def captured_output():
    """
    Usage:
        with captured_output() as (out, err):
            print("hello world")
        # This can go inside or outside the `with` block
        output = out.getvalue().strip()
        self.assertEqual(output, 'hello world!')
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class TestConfigStateInteractor(ConfigStateInteractor):
    def __init__(self):
        super(TestConfigStateInteractor, self).__init__(
                Path(test.__file__).parent / "__files__/test_repos_acceptance.ini",
                Path(test.__file__).parent / "__files__/test_remote_acceptance.ini")

def test_interactors():
    return TestConfigStateInteractor()
