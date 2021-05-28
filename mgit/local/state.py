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
    LOCAL  = 4

@dataclass(frozen=True)
class Remote:
    name:        str
    url:         str
    path:        str
    type: RemoteType

    def get_url(self) -> str:
        if self.url:
            return f"{self.url}:{self.path}"
        else:
            return self.path

    def get_subpath(self, remote_repo: 'RemoteRepo') -> Optional[str]:
        if not remote_repo.url.startswith(self.get_url()):
            return None
        if self.url:
            path = remote_repo.url[len(self.url + ":"):]
        else:
            path = remote_repo.url
        if not self.path:
            return path
        try:
            return str(Path(path).relative_to(Path(self.path)))
        except ValueError:
            return None

    def __contains__(self, element: 'RemoteRepo'):
        if isinstance(element, NamedRemoteRepo):
            return element.remote == self
        elif isinstance(element, UnnamedRemoteRepo):
            return self.get_subpath(element) is not None
        else:
            return False

@dataclass # type: ignore # mypy cannot handle abstract classes properly for some annoying reason
class RemoteRepo(ABC):
    @abstractmethod
    def represent(self, indent=0):
        raise NotImplementedError("Subclass should implement")

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError("Subclass should implement")

    @property
    # @abstractmethod # makes mypy error..., but really should be set
    def url(self) -> str:
        raise NotImplementedError("Subclass should implement")

    def compare(self, other):
        return isinstance(other, RemoteRepo) and self.url == other.url and self.name == other.name

    def remote_key(self) -> str:
        return f"{self.name}:{self.url}"

    def __repr__(self) -> str:
        return f"{self.url} {self.name}"

@dataclass(frozen=True, repr=False)
class NamedRemoteRepo(RemoteRepo):
    remote: Remote
    project_name: str

    def represent(self, indent=0):
        return " " * (indent) + f"{self.remote.name}:{self.project_name}\n"

    @property
    def name(self):
        return self.remote.name

    @property
    def path(self):
        return os.path.join(self.remote.path, self.project_name)

    @property
    def url(self) -> str:
        if self.remote.url:
            return self.remote.url + ":" + self.path
        else:
            return self.path

    def __repr__(self) -> str:
        return f"Named: {self.url} {self.name}"

@dataclass(frozen=True, repr=False)
class UnnamedRemoteRepo(RemoteRepo):
    remote_name:   str
    url: str
    _url: str = field(init=False, repr=False)

    def represent(self, indent=0):
        return " " * (indent) + f"{self.remote_name}:{self.url}\n"

    @property
    def name(self):
        return self.remote_name

    @property             # type: ignore
    def url(self) -> str: # type: ignore # pylint: disable=E0102 # Redefinition is needed
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        object.__setattr__(self, '_url', url)

    def __repr__(self) -> str:
        return f"Unnamed: {self.url} {self.name}"

@dataclass(frozen=True)
class RemoteBranch:
    remote_repo: RemoteRepo
    ref:         str # can be *

@dataclass(frozen=True)
class LocalBranch:
    ref:         str

@dataclass(frozen=True)
class AutoCommand:
    remote_branches: Set[RemoteBranch] #needs at least 1, thus no default
    local_branch:    Optional[LocalBranch] = None
    fetch:           bool                  = False
    push:            bool                  = False
    commit:          bool                  = False

@dataclass(frozen=True)
class Conflict:
    key: str
    left:  "RepoState"
    right: "RepoState"

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        left  = self.left.__getattribute__(self.key)
        right = self.right.__getattribute__(self.key)
        if type(left) == type(right) == set:
            left, right = left - right, right - left
        return f"{self.left.name or self.right.name}: {self.key} in {self.left.source} ({left}) doesn't match {self.key} in {self.right.source} ({right})"

@dataclass
class RepoState:   # No defaults to catch changes around the code
    source:        str                   = field(repr=False, compare=False)
    name:          Optional[str]
    repo_id:       Optional[str]
    path:          Optional[Path]
    parent:        Optional['RepoState']
    remotes:       Set[RemoteRepo]
    # origin:        Optional[RemoteRepo]
    auto_commands: Optional[Set[AutoCommand]]
    archived:      Optional[bool]
    tags:    Optional[Set[str]]

    # def __eq__(self, other):
    #     return self.compare(other, hard=True) == []

    def represent(self, step:int =2, verbosity=1) -> str:
        if verbosity == 0:
            return self.name or ""
        result = [""] # put string in list to make it mutable for the function below
        def add_line(line, indent=step):
            result[0] += " " * (indent) + line + "\n"
        if verbosity == 2:
            add_line((self.name or '') + ":" + self.source or "")
        else:
            add_line((self.name or '') + ":")
        add_line(f"repo_id = {self.repo_id or ''}")
        add_line(f"path = {self.path or ''}")

        if self.parent:
            add_line(f"parent = {self.parent.name}")
        elif verbosity ==2:
            add_line("parent = ")

        add_line("remotes = ")
        for remote in self.remotes:
            result[0] += remote.represent(step*2)

        # if self.origin:
        #     result[0] += " " * (step) + "origin = " + self.origin.represent()

        if self.auto_commands is not None:
            add_line("auto_commands = ")
            for auto in self.auto_commands:
                result[0] += " " * (step) + str(auto)#.represent(step)

        add_line(f"archived = {self.archived or False}")
        if self.tags is not None:
            add_line(f"tags = {', '.join(self.tags)}")
        elif verbosity ==2:
            add_line("tags = ")
        return result[0].strip()

    def zip(self, other) -> Iterator[Tuple]:
        ignored = ["source"]

        keys = list(asdict(self).keys())

        for i in ignored:
            keys.remove(i)

        ours   = [ self.__getattribute__(key) for key in keys]
        theirs = [other.__getattribute__(key) for key in keys]

        return zip(keys, ours, theirs)

    def compare(self, other: "RepoState", hard=False) -> List[Conflict]:
        "Returns a list of conficts"
        if other is None:
            return None

        ans: List[Conflict] = []
        for key, our, their in self.zip(other):
            if not self.compare_key(key, our, their, hard):
                ans.append( Conflict( key=key, left=self, right=other))
        return ans

    def compare_key(self, key, our, their, hard=False):
        if (    our   is not None and
                their is not None and
                our != their):
            if key == "remotes" and not hard:
                our_remotes = sorted([r.remote_key() for r in our])
                their_remotes = sorted([r.remote_key() for r in their])
                if our_remotes == their_remotes:
                    return True
                return False
        return True

    def __lt__(self, other):
        """Sorting happens on path"""
        if str(other.path.expanduser()).startswith(str(self.path.expanduser())):
            return True
        else:
            return str(self.path) < str(other.path)

    def __add__(self, other: "RepoState") -> 'RepoState':
        repo_state: dict = {"source": ""}
        for key, our, their in self.zip(other):
            if not self.compare_key(key, our, their, hard=False):
                raise self.StateConflict(f"{our} != {their}")

            if our is None:
                repo_state[key] = their
            else:
                repo_state[key] = our

        # add all remotes to a
        remotes = {remote.remote_key():remote for remote in self.remotes}
        remotes.update({remote.remote_key():remote for remote in other.remotes})

        # add all named remotes and overwrite those with same name:url
        remotes.update({remote.remote_key():remote for remote in self.remotes if isinstance(remote, NamedRemoteRepo)})
        remotes.update({remote.remote_key():remote for remote in other.remotes if isinstance(remote, NamedRemoteRepo)})

        repo_state["remotes"] = set(remotes.values())

        # origin = self.origin or other.origin #might be None
        # for remote in remotes:
        #     if remote == origin:
        #         origin = remote
        #         break
        # repo_state["origin"] = origin

        repo_state['tags'] = (self.tags or set()).union(other.tags or set())

        return RepoState(**repo_state)

    class StateConflict(Exception):
        pass

