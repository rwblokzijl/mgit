# Next steps

rename tags to tags

## Sync mechanic. How does it work

### Intro

- "branches" need to be synced through all remotes
- syncing local branches to remote is handled through the local branch tracking the remote:
    * [branch "master"]
	    remote = bagn
	    merge = refs/heads/master
- For the remote branch, it specifies the remote name as well as the head IN THE REMOTE (not the local fetched head)
- we want to fetch from a remote, then the next, then the next
- problem is we sometimes need to merge in between, this has to be handled manually by the user
- usually git merge strategies will handle the merge

## Config:
- option 1:
    * remote1:branch/name = local/branch
    * remote2:branch/name = local/branch

- option 2:
    - remote1:branch/name = tag # ignores local and tracks directly between remotes
    - remote2:branch/name = tag

changeing the config:

`mgit track [REPO] [tag?? | localbranch] [[remote_branch]..] `

remote_branches can be specified as a remote, this infers branch from local or
specify explicitly: remote:branch

## usage

- Multi REPO
- specify branches
    * default = all
- secify a subset of remotes to use

take (all branches in all "repos" if branch is in the input)
<push/sync/pull/fetch/merge> to/from all those branches to all remotes

Multiple repo and branches seem to be in conflict, and really they are..., but i
see no reason to not push all "masters" to a subset of remotes. One issue is it
might be confusing to users

`mgit fetch [REPOS] branches remotes`

1. Fetch all remotes

`mgit merge [REPOS] branches remotes`

- Merge currently copies of remotes into local branches

`mgit pull [REPOS] branches remotes`

- Fetch followed by merge
- If some remotes conflict, cancel the merge and include the "error" in the
  "check"

`mgit push [REPOS] branches remotes`

1. Push to all remotes

`mgit sync [REPOS] branches remotes`

- Pull followed by push

## Usage

1. Define BranchRelation s (formerly auto commands)

    - mgit push:
        * push all branches to all remotes
        * refspecs map the push branches # not managed (maybe later)
        * refspecs map the fetch branches # not managed (maybe later)
        * tracking maps the merge (pull) # not managed (maybe later)
        * we mass fetch remote* branch*

    - Less granular, allows :
        * remote1:rbranch:lbranch

# Development notes

## How to select multiple repos

Program chooses, must define for readability??:
1. require config
2. require system
3. combine

- all (in config)
- name* + path*
- recursive path (system only)

- [installed]
- [missing]
    * [archived] include archived repos

## The conflict problem

1. Make combine raise if it doesnt work
2. Make check print the error
3. Make update auto-fix the issue
4. Use combine everywhere??

The code:
we need ways to recombine all fields
combine - only if matches
merge   - combine fields

## The parent problem

We would like to keep track of repos in repos.

Git has submodules already

1. What really is the core of mgit
    a. Track a single repo across multiple locations
    b. syncing
    c. act as a package manager
2. Do we need to track "parents".
    a. It specifies a the place where the repo was initially found
    b. Does git submodules not already do this?
3. Parents really are just a 'back link' for the submodules.
    a. Submodules specify dependencies
    b. Parents specify ...? what?
4. Parents do define the path of a repo based on its parent
    a. if we track the repo and its parent, then the moving of the parent should
    also move the child.
    b. If the parent is not installed, there is no way of knowing this happens
    c. Keeping track of the parent is one way to do this.
    d. A better way might be to keep track of the submodules instead
    e. submodule-name=path ; doesnt allow for multiple instances of the same repo
    f. submodule-path=name:commit ; does?
    g. submodule-path=name ; maybe we dont want to know about the current commit as we auto update these anyway, and this is stored in the repo regardless
    h. This is nice for later, but for now we just use the path

## Fetch all

By fetching all repos from all remotes we set up the status command to show
complete information

mgit fetch is a multi repo command

for repo in args
    for remote in repo
        fetch all branches

## Backup system

We want all repos to exist in at least 2 remotes

to ensure this we use the catergory system, which we will rename to tags

- Repos can have multiple tags
- Remotes will be have some backup tags
- for every tag of a remote
    * all repos of that tag should have a copy in that remote

We need the following commands:

- mgit backup check
    * prints all repos with a tag, that are missing from remotes with that tag
    * prints all repos that have less than 2 remotes configured to track it
- mgit backup update
    * will instantiate all missing repos in their assigned remotes
- mgit backup sync (maybe mgit sync)
    * will make sure all remotes are up to date with one another
    * If possible this should work without

## Tag system


