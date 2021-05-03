from test.test_util import MgitUnitTestBase
from mgit.ui.commands.category.add import CommandCategoryAdd
import unittest

class TestCategoryAdd(MgitUnitTestBase):

    """Test case docstring."""

    def test_add(self):
        self.assertEqual(
                self.config.get_state(name="test_repo_1").categories,
                { 'category2', 'category1' }
                )
        CommandCategoryAdd(
                **self.interactors
                ).run(  project="test_repo_1",
                        categories=["c1", "c2"]
                        )
        self.assertEqual(
                self.config.get_state(name="test_repo_1").categories,
                { 'category2', 'category1', "c1", "c2"}
                )

