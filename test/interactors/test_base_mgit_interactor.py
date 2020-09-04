from test.test_interactor import TestInteractor

class TestInteractorGeneral(TestInteractor):

    def test_show(self):
        interactor = self.get_file_test_interactor()
        self.assertIn(
                "ti2316",
                interactor.as_dict()
                )

    def test_show_path(self):
        interactor = self.get_file_test_interactor()
        self.assertEqual(
                "~/.config/dotfiles",
                interactor.as_dict()["dotfiles"]["path"]
                )

