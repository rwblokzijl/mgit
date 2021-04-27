from mgit.ui.cli               import CLI
from mgit.ui.commands.commands import MgitCommand

import unittest
from unittest.mock import Mock

class TestSingleRepoCommands(unittest.TestCase):

    def setUp(self):
        self.interactor=Mock()
        self.interactor.test_mode = True
        self.ui = CLI(command=MgitCommand(interactor=self.interactor))

    def tearDown(self):
        pass

    def test_init(self):
        args = "init --path /tmp/test_dir --remotes a:b c --origin a".split()
        self.interactor.resolve_best_parent.return_value = None
        self.ui.run(args)
        self.interactor.repo_init.assert_called_with(
                name="test_dir",
                path="/tmp/test_dir",
                remotes={"a":"b", "c":"test_dir"},
                origin="a",
                abspath='/tmp/test_dir'
                )

