from dataclasses import dataclass


@dataclass
class GitAutograderReflogEntry:
    sha: str
    index: int
    action: str
    message: str
