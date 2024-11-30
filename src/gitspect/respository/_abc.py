from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path

__all__ = ["CommitId", "Commit", "Repository"]

CommitId = str


class Commit(ABC):
    @property
    @abstractmethod
    def commit_id(self) -> CommitId:
        pass

    @property
    @abstractmethod
    def message(self) -> str:
        pass


class Repository(ABC):
    @property
    @abstractmethod
    def path(self) -> Path:
        pass

    @abstractmethod
    def commits(
        self, start: int = 0, end: int = None, reverse: bool = False
    ) -> Iterable[Commit]:
        pass

    def commits_between(self, start: str, end: str = None) -> Iterable[Commit]:
        pass
