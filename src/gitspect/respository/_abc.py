from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path

__all__ = ["CommitId", "BlobId", "Commit", "RepositoryFile", "Repository"]

CommitId = str
BlobId = str


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


class Diff(ABC):
    @property
    @abstractmethod
    def before_file(self) -> RepositoryFile:
        pass

    @property
    @abstractmethod
    def after_file(self) -> RepositoryFile:
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
    def list_diff_files(self, commit_id: CommitId) -> Iterable[RepositoryFile]:
        pass

    @abstractmethod
    def read_blob(self, blob_id: BlobId) -> str:
        pass
