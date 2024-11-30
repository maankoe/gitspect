__all__ = ["RunGit", "GitError", "is_repo"]

import subprocess
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Tuple


class RunGit:
    def __init__(self, cmd: Sequence[str], errors_acceptable: bool = False):
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
            yield ci, commit_line.decode()

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


def is_repo(path: Path) -> bool:
    cmd = ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"]
    try:
        return (
            subprocess.run(cmd, capture_output=True, check=True).stdout.decode().strip()
            == "true"
        )
    except subprocess.CalledProcessError:
        return False


class GitError(Exception):
    pass
