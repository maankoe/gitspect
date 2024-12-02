import unittest

from gitspect.respository._diff import parse_diff

raw_diff = """
diff --git a/src/gitspect/respository/_abc.py b/src/gitspect/respository/_abc.py
index 9f68b00..748a08a 100644
--- a/src/gitspect/respository/_abc.py
+++ b/src/gitspect/respository/_abc.py
@@ -38,8 +38,14 @@ class Repository(ABC):
     ) -> Iterable[Commit]:
         pass

+    @abstractmethod
     def commits_between(self, start: str, end: str = None) -> Iterable[Commit]:
         pass

-    def files(self, commit_id: CommitId) -> Iterable[RepositoryFile]:
+    @abstractmethod
+    def list_files(self, commit_id: CommitId) -> Iterable[RepositoryFile]:
+        pass
+
+    @abstractmethod
+    def read_file(self, commit_id: CommitId, file: RepositoryFile) -> str:
         pass
diff --git a/src/gitspect/respository/_git_repository.py b/src/gitspect/respository/_git_repository.py
index e78baae..6556f7f 100644
--- a/src/gitspect/respository/_git_repository.py
+++ b/src/gitspect/respository/_git_repository.py
@@ -59,7 +59,7 @@ class GitRepository(Repository):
                 raise ValueError(git.errors())
         return files

-    def read_file(self, commit_id: CommitId, file: GitRepositoryFile) -> str:
+    def read_file(self, commit_id: CommitId, file: RepositoryFile) -> str:
         cmd = ["git", "show", f"{commit_id}:{file.path}"]
         lines = []
         with RunGit(cmd) as git:
(END)"""


class TestDiffParser(unittest.TestCase):
    def test_something(self):
        parse_diff(raw_diff)
