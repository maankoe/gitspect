from collections.abc import Iterable
from pathlib import Path
from ._abc import Commit, Repository, CommitId
from ._git_commit import GitCommit
from ._git_runner import RunGit, is_repo

__all__ = ["GitRepository"]


class GitRepository(Repository):
    def __init__(self, path: Path):
        if not is_repo(path):
            raise ValueError("Not a git repository path")
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def commits(
        self, start: int = 0, end: int = None, reverse: bool = False
    ) -> Iterable[Commit]:
        if start < 0:
            raise ValueError(f"start must be non-negative, start={start}")
        if end < start:
            raise ValueError(
                f"end must be greater than or equal to start, start={start}, end={end}"
            )
        cmd = ["git", "log", "--format=oneline"]
        if reverse:
            cmd.append("--reverse")
        end = float("inf") if end is None else end
        with RunGit(cmd) as git:
            for ci, line in git.iter_lines():
                if start <= ci <= end:
                    yield _commit_from_oneline(self, line)
                elif ci > end:
                    break

    def commits_between(
        self, start: CommitId, end: CommitId = None
    ) -> Iterable[Commit]:
        cmd = ["git", "log", "--format=oneline", f"{start}..{end or ""}"]
        with RunGit(cmd) as git:
            for ci, line in git.iter_lines():
                yield _commit_from_oneline(self, line)
            errors = git.errors()
            if errors:
                raise ValueError(errors)


def _commit_from_oneline(repo: "GitRepository", line: str) -> Commit:
    hash_end = line.index(" ")
    return GitCommit(repo, commit_id=line[:hash_end], message=" ".join(line[hash_end:]))
