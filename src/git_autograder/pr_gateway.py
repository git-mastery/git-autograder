import json
import subprocess
from typing import Any, Dict

from git_autograder.exception import GitAutograderInvalidStateException


PR_GRAPHQL_QUERY = """
query ($owner: String!, $name: String!, $number: Int!) {
    repository(owner: $owner, name: $name) {
        pullRequest(number: $number) {
            number
            title
            body
            createdAt
            state
            author { login }
            baseRefName
            headRefName
            isDraft
            mergedAt
            mergedBy { login }
            commits(first: 50) {
                nodes {
                    commit { oid }
                }
            }
            latestReviews(first: 50) {
                nodes {
                    author { login }
                    state
                    body
                    submittedAt
                    createdAt
                }
            }
            comments(first: 50) {
                nodes {
                    author { login }
                    body
                    createdAt
                }
            }
        }
    }
}
"""


def fetch_pull_request_data(pr_number: int, pr_repo_full_name: str) -> Dict[str, Any]:
    repo_parts = pr_repo_full_name.split("/", 1)
    if len(repo_parts) != 2:
        raise GitAutograderInvalidStateException(
            f"Invalid repository full name: {pr_repo_full_name}"
        )

    owner, name = repo_parts
    command = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={PR_GRAPHQL_QUERY}",
        "-F",
        f"owner={owner}",
        "-F",
        f"name={name}",
        "-F",
        f"number={pr_number}",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise GitAutograderInvalidStateException(
            f"Timed out fetching PR #{pr_number} from {pr_repo_full_name}"
        )

    if result.returncode != 0:
        stderr = result.stderr.strip() or "Unknown gh error"
        raise GitAutograderInvalidStateException(
            f"Failed to load PR #{pr_number} from {pr_repo_full_name}: {stderr}"
        )

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise GitAutograderInvalidStateException(
            "Failed to parse pull request metadata returned by GitHub CLI."
        ) from error

    if not isinstance(payload, dict):
        raise GitAutograderInvalidStateException(
            "Unexpected pull request metadata shape returned by GitHub CLI."
        )

    data = payload.get("data", {}).get("repository", {}).get("pullRequest")
    if not isinstance(data, dict):
        raise GitAutograderInvalidStateException(
            "Unexpected pull request metadata shape returned by GitHub CLI."
        )

    return data
