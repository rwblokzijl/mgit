from mgit.ui.commands.tags._tags import CommandTags
from mgit.ui.base_commands       import SingleRepoCommand

@CommandTags.register
class CommandCategoryRemove(SingleRepoCommand):
    command = "remove"
    help="Remove tags from project"

    config_required = True
    system_required = False

    def build(self, parser):
        parser.add_argument("tags", help="List of tags to remove", default=[], nargs="*", type=str)

    def run(self, repo_state, tags):
        repo_state.tags -= set(tags)
        self.config.set_state(repo_state)
        return repo_state


