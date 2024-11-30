from ._abc import Commit, Repository

__all__ = ["GitCommit"]


class GitCommit(Commit):
    def __init__(self, repo: Repository, commit_id: str, message: str = None):
        self._repo = repo
        self._commit_id = commit_id
        self._message = message

    @property
    def commit_id(self) -> str:
        return self._commit_id

    @property
    def message(self) -> str:
        return self._message or NotImplemented(
            "Null message will be supported, but not now"
        )

    def __eq__(self, other):
        return (
            isinstance(other, GitCommit)
            and self._repo == other._repo
            and self._commit_id == other._commit_id,
        )

    def __hash__(self):
        return hash(
            (
                self._repo,
                self._commit_id,
            )
        )

    def __str__(self) -> str:
        display_items = [self._commit_id]
        if self._message:
            display_items.append(self._message)
        return f"{self.__class__.__name__}({", ".join(display_items)})"

    __repr__ = __str__
