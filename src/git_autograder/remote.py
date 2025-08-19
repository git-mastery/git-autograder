from typing import Any, List
from urllib.parse import urlparse

from git import Remote


class GitAutograderRemote:
    def __init__(self, remote: Remote) -> None:
        self.remote = remote

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, GitAutograderRemote):
            return False
        return value.remote == self.remote

    def track_branches(self, branches: List[str]) -> None:
        # We start with filtering main because it should be the default branch that
        # exists even on local machines.
        tracked = {"main"}
        for remote in self.remote.refs:
            for b in branches:
                if b not in tracked or f"{self.remote.name}/{b}" != remote.name:
                    continue
                tracked.add(b)
                self.remote.repo.git.checkout("-b", b, f"{self.remote.name}/{b}")
                break

    def is_for_repo(self, owner: str, repo_name: str) -> bool:
        remote_url = self.remote.url
        if remote_url.startswith("https://github.com"):
            # https://github.com/<owner>/<repo>.git
            parsed = urlparse(remote_url)
            path_parts = parsed.path.strip("/").split("/")
        elif remote_url.startswith("git@github.com"):
            # git@github.com:<owner>/<repo>.git
            components = remote_url.split(":")
            if len(components) != 2:
                return False
            path_parts = components[1].split("/")
        else:
            return False

        owner_part = path_parts[0]
        repo_part = path_parts[1]
        if repo_part.endswith(".git"):
            repo_part = repo_part[:-4]

        return owner_part == owner and repo_part == repo_name
