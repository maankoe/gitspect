import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import List, Tuple
from ._abc import Commit, Repository, CommitId
from ._git_commit import GitCommit

__all__ = ["GitRepository"]


class GitRepository(Repository):
    def __init__(self, path: Path):
        if not _is_repo(path):
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


def _is_repo(path: Path) -> bool:
    cmd = ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"]
    try:
        return (
            subprocess.run(cmd, capture_output=True, check=True).stdout.decode().strip()
            == "true"
        )
    except subprocess.CalledProcessError:
        return False


class RunGit:
    def __init__(self, cmd: List[str], errors_acceptable: bool = False):
        self._cmd = cmd
        self._errors_acceptable = errors_acceptable
        self._process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self._errors = []

    def iter_lines(self) -> Iterable[Tuple[int, str]]:
        for ci, commit_line in enumerate(self._process.stdout.readlines()):
            if self.errors():
                raise GitError(self.errors())
            yield ci, commit_line.decode().strip()

    def errors(self) -> str:
        self._errors.extend(
            [line.decode().strip() for line in self._process.stderr.readlines()]
        )
        return "\n".join(self._errors)

    def __enter__(self):
        self._process.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._process.stdout.close()
        self._process.__exit__(exc_type, exc_val, exc_tb)


class GitError(Exception):
    pass
