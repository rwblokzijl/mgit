import mgit.ui.commands.tags.remove # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestCategoryAdd(MgitUnitTestBase):

    """Test case docstring."""

    def test_add(self):
        self.assertEqual(
                self.config.get_state(name="test_repo_1").tags,
                { 'category2', 'category1' }
                )
        self.run_command("tags remove -n test_repo_1 category2")
        self.assertEqual(
                self.config.get_state(name="test_repo_1").tags,
                { 'category1' }
                )

