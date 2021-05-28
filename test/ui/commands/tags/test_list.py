import mgit.ui.commands.tags.list # pylint: disable=W0611 #import important for decorators to run
from test.test_util               import MgitUnitTestBase

class TestCategoryListCommand(MgitUnitTestBase):

    def test_category_list(self):
        self.run_command("tags list")

    def test_category_list_v(self):
        self.run_command("tags list -v")

    def test_category_list_vv(self):
        self.run_command("tags list -vv")

    def test_category_list_vvv(self):
        self.run_command("tags list -vvv")
