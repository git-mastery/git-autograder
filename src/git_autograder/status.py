from enum import StrEnum


class GitAutograderStatus(StrEnum):
    SUCCESSFUL = "SUCCESSFUL"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    ERROR = "ERROR"
