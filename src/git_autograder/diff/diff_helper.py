from typing import Iterator, Union

from difflib_parser.difflib_parser import DiffParser
from git import Commit, Diff, DiffIndex
from git.diff import Lit_change_type

from git_autograder.commit import GitAutograderCommit
from git_autograder.diff.diff import GitAutograderDiff


class GitAutograderDiffHelper:
    def __init__(
        self,
        a: Union[Commit, GitAutograderCommit],
        b: Union[Commit, GitAutograderCommit],
    ) -> None:
        a_commit = a if isinstance(a, Commit) else a.commit
        b_commit = b if isinstance(b, Commit) else b.commit
        self.diff_index: DiffIndex[Diff] = a_commit.diff(b_commit)

    def iter_changes(self, change_type: Lit_change_type) -> Iterator[GitAutograderDiff]:
        for change in self.diff_index.iter_change_type(change_type):
            original_file_rawpath = change.a_rawpath
            edited_file_rawpath = change.b_rawpath
            original_file_path = (
                original_file_rawpath.decode("utf-8")
                if original_file_rawpath is not None
                else None
            )
            edited_file_path = (
                edited_file_rawpath.decode("utf-8")
                if edited_file_rawpath is not None
                else None
            )
            original_file_blob = change.a_blob
            edited_file_blob = change.b_blob
            original_file = (
                original_file_blob.data_stream.read().decode("utf-8")
                if original_file_blob is not None
                else None
            )
            edited_file = (
                edited_file_blob.data_stream.read().decode("utf-8")
                if edited_file_blob is not None
                else None
            )

            diff_parser = (
                DiffParser(original_file.split("\n"), edited_file.split("\n"))
                if original_file is not None and edited_file is not None
                else None
            )

            yield GitAutograderDiff(
                change_type=change_type,
                diff=change,
                original_file_path=original_file_path,
                edited_file_path=edited_file_path,
                original_file=original_file,
                edited_file=edited_file,
                diff_parser=diff_parser,
            )
