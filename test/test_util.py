import sys
from contextlib import contextmanager
from io import StringIO
import copy

class TestPersistence:
    def __init__(self, persistence):
        self.persistence = persistence
        self.file = copy.copy(self.persistence)

    def set(self, key, item):
        self.persistence[key] = item

    def remove(self, key):
        del(self.persistence[key])

    def __contains__(self, key):
        return key in self.persistence

    def read_all(self):
        self.persistence = copy.copy(self.file)
        return self.persistence

    def read(self):
        return self.persistence

    def write_all(self):
        self.file = copy.copy(self.persistence)

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

