from typing import Iterator, List, Optional, Tuple, Union

from difflib_parser import DifflibParser
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
        a_commit = self.__get_commit(a)
        b_commit = self.__get_commit(b)
        self.diff_index: DiffIndex[Diff] = a_commit.diff(b_commit)

    def __get_commit(self, commit: Union[Commit, GitAutograderCommit]) -> Commit:
        if isinstance(commit, Commit):
            return commit
        return commit.commit

    @staticmethod
    def get_file_diff(
        a: Union[Commit, GitAutograderCommit],
        b: Union[Commit, GitAutograderCommit],
        file_path: str,
    ) -> Optional[Tuple["GitAutograderDiff", Lit_change_type]]:
        """Returns file difference between two commits across ALL change types."""
        # Based on the expectation that there can only exist one change type per file in a diff
        diff_helper = GitAutograderDiffHelper(a, b)
        change_types: List[Lit_change_type] = ["A", "D", "R", "M", "T"]
        for change_type in change_types:
            for change in diff_helper.iter_changes(change_type):
                if change.diff_parser is None or change.edited_file_path != file_path:
                    continue
                return change, change_type
        return None

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
                DifflibParser(original_file.split("\n"), edited_file.split("\n"))
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
