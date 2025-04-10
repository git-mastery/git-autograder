from dataclasses import dataclass
from typing import Optional

from difflib_parser.difflib_parser import DiffParser
from git.diff import Diff, Lit_change_type


@dataclass
class GitAutograderDiff:
    diff: Diff
    change_type: Lit_change_type
    original_file_path: Optional[str]
    edited_file_path: Optional[str]
    original_file: Optional[str]
    edited_file: Optional[str]
    diff_parser: Optional[DiffParser]
