from abc         import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum        import Enum
from pathlib     import Path
from typing      import List, Optional, Set, Tuple, Iterator

import os

class RemoteType(Enum):
    SSH = 1
    GITHUB = 2
    GITLAB = 3

@dataclass(frozen=True)
class Remote:
    name:        str
    url:         str
    path:         str
    remote_type: RemoteType

@dataclass
class RemoteRepo:
    @abstractmethod
    def represent(self, indent=0):
        raise NotImplementedError("Subclass should implement")

    @abstractmethod
    def get_name(self):
        raise NotImplementedError("Subclass should implement")

    @abstractmethod
    def get_url(self):
        raise NotImplementedError("Subclass should implement")

    def __eq__(self, other):
        return self.get_url() == other.get_url() and self.get_name() == other.get_name()

    def __hash__(self):
        return hash((self.get_url(), self.get_name()))

    def __repr__(self):
        return f"{self.get_url()} {self.get_name()}"

@dataclass(frozen=True, eq=False, repr=False)
class NamedRemoteRepo(RemoteRepo):
    remote: Remote
    project_name: str

    def represent(self, indent=0):
        return " " * (indent) + f"{self.remote.name}:{self.project_name}\n"

    def get_name(self):
        return self.remote.name

    def get_url(self):
        return self.remote.url + ":" + os.path.join(self.remote.path, self.project_name)

@dataclass(frozen=True, eq=False, repr=False)
class UnnamedRemoteRepo(RemoteRepo):
    remote_name:   str
    url: str

    def represent(self, indent=0):
        return " " * (indent) + f"{self.remote_name}:{self.url}\n"

    def get_name(self):
        return self.remote_name

    def get_url(self):
        return self.url

@dataclass(frozen=True)
class RemoteBranch:
    remote_repo: RemoteRepo
    ref:         str

@dataclass(frozen=True)
class LocalBranch:
    ref:         str

@dataclass(frozen=True)
class AutoCommand:
    remote_branches: Set[RemoteBranch] #needs at least 1, thus no default
    local_branch:    Optional[LocalBranch] = None
    fetch:           bool                  = False
    push:            bool                  = False
    pull:            bool                  = False
    commit:          bool                  = False

@dataclass(frozen=True)
class Conflict:
    key: str
    left: "RepoState"
    right: "RepoState"

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.key} in {self.left.source} ({self.left.__getattribute__(self.key)}) doesn't match {self.key} in {self.right.source} ({self.right.__getattribute__(self.key)})"

@dataclass(frozen=True)
class RepoState:   # No defaults to catch changes around the code
    source:        str                   = field(repr=False, compare=False)
    name:          Optional[str]
    repo_id:       Optional[str]
    path:          Optional[Path]
    parent:        Optional['RepoState']
    remotes:       Set[RemoteRepo]
    origin:        Optional[RemoteRepo]
    auto_commands: Optional[Set[AutoCommand]]
    archived:      Optional[bool]
    categories:    Optional[Set[str]]

    def represent(self, indent=0) -> str:
        result = [""]
        def add_line(line):
            result[0] += " " * (indent) + line + "\n"
        # add_line(f"name = {self.name or ''}")
        add_line(f"repo_id = {self.repo_id or ''}")
        add_line(f"path = {self.path or ''}")

        if self.parent:
            add_line(f"parent = {self.parent.name}")

        add_line(f"remotes = ")
        for remote in self.remotes:
            result[0] += remote.represent(indent+2)

        if self.origin:
            result[0] += " " * (indent) + "origin = " + self.origin.represent()

        if self.auto_commands is not None:
            add_line(f"auto_commands = ")
            for auto in self.auto_commands:
                result[0] += " " * (indent+2) + str(auto)#.represent(indent+2)

        add_line(f"archived = {self.archived or False}")
        if self.categories is not None:
            add_line(f"categories = {', '.join(self.categories)}")
        return result[0]

    def zip(self, other) -> Iterator[Tuple]:
        ignored = ["source"]

        keys = list(asdict(self).keys())

        for i in ignored:
            keys.remove(i)

        ours   = [ self.__getattribute__(key) for key in keys]
        theirs = [other.__getattribute__(key) for key in keys]

        return zip(keys, ours, theirs)

    def compare(self, other: "RepoState") -> List[Conflict]:
        "Returns a list of conficts"

        ans: List[Conflict] = []
        for key, our, their in self.zip(other):
            if (    our   is not None and
                    their is not None and
                    our != their):
                ans.append( Conflict( key=key, left=self, right=other))
        return ans

    def __add__(self, other: "RepoState") -> Optional["RepoState"]:
        repo_state: dict = {"source": ""}
        for key, our, their in self.zip(other):
            if (    our   is not None and
                    their is not None and
                    our != their):
                return None

            if our is None:
                repo_state[key] = their
            else:
                repo_state[key] = our

        # add all named remotes
        remotes: Set[RemoteRepo]  = {remote for remote in self.remotes if isinstance(remote, NamedRemoteRepo)}
        remotes |= {remote for remote in other.remotes if isinstance(remote, NamedRemoteRepo)}

        # afterwards add unnamed remotes (will not add to set if an "equal" named exits
        remotes |= self.remotes
        remotes |= other.remotes

        repo_state["remotes"] = remotes

        origin = self.origin or other.origin #might be None
        for remote in remotes:
            if remote == origin:
                origin = remote
                break
        repo_state["origin"] = origin

        repo_state['categories'] = (self.categories or set()).union(other.categories or set())

        return RepoState(**repo_state)

