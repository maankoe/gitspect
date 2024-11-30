from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path

__all__ = ["CommitId", "Commit", "RepositoryFile", "Repository"]

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


class RepositoryFile(ABC):
    @property
    @abstractmethod
    def path(self) -> Path:
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

    @abstractmethod
    def commits_between(self, start: str, end: str = None) -> Iterable[Commit]:
        pass

    @abstractmethod
    def list_files(self, commit_id: CommitId) -> Iterable[RepositoryFile]:
        pass

    @abstractmethod
    def read_file(self, commit_id: CommitId, file: RepositoryFile) -> str:
        pass
