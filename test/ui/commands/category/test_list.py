import mgit.ui.commands.category.list # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestCategoryListCommand(MgitUnitTestBase):

    def test_category_list(self):
        self.run_command("category list")

    def test_category_list_v(self):
        self.run_command("category list -v")

    def test_category_list_vv(self):
        self.run_command("category list -vv")

    def test_category_list_vvv(self):
        self.run_command("category list -vvv")
