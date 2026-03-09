from typing import Any, Optional

from git.refs.tag import TagReference

from git_autograder.commit import GitAutograderCommit


class GitAutograderTag:
    def __init__(self, tag_ref: TagReference) -> None:
        self.tag_ref = tag_ref

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, GitAutograderTag) and value.tag_ref == self.tag_ref

    @property
    def name(self) -> str:
        return str(self.tag_ref)

    @property
    def commit(self) -> GitAutograderCommit:
        return GitAutograderCommit(self.tag_ref.commit)

    @property
    def is_annotated(self) -> bool:
        return self.tag_ref.tag is not None

    @property
    def is_lightweight(self) -> bool:
        return self.tag_ref.tag is None

    def message_or_none(
        self, *, strip: bool = True, lower: bool = False
    ) -> Optional[str]:
        if self.tag_ref.tag is None:
            return None

        message = self.tag_ref.tag.message
        if strip:
            message = message.strip()
        if lower:
            message = message.lower()
        return message
