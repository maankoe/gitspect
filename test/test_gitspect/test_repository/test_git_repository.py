import subprocess
import unittest
from pathlib import Path

from gitspect.respository import GitRepository, GitCommit
from gitspect.respository._git_file import GitRepositoryFile
from gitspect.respository._git_repository import (
    CommitParser,
    _commits_format,
)

repo_path = Path(__file__).parents[3]
repo = GitRepository(repo_path)
repo_commits = [
    GitCommit(repo, "15dfeb5c2949b9c77fb4264435a67ca4ac176c58", "fix import"),
    GitCommit(
        repo, "91d8fbb78b5b93dd60cd11306bc8af4023665c39", "add document name (filepath)"
    ),
    GitCommit(
        repo,
        "2f387e20c46d5b2da7ef8a76acfb5753ef839579",
        "move document classes to model package",
    ),
    GitCommit(
        repo,
        "61c803f2ae95c001c63fe4248fb1727f93570a00",
        "first go at segmenting py files",
    ),
    GitCommit(repo, "c8f7c6d2e7111a653ddac6d15a56772a473ed635", "initial commit"),
]


class TestGitRepository(unittest.TestCase):
    def test_error_on_not_a_repo(self):
        with self.assertRaises(ValueError):
            GitRepository(Path("/"))

    def test_get_first_commit(self):
        self.assertEqual(
            list(repo.commits(end=1, reverse=True)),
            repo_commits[-1:],
        )

    def test_get_last_commit(self):
        last_commit_log = subprocess.run(
            ["git", "rev-list", "--all", "-1", f"--format={_commits_format}"],
            capture_output=True,
        ).stdout.decode()
        builder = CommitParser(repo)
        for ci, line in enumerate(last_commit_log.splitlines()):
            builder.add_line(line)
        self.assertEqual(
            repo.commits(end=0),
            builder.build(),
        )

    def test_errors_on_negative_start(self):
        with self.assertRaises(ValueError):
            list(repo.commits(start=-1))

    def test_errors_on_end_smaller_than_start(self):
        with self.assertRaises(ValueError):
            list(repo.commits(start=2, end=1))

    def test_get_commits_by_index(self):
        self.assertEqual(list(repo.commits(1, 3, reverse=True)), repo_commits[-3:-1])

    def test_get_commits_by_commit(self):
        self.assertEqual(
            list(
                repo.commits_between(
                    repo_commits[4].commit_id, repo_commits[2].commit_id
                )
            ),
            repo_commits[2:4],
        )

    def test_not_a_commit(self):
        with self.assertRaises(ValueError):
            list(repo.commits_between("asdf", "qwer"))

    def test_commit_files(self):
        self.assertEqual(
            list(repo.list_diff_files("91d8fbb78b5b93dd60cd11306bc8af4023665c39")),
            [
                GitRepositoryFile(
                    repo,
                    Path("src/gitspect/model/_document.py"),
                    blob_id="b2ff4a32f3ef7d86f9572c93d3ec5a8988a0408b",
                ),
                GitRepositoryFile(
                    repo,
                    Path("src/gitspect/segmentation/python_segmentation.py"),
                    blob_id="500487ef83d2cbe9c4201504c7fa22256fd81a22",
                ),
                GitRepositoryFile(
                    repo,
                    Path(
                        "test/test_gitspect/test_segmentation/test_python_segmentation.py"
                    ),
                    blob_id="484dff4490094e2792f2e10b0bc0ed338b6cd8ae",
                ),
            ],
        )

    def test_read_blob(self):
        blob_id = "b2ff4a32f3ef7d86f9572c93d3ec5a8988a0408b"
        file_text = (
            subprocess.run(
                [
                    "git",
                    "cat-file",
                    "-p",
                    f"{blob_id}",
                ],
                capture_output=True,
            )
            .stdout.decode()
            .strip()
        )
        self.assertEqual(
            repo.read_blob(blob_id),
            file_text,
        )

    def test_read_blob_bad_blob_id(self):
        with self.assertRaises(ValueError):
            repo.read_blob("asdf")

    def test_commit_files_invalid_commit(self):
        with self.assertRaises(ValueError):
            list(repo.list_diff_files("asdf"))
