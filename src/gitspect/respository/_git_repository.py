import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import List, Tuple
from ._abc import Commit, Repository, CommitId
from ._git_commit import GitCommit

__all__ = ["GitRepository"]


class GitRepository(Repository):
    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def commits(
        self, start: int = 0, end: int = None, reverse: bool = False
    ) -> Iterable[Commit]:
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


def _commit_from_oneline(repo: "GitRepository", line: str) -> Commit:
    hash_end = line.index(" ")
    yield GitCommit(repo, commit_id=line[:hash_end], message=" ".join(line[hash_end:]))


class RunGit:
    def __init__(self, cmd: List[str]):
        self._cmd = cmd
        self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    def iter_lines(self) -> Iterable[Tuple[int, str]]:
        for ci, commit_line in enumerate(self._process.stdout.readlines()):
            yield ci, commit_line.decode().strip()

    def __enter__(self):
        self._process.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._process.stdout.close()
        self._process.__exit__(exc_type, exc_val, exc_tb)
