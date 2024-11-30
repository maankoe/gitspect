from collections.abc import Iterable, Sequence
from pathlib import Path

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

    def read_file(self, commit_id: CommitId, file: GitRepositoryFile) -> str:
        cmd = ["git", "show", f"{commit_id}:{file.path}"]
        lines = []
        with RunGit(cmd) as git:
            for ci, line in git.iter_lines():
                lines.append(line.rstrip())
            if git.errors():
                raise ValueError(git.errors())
        return "\n".join(lines)


def _commit_from_oneline(repo: "GitRepository", line: str) -> Commit:
    hash_end = line.index(" ")
    return GitCommit(repo, commit_id=line[:hash_end], message=" ".join(line[hash_end:]))
