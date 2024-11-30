from pathlib import Path

from ._abc import Repository, RepositoryFile

__all__ = ["GitRepositoryFile"]


class GitRepositoryFile(RepositoryFile):
    def __init__(self, repo: Repository, path: Path):
        self._repo = repo
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def __eq__(self, other):
        return (
            isinstance(other, GitRepositoryFile)
            and self._repo == other._repo
            and self._path == other._path
        )
