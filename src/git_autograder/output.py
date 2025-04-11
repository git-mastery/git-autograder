import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import ClassVar, List, Optional

from git_autograder.encoder import Encoder
from git_autograder.status import GitAutograderStatus


@dataclass
class GitAutograderOutput:
    status: GitAutograderStatus

    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    is_local: Optional[bool]
    comments: Optional[List[str]] = None
    exercise_name: Optional[str] = None

    OUTPUT_FILE_NAME: ClassVar[str] = "output.json"

    def save(self, path: str = "../output") -> None:
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, self.OUTPUT_FILE_NAME)
        output = asdict(self)
        with open(file_path, "w") as f:
            f.write(json.dumps(output, cls=Encoder))
