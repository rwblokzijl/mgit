from mgit.ui.commands.tags._tags import CommandTags
from mgit.ui.base_commands       import SingleRepoCommand

@CommandTags.register
class CommandCategoryAdd(SingleRepoCommand):
    command = "add"
    help="Add tags to project"

    config_required = True
    system_required = False

    def build(self, parser):
        parser.add_argument("tags", help="List of tags to show", default=[], nargs="*", type=str)

    def run(self, repo_state, tags):
        repo_state.tags.update(tags)
        self.config.set_state(repo_state)
        return repo_state

