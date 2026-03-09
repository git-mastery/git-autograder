import os
from contextlib import contextmanager
from typing import Iterator, List, Optional, TextIO, Union

from git import Repo


class FileHelper:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    @contextmanager
    def file_or_none(
        self, path: Union[str, os.PathLike[str]]
    ) -> Iterator[Optional[TextIO]]:
        file_path = os.path.join(self.repo.working_dir, path)
        if not os.path.isfile(file_path):
            yield None
        else:
            with open(file_path, "r") as file:
                yield file

    @contextmanager
    def file(self, path: Union[str, os.PathLike[str]]) -> Iterator[TextIO]:
        file_path = os.path.join(self.repo.working_dir, path)
        with open(file_path, "r") as file:
            yield file

    def untracked_files(self) -> List[str]:
        return self.repo.untracked_files
    
    def content_equal(self, path: Union[str, os.PathLike[str]], expected: str):
        with self.file_or_none(path) as input_file:
            if input_file is None:
                return False
            contents = [
                line.strip() for line in input_file.readlines() if line.strip() != ""
            ]
            if contents != expected:
                return False

            return True

