from datetime import datetime, timezone
from typing import Any, List

from git import Repo
from git_autograder.commit import GitAutograderCommit
from git_autograder.pr_comment import GitAutograderPrComment
from git_autograder.pr_review import GitAutograderPrReview


def extract_commit_shas(commits: List[Any]) -> List[str]:
    commit_shas: List[str] = []
    for commit in commits:
        if not isinstance(commit, dict):
            continue

        sha = commit.get("oid")
        if not isinstance(sha, str):
            commit_node = commit.get("commit")
            if isinstance(commit_node, dict):
                nested_sha = commit_node.get("oid")
                if isinstance(nested_sha, str):
                    sha = nested_sha

        if isinstance(sha, str):
            commit_shas.append(sha)

    return commit_shas


def build_commits(commits: List[Any], repo: Repo) -> List[GitAutograderCommit]:
    commit_shas = extract_commit_shas(commits)
    git_commits = [repo.commit(sha) for sha in commit_shas]
    git_commits.sort(key=lambda commit: commit.committed_datetime)
    return [GitAutograderCommit(commit) for commit in git_commits]


def build_reviews(latest_reviews: List[Any]) -> List[GitAutograderPrReview]:
    sorted_reviews = sorted(
        [review for review in latest_reviews if isinstance(review, dict)],
        key=lambda review: _parse_iso_or_min(
            review.get("submittedAt") or review.get("createdAt")
        ),
    )

    return [
        GitAutograderPrReview(
            author_login=review.get("author", {}).get("login")
            if isinstance(review, dict)
            else None,
            state=review.get("state") if isinstance(review, dict) else None,
            body=review.get("body") if isinstance(review, dict) else None,
        )
        for review in sorted_reviews
    ]


def build_comments(comments: List[Any]) -> List[GitAutograderPrComment]:
    sorted_comments = sorted(
        [comment for comment in comments if isinstance(comment, dict)],
        key=lambda comment: _parse_iso_or_min(comment.get("createdAt")),
    )

    return [
        GitAutograderPrComment(
            comment.get("author", {}).get("login") if isinstance(comment, dict) else None,
            comment.get("body") if isinstance(comment, dict) else None,
        )
        for comment in sorted_comments
    ]


def _parse_iso_or_min(value: Any) -> datetime:
    if not isinstance(value, str):
        return datetime.min.replace(tzinfo=timezone.utc)

    try:
        iso_value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso_value)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
