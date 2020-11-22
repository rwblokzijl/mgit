from mgit.interactors.base_mgit_interactor import BaseMgitInteractor

class CategoryInteractor(BaseMgitInteractor):
    def categories_list(self):
        return list(self.repos.by("categories").keys())

    def categories_show(self, categories):
        ans = dict()
        if not categories:
            categories = self.categories_list()
        for category in categories:
            ans[category] = [r.name for r in self.repos.by("categories").get(category, [])]
        return ans

    def categories_add(self, project, category):
        self.repo_should_exist(project)

        repo_cats = list(self.repos[project].categories)
        repo_cats.append(category)
        repo_cats = list(set(repo_cats))

        with self.repos:
            self.repos.edit(project, categories=repo_cats)

    def categories_remove(self, project, category):
        if project not in self.repos:
            raise self.RepoNotFoundError(f"No tracked project found: '{project}'")
        repo_cats = list(self.repos[project].categories)
        if category not in repo_cats:
            raise self.CategoryNotFoundError(f"'{project}' has no category '{category}")
        repo_cats.remove(category)
        repo_cats = list(set(repo_cats))
        with self.repos:
            self.repos.edit(project, categories=repo_cats)

