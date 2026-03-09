from typing import List, Optional

from git import Repo
from git.exc import GitCommandError

from git_autograder.commit import GitAutograderCommit
from git_autograder.exception import GitAutograderInvalidStateException
from git_autograder.tag import GitAutograderTag


class TagHelper:
    MISSING_TAG = "Tag {tag} is missing."
    MISSING_REMOTE = "Remote {remote} is missing."
    CANNOT_QUERY_REMOTE_TAGS = "Unable to query remote tags for '{remote}'."

    @staticmethod
    def _parse_remote_tag_names(raw: str) -> List[str]:
        names: List[str] = []
        seen = set()

        for line in raw.splitlines():
            parts = line.split()
            if len(parts) != 2:
                continue

            ref = parts[1]
            if not ref.startswith("refs/tags/"):
                continue

            name = ref[len("refs/tags/") :]
            if name.endswith("^{}"):
                name = name[:-3]

            if name not in seen:
                seen.add(name)
                names.append(name)

        return names

    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    def tag_or_none(self, tag_name: str) -> Optional[GitAutograderTag]:
        for tag_ref in self.repo.tags:
            if str(tag_ref) == tag_name:
                return GitAutograderTag(tag_ref)
        return None

    def tag(self, tag_name: str) -> GitAutograderTag:
        t = self.tag_or_none(tag_name)
        if t is None:
            raise GitAutograderInvalidStateException(
                self.MISSING_TAG.format(tag=tag_name)
            )
        return t

    def has_tag(self, tag_name: str) -> bool:
        return self.tag_or_none(tag_name) is not None

    def commit_or_none(self, tag_name: str) -> Optional[GitAutograderCommit]:
        t = self.tag_or_none(tag_name)
        if t is None:
            return None
        return t.commit

    def points_to(self, tag_name: str, commit: GitAutograderCommit) -> bool:
        tag_commit = self.commit_or_none(tag_name)
        return tag_commit is not None and tag_commit.hexsha == commit.hexsha

    def remote_tag_names_or_none(self, remote: str = "origin") -> Optional[List[str]]:
        if not any(r.name == remote for r in self.repo.remotes):
            return None

        try:
            raw = self.repo.git.ls_remote("--tags", remote)
        except GitCommandError:
            return None

        return self._parse_remote_tag_names(raw)

    def remote_tag_names(self, remote: str = "origin") -> List[str]:
        if not any(r.name == remote for r in self.repo.remotes):
            raise GitAutograderInvalidStateException(
                self.MISSING_REMOTE.format(remote=remote)
            )

        names = self.remote_tag_names_or_none(remote)
        if names is None:
            raise GitAutograderInvalidStateException(
                self.CANNOT_QUERY_REMOTE_TAGS.format(remote=remote)
            )
        return names
