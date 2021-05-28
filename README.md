title: Mgit - your personal package manager

# Introduction

`mgit` is a wrapper around the popular VCS `git` that aids the maintenance of
repos across multiple remotes and developer machines. It maintains a list of all
repos available across your digital environment and provides a single management
source, while allowing files to be stored distributed.

# Mgit

## Repos

A developer will create many repos across their lifetime. These might not only
be for code, but also management of other files. Keeping all these repos backed
up and findable across multiple workstations and remote storage solutions can be
a real challenge.

## Remotes

There are some local git configurations that could benefit from being
maintained for each repo.

**Remotes** - When cloning a repo there is no information included on where to
find other remotes that have the same repo. Storing this enables easy backup of
repos and switching of remotes if one is to go down.

**Tracked branches** - In git local branches and remote branches have no "real"
link. They might diverge at any time. On a user level, local branches can
"track" remote branches, but git provides no such function across remotes.
Maintaining "tracking" information between multiple remote branches provides a
framework to keep different remotes up to date with eachother.

## Commands

Using the information stored about the repos, we define the following commands.

### `mgit` `pull` / `fetch` / `push`

These commands perform their respective functions but on all tracked branches at
the same time.

### `mgit auto`

This is the mechanism thats used to keep the remotes up to date with eachother.

The auto command is used to set up automatic commit, fetch, pull and push for
a repos branches. These are then performed for all repos on the system for which
automatic actions are configured.

### `mgit init`

This follows the same logic as `git init` but also initiates the repo in the
config ans allows the user to specify remotes, in which the repo will also be
initiated. Default remotes can be specified for when no remotes are specifies
with the `init` command.

### `mgit add`

Adds the current repo and its remotes to the config.

### `mgit remote`

Perform remote actions on the repo and the config, like adding, changing or
removing remotes, as well as specifying the default upstream.

### `mgit remotes` `add` / `remote` / `t` / `t`

Remotes (plural) handles the remotes that `mgit` should be aware of. This is
only required for automatic instantiation of repos in a remote as it specifies
the process necessary. For now only 1 type is supported: ssh, but gitlab and
github support might follow at some point.

#### `mgit remotes list <remote>`

This also allows `mgit` to list all repos in the remote.

### More commands...

# Implementation

The `mgit` program has 2 general functions

1. Maintain and mutate the "desired state" of repos
2. Act on the current state of repos

## Mutating the state

All commands that mutate the state do so in the following way:

1. take a "state description" of repos from a "state source"
2. And write that state to a "sink"

1. State source examples
    a. repo on system
    b. config
    c. user input
2. State sink examples
    a. repo on system
    b. config
    c. user screen

The business logic is this contained in the "state description" object and "state source" and "state sink":

### State description

- Repo
    - name
    - system_path
    - remotes: List<RemoteRepo>
    - parent: Repo?
    - BranchLinks: List<BranchLink>
    - repo_id
- RemoteRepo
    * name
- NamedRemoteRepo<RemoteRepo>
    * Remote
- Remote
    * name: str
    * url-prefix: str # path where repos are to be found
    * type: TYPE [ssh, github, gitlab...]
- UnnamedRemoteRepo<RemoteRepo>
    * url
- AutoCommand ??? This part is hard to define yet
    * local_ref: str (branchname, None is all)
    * remote_branches: List<RemoteRepoBranch>
    * Fetch: Bool
    * Push:  Bool
    * Pull: Bool
    * Commit: Bool
- RemoteBranch
    * remote_repo: RemoteRepo
    * ref: str
- LocalBranch
    * ref: str

tracked-branches:
  - branch:
    name: "val"
The remote state description =



### Source interface

### Code flow:
1. User command specifies:
    a. Source
    b. Sink
    c. (sub) state
2.

## command structure

We would like the commands to follow the git logic

mgit


## General code flow

1. Recursive sub parsers to achieve the goals

### Parse commands

There seem to be 2 main objectives:

1. Single repo commands
    a. Maintaining remotes
    b. Syncing brances
    c. etc
2. Commands for doing the same actions for multiple repos

## Commands

All commands have these main effects

1. Config
    a. Show the configuration state
    b. Change the configuration state
2. Repo
    a. Show the repo state compared to the config
    b. Update the repo state to match the congig

example: `mgit remote`



### Single repo commands

These are the normal git repo manipulation commands

prefix: `mgit`

1. remote

#### Config editing commands

add       |        | path, name              | add a repo (init remote?)
move      |        | path, name              | move a repo to another path
remove    |        | name                    | stop tracking a repo
rename    |        | name, name              | rename the repo in the config
archive   |        | name                    | add archive flag to
unarchive |        | name                    | remove archive flag to
clone     |        | name, remote            | clone a repo to an existing remote
show      |        | name                    | show a repo by name


### Multiple repo

prefix `mgit -g`


update    | update properties about the repos that can be infered
sanity    | full sanity check of all repos/remotes/configs
config    | commands for handling the configs

"repo remote"
remote    | add    | repo, remote, name      | add a remote to the repo, and vv
remote    | remove | repo, remote, name      | remove a remote from the repo, and vv
remote    | origin | repo, remote, name      | set a remote as origin, and vv

"mass repo"
list      | -l -r [remotes] | list repos, (missing remote)
fetch     | repos, remotes  | mass fetch
pull      | repos, remotes  | mass pull
push      | repos, remotes  | mass push (after shutdown)

"automatic git functions" - stored: auto-[remote]-[branch] = [commit] [push] [pull] [fetch]
auto      | add    | repo, branch, [commit] [push] [pull] [fetch], [[REMOTE]..] | add auto function to repo |
auto      | remove | repo, branch, [commit] [push] [pull] [fetch], [[REMOTE]..] | remove auto function from branch |

auto      | commit | commit branches with auto commit configured (warn when wrong branch is checked out)
auto      | push   | push branches with auto push configured
auto      | fetch  | fetch branches with auto fetch configured
auto      | pull   | pull branches with auto pull configured

"remotes"
remotes   | list   |                | list remotes
remotes   | add    | name, url      | add a remote
remotes   | remove | name           | remove a remote
remotes   | init   | name, remote   | init repo in remote
remotes   | delete | name, remote   | remove repo from remote, maybe not implement for safety!!!
remotes   | clone  | repos, remote  | clone to remotes to another https://stackoverflow.com/questions/7818927/git-push-branch-from-one-remote-to-another
remotes   | show   | name           | show the remote and its repos
remotes   | check  | repos, remotes | find non up to date repos across all remotes
remotes   | sync   | repos, remotes | fix non up to date repos across all remotes




## Configuration storage

Storing information IN the repos has some issues. For shared repos, the
configuration is visible and susceptible to other developers who have their own
repo management solutions. Its desirable to have mgit be localised to the users
machines and stay transparent to other developers. All action should also be
done without requiring any non-git actions by the remotes. For this reason we
store all mgit information in a global config file.

##

Backing up of repos is not easily done automatically. Pushing to other remotes
is possible but requires manual maintenance of the remotes and manutal pushed
to multiple remotes.

Cloning does not include all known remotes. Every repo has 1 upstream that
cannot go down.

### Multiple machines

My local repos do not have information about changes on the remotes.

## Solution

Maintain information on extra remotes "in the repo".

# Desired commands

General:
|------|--------|----------------------------------------------------------------------------|
|      | update | update properties about the repos that can be infered                      |
| TODO | check  | full sanity check of all repos/remotes/configs                             |

repo config actions:
|------|-----------|--------|-------------------------|---------------------------------------------------------|
|      | show      |        | name                    | show a repo by name                                     |
|      | init      |        | path, [[remote name]..] | init a repo local and remote                            |
| todo | add       |        | path, name              | add a repo (init remote?)                               |
| todo | move      |        | path, name              | move a repo to another path                             |
| todo | remove    |        | name                    | stop tracking a repo                                    |
|      | rename    |        | name, name              | rename the repo in the config                           |
|      | archive   |        | name                    | add archive flag to                                     |
|      | unarchive |        | name                    | remove archive flag to                                  |
|      | install   |        | name                    | install a repo from remote by name (add listed remotes) |
|      | tag  |        |                         | tag actions                                        |
|      |           | list   |                         | lists all tags                                    |
|      |           | show   | tag                | show the tag and children                          |
|      |           | add    | repo, tag          | add tag                                            |
|      |           | remove | repo, tag          | remote tag                                         |
| TODO | remote    |        |                         | Repo remote actions                                     |
| TODO |           | add    | repo, remote, name      | add a remote to the repo, and vv                        |
| TODO |           | remove | repo, remote, name      | remove a remote from the repo, and vv                   |

mutli repo actions:
|--------|----------|------------------|------------------------------------------------|
|        | dirty    | repos            | is any repo dirty                              |
|        | status   | repos            | show status of all repos (clean up ordering)   |
| ------ | -------- | ---------------- | ---------------------------------------------- |
| TODO   | fetch    | repos, remotes   | mass fetch                                     |
| TODO   | pull     | repos, remotes   | mass pull                                      |
| TODO   | push     | repos, remotes   | mass push (after shutdown)                     |

remote actions:
|--------|-----------|----------|------------------|----------------------------------------------------------------|
| TODO   | remotes   |          |                  | manage remotes                                                 |
|--------|-----------|----------|------------------|----------------------------------------------------------------|
| TODO   |           | list     |                  | list remotes                                                   |
| TODO   |           | add      | name, url        | add a remote                                                   |
| TODO   |           | remove   | name             | remove a remote                                                |
| ------ | --------- | -------- | ---------------- | -------------------------------------------------------------- |
| TODO   |           | init     | name, remote     | init repo in remote                                            |
| TODO   |           | delete   | name, remote     | remove repo from remote, maybe not implement for safety!!!     |
| TODO   |           | clone    | repos, remote    | clone to remotes to another                                    |
| ------ | --------- | -------- | ---------------- | -------------------------------------------------------------- |
| TODO   |           | show     | name             | show the remote and its repos                                  |
| TODO   |           | check    | repos, remotes   | find non up to date repos across all remotes                   |
| TODO   |           | sync     | repos, remotes   | fix non up to date repos across all remotes                    |
|--------|-----------|----------|------------------|----------------------------------------------------------------|

branch actions:

REF: REF/REF | string | *

LOCAL : REF

BRANCH: REMOTE:REF | LOCAL
example: +refs/heads/*:refs/remotes/home/*

[branch "master"]
	remote = bagn
	merge = refs/heads/master

|------|--------|--------|--------------------------|------------------------------------|
| TODO | branch |        |                          |                                    |
| TODO |        | merge  | [LINK_NAME] [[BRANCH]..] |                                    |
| TODO |        | push   | [LINK_NAME]              |                                    |
| TODO |        | pull   | [LINK_NAME]              | git already has mass fetch i think |

| TODO |  | commit | [LINK_NAME] | commit all |

"""


