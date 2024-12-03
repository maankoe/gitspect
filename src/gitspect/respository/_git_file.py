from pathlib import Path

from ._abc import Repository, RepositoryFile, BlobId

__all__ = ["GitRepositoryFile"]


class GitRepositoryFile(RepositoryFile):
    def __init__(self, repo: Repository, path: Path, blob_id: BlobId):
        self._repo = repo
        self._path = path
        self._blob_id = blob_id

    @property
    def path(self) -> Path:
        return self._path

    def __eq__(self, other):
        return (
            isinstance(other, GitRepositoryFile)
            and self._repo == other._repo
            and self._blob_id == other._blob_id
            and self._path == other._path
        )
