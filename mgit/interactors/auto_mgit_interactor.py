from mgit.interactors.base_mgit_interactor import BaseMgitInteractor

class AutoRepoInteractor(BaseMgitInteractor):
    # def categories_list(self):
    #     return list(self.repos.by("categories").keys())

    "Helpers that interact"
    def add_to_key(self, name, key, remotes):
        self.repo_should_exist(name)

        value = list(self.repos[name].get_auto_key(key)) or []
        value.extend(remotes)
        value = " ".join(list(set(value)))

        with self.repos:
            self.repos.edit(name, **{key:value})

        return f"{name} {key} {value}"

    def remove_from_key(self, name, key, remotes):
        self.repo_should_exist(name)

        current_remotes = list(self.repos[name].get_auto_key(key)) or []
        value = [remote for remote in current_remotes if remotes not in remotes]
        value = " ".join(list(set(value)))
        with self.repos:
            self.repos.edit(name, **{key:value})

        return f"{name} {key}: {value}"

    def set_key(self, name, key, value):
        value = " ".join(list(set(value)))
        self.repo_should_exist(name)
        with self.repos:
            self.repos.edit(name, **{key:value})

        return f"{name} {key}: {value}"

    def remove_key(self, name, key, value):
        self.repo_should_exist(name)
        with self.repos:
            self.repos.edit(name, **{key:""})

        return f"{name} {key} removed"

    "Show"
    def auto_show(self, name, branch, functions=[]):
        self.repo_should_exist(name)
        keys = [ f"auto-{function}-{branch}" for function in functions ] or[ f"auto-commit-{branch}",
                f"auto-push-{branch}",
                f"auto-fetch-{branch}",
                f"auto-pull-{branch}" ]
        for key in keys:
            value = self.repos[name].get_auto_key(key) or ""
            yield f"{name} {key}: {value}"

    "Ui that calls helpers"
    def auto_add_push(self, name, branch, remotes):
        self.remotes_should_exist(remotes)
        key = f"auto-push-{branch}"
        return self.add_to_key(name, key, remotes)

    def auto_add_fetch(self, name, branch, remotes):
        self.remotes_should_exist(remotes)
        key = f"auto-fetch-{branch}"
        return self.add_to_key(name, key, remotes)

    def auto_set_commit(self, name, branch):
        key = f"auto-commit-{branch}"
        return self.set_key(name, key, 1)

    def auto_set_push(self, name, branch, remotes):
        self.remotes_should_exist(remotes)
        key = f"auto-push-{branch}"
        return self.set_key(name, key, remotes)

    def auto_set_fetch(self, name, branch, remotes):
        self.remotes_should_exist(remotes)
        key = f"auto-fetch-{branch}"
        return self.set_key(name, key, remotes)

    def auto_set_pull(self, name, branch, remote):
        self.remotes_should_exist([remote])
        key = f"auto-pull-{branch}"
        return self.set_key(name, key, remote)

    def auto_remove_commit(self, name, branch):
        key = f"auto-commit-{branch}"
        return self.remove_key(name, key)

    def auto_remove_push(self, name, branch, remotes):
        self.remotes_should_exist(remotes)
        key = f"auto-push-{branch}"
        return self.remove_from_key(name, key, remotes)

    def auto_remove_fetch(self, name, branch, remotes):
        self.remotes_should_exist(remotes)
        key = f"auto-fetch-{branch}"
        return self.remove_from_key(name, key, remotes)

    def auto_remove_pull(self, name, branch):
        key = f"auto-pull-{branch}"
        return self.remove_key(name, key)
