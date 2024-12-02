from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Callable, Tuple

from ._abc import Commit, Repository, CommitId, RepositoryFile
from ._git_commit import GitCommit
from ._git_file import GitRepositoryFile
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
        cmd = ["git", "rev-list", "--all", "--format=%s%n%H"]
        if reverse:
            cmd.append("--reverse")
        print(" ".join(cmd))
        end = float("inf") if end is None else end
        with RunGit(cmd) as git:
            yield from CommitsParser(
                self, lambda index, builder: start <= index <= end
            ).parse(git.iter_lines())

    def commits_between(
        self, start: CommitId, end: CommitId = None
    ) -> Iterable[Commit]:
        cmd = ["git", "rev-list", "--format=%s%n%H", f"{start}..{end or ""}"]
        print(" ".join(cmd))
        with RunGit(cmd) as git:
            yield from CommitsParser(self, lambda index, builder: True).parse(
                git.iter_lines()
            )
            if git.errors():
                raise ValueError(git.errors())

    def list_files(self, commit_id: CommitId) -> Iterable[RepositoryFile]:
        cmd = ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", commit_id]
        files = []
        with RunGit(cmd) as git:
            for ci, line in git.iter_lines():
                files.append(GitRepositoryFile(self, Path(line.rstrip())))
            if git.errors():
                raise ValueError(git.errors())
        return files

    def read_file(self, commit_id: CommitId, file: RepositoryFile) -> str:
        cmd = ["git", "show", f"{commit_id}:{file.path}"]
        lines = []
        with RunGit(cmd) as git:
            for ci, line in git.iter_lines():
                lines.append(line.rstrip())
            if git.errors():
                raise ValueError(git.errors())
        return "\n".join(lines)


class CommitParser:
    def __init__(self, repo: Repository):
        self._repo = repo
        self._lines = []
        self._commit_id: CommitId | None = None

    def add_line(self, line: str):
        if not self._commit_id:
            self._commit_id = line[line.index(" ") + 1 :]
        else:
            self._lines.append(line)

    def is_complete(self) -> bool:
        return self._lines and self._lines[-1] == self._commit_id

    def build(self) -> Commit:
        return GitCommit(self._repo, self._commit_id, "\n".join(self._lines[:-1]))

    def __str__(self):
        return f"{self.is_complete()} :: {self._lines}"


class CommitsParser:
    def __init__(
        self, repo: GitRepository, accept: Callable[[int, CommitParser], bool]
    ):
        self._repo = repo
        self._accept = accept
        self._commit_index = 0
        self._builder = CommitParser(self._repo)

    def parse(self, lines: Iterable[Tuple[int, str]]):
        for ci, line in lines:
            self._builder.add_line(line.strip())
            if self._builder.is_complete():
                if self._accept(self._commit_index, self._builder):
                    yield self._builder.build()
                self._builder = CommitParser(self._repo)
                self._commit_index += 1
