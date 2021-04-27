import sys
from contextlib import contextmanager
from io import StringIO
import copy

from mgit.persistence.persistence import Persistence

class File_var:
    def __init__(self):
        self.file = {}

    def set(self, data):
        self.file = copy.copy(data)

    def get(self):
        return copy.copy(self.file)

class MockPersistence(Persistence):
    def __init__(self, persistence, file_var=None):
        self.persistence = persistence
        self.file = file_var or File_var()
        self.file.set(self.persistence)

    def __setitem__(self, key, item):
        self.persistence[key] = item

    def __getitem__(self, item):
        return self.persistence[item]

    def remove(self, key):
        del(self.persistence[key])

    def __contains__(self, key):
        return key in self.persistence

    def read_all(self):
        self.persistence = self.file.get()
        return self.persistence

    def read(self):
        return self.persistence

    def write_all(self):
        self.file.set(self.persistence)

    def set_all(self, data):
        self.persistence = data
        self.write_all()

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

