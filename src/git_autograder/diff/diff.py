from dataclasses import dataclass
from typing import Optional

from difflib_parser import DiffCode, DifflibParser
from git.diff import Diff, Lit_change_type


@dataclass
class GitAutograderDiff:
    diff: Diff
    change_type: Lit_change_type
    original_file_path: Optional[str]
    edited_file_path: Optional[str]
    original_file: Optional[str]
    edited_file: Optional[str]
    diff_parser: Optional[DifflibParser]

    def has_deleted_line(self) -> bool:
        if self.diff_parser is None:
            return False

        for diff in self.diff_parser.iter_diffs():
            if diff.code == DiffCode.LEFT_ONLY and diff.line.strip() != "":
                return True

        return False

    def has_added_line(self) -> bool:
        if self.diff_parser is None:
            return False

        for diff in self.diff_parser.iter_diffs():
            if diff.code == DiffCode.RIGHT_ONLY and diff.line.strip() != "":
                return True

        return False

    def has_edited_line(self) -> bool:
        if self.diff_parser is None:
            return False

        for diff in self.diff_parser.iter_diffs():
            if diff.code == DiffCode.CHANGED and diff.line.strip() != "":
                return True

        return False
