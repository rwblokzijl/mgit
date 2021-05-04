import mgit.ui.commands.category.add # pylint: disable=W0611 #import important for decorators to run
from test.test_util import MgitUnitTestBase

class TestCategoryAdd(MgitUnitTestBase):

    """Test case docstring."""

    def test_add(self):
        self.assertEqual(
                self.config.get_state(name="test_repo_1").categories,
                { 'category2', 'category1' }
                )
        self.run_command("category add -n test_repo_1 c1 c2")
        # CommandCategoryAdd(
        #         **self.interactors
        #         ).run(  project="test_repo_1",
        #                 categories=["c1", "c2"]
        #                 )
        self.assertEqual(
                self.config.get_state(name="test_repo_1").categories,
                { 'category2', 'category1', "c1", "c2"}
                )

