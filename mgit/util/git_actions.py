from pygit2 import Repository
import pygit2

from functools import reduce

def fetch(repo: Repository):
    for remote in repo.remotes:
        username = remote.url.split('@')[0]
        remote.fetch(callbacks=pygit2.RemoteCallbacks(credentials=pygit2.KeypairFromAgent(username)))

def merge(repo: Repository, branch: str | None = None):
    for branch_bytes in repo.raw_listall_branches(pygit2.GIT_BRANCH_LOCAL):
        branch_string = branch_bytes.decode("utf-8")
        print(branch_string)
        # branch = repo.branches.get(branch_string)
        # for remote in repo.remotes:
        #     # print(repo.branches[f"{branch_string}"].target)
        #     print(repo.resolve_refish(f"{branch_string}"))
        #     print(repo.resolve_refish(f"{remote.name}/{branch_string}"))
        #     # local_known_hash = repo.resolve_refish(f"{branch_string}")
        #     # remote_known_hash = repo.branches[f"{remote.name}/{branch_string}"].target.hex
        #     # commits_ahead, commits_behind = repo.ahead_behind(local_known_hash, remote_known_hash)
        #     # if commits_ahead == 0:
        #     #     print("do the merge")

def merge(repo: Repository, auto_merge: bool=False):
    if dirty(repo):
        return
    head = repo.head
    for branch_bytes in repo.raw_listall_branches(pygit2.GIT_BRANCH_LOCAL):
        branch_string = branch_bytes.decode("utf-8")
        branch = repo.branches.get(branch_string)
        repo.checkout(branch)
        for remote in repo.remotes:
            remote_master_id = repo.lookup_reference(f"refs/remotes/{remote.name}/{branch_string}").target
            merge_result, _ = repo.merge_analysis(remote_master_id)
            # Up to date, do nothing
            if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                return
            # We can just fastforward
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                repo.checkout_tree(repo.get(remote_master_id))
                try:
                    master_ref = repo.lookup_reference(f"refs/heads/{branch_string}")
                    master_ref.set_target(remote_master_id)
                except KeyError:
                    pass
                    # repo.create_branch(branch_string, repo.get(remote_master_id))
                repo.head.set_target(remote_master_id)
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
                pass
                # if auto_merge:
                #     repo.merge(remote_master_id)

                #     if repo.index.conflicts is not None:
                #         for conflict in repo.index.conflicts:
                #             print(f"Conflicts found in: {conflict[0].path}")
                #         raise AssertionError('Conflicts, ahhhhh!!')

                #     user = repo.default_signature
                #     tree = repo.index.write_tree()
                #     commit = repo.create_commit('HEAD',
                #                                 user,
                #                                 user,
                #                                 'Merge!',
                #                                 tree,
                #                                 [repo.head.target, remote_master_id])
                #     # We need to do this or git CLI will think we are still merging.
                #     repo.state_cleanup()
            else:
                raise AssertionError('Unknown merge analysis result')
        # endfor remotes
    # endfor branches
    repo.checkout(head)

def dirty(repo, ignore_flags=[pygit2.GIT_STATUS_IGNORED]):
    ignore_mask = reduce(lambda x, y: x | y, ignore_flags)
    inverse_mask = ~ ignore_mask
    return { filepath: flag for filepath, flag in repo.status().items() if flag & inverse_mask }
