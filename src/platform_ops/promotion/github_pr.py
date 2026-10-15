"""Open a GitHub PR that contains only the GitOps digest change."""

from __future__ import annotations

import base64
from typing import Protocol

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential_jitter

from platform_ops.exceptions import IntegrationError


class PullRequestOpener(Protocol):
    def open_pr(
        self,
        *,
        repo: str,
        path: str,
        content: str,
        branch: str,
        title: str,
        body: str,
        base: str = "main",
        commit_message: str,
    ) -> str: ...


class DryRunOpener:
    def open_pr(
        self,
        *,
        repo: str,
        path: str,
        content: str,
        branch: str,
        title: str,
        body: str,
        base: str = "main",
        commit_message: str,
    ) -> str:
        return f"dry-run://{repo}/pull/{branch}"


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TimeoutException | httpx.NetworkError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in {429, 500, 502, 503, 504}
    return False


class GitHubOpener:
    def __init__(
        self,
        token: str,
        api_url: str = "https://api.github.com",
        timeout_s: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not token:
            raise IntegrationError("PROMOTION_GITHUB_TOKEN is required for --open-pr")
        self._client = client or httpx.Client(
            base_url=api_url.rstrip("/"),
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=timeout_s,
        )

    def close(self) -> None:
        self._client.close()

    def open_pr(
        self,
        *,
        repo: str,
        path: str,
        content: str,
        branch: str,
        title: str,
        body: str,
        base: str = "main",
        commit_message: str,
    ) -> str:
        owner_repo = repo.strip("/")
        sha = self._git_sha(owner_repo, f"heads/{base}")
        self._create_ref(owner_repo, branch, sha)
        file_sha = self._file_sha(owner_repo, path, branch=base)
        self._put_file(owner_repo, path, content, branch, commit_message, file_sha)
        pr = self._create_pull(owner_repo, title, body, branch, base)
        html_url = pr.get("html_url")
        if not isinstance(html_url, str):
            raise IntegrationError("GitHub pull request response missing html_url")
        return html_url

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential_jitter(initial=0.5, max=8),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def _request(self, method: str, url: str, **kwargs: object) -> httpx.Response:
        response = self._client.request(method, url, **kwargs)  # type: ignore[arg-type]
        if response.status_code in {429, 500, 502, 503, 504}:
            response.raise_for_status()
        if response.is_error:
            raise IntegrationError(f"GitHub {method} {url} failed: {response.status_code} {response.text}")
        return response

    def _git_sha(self, repo: str, ref: str) -> str:
        payload = self._request("GET", f"/repos/{repo}/git/ref/{ref}").json()
        sha = payload.get("object", {}).get("sha")
        if not isinstance(sha, str):
            raise IntegrationError(f"could not resolve ref {ref} in {repo}")
        return sha

    def _create_ref(self, repo: str, branch: str, sha: str) -> None:
        self._request(
            "POST",
            f"/repos/{repo}/git/refs",
            json={"ref": f"refs/heads/{branch}", "sha": sha},
        )

    def _file_sha(self, repo: str, path: str, branch: str) -> str:
        payload = self._request("GET", f"/repos/{repo}/contents/{path}", params={"ref": branch}).json()
        sha = payload.get("sha")
        if not isinstance(sha, str):
            raise IntegrationError(f"could not read {path} on {branch}")
        return sha

    def _put_file(self, repo: str, path: str, content: str, branch: str, message: str, sha: str) -> None:
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        self._request(
            "PUT",
            f"/repos/{repo}/contents/{path}",
            json={"message": message, "content": encoded, "branch": branch, "sha": sha},
        )

    def _create_pull(self, repo: str, title: str, body: str, head: str, base: str) -> dict[str, object]:
        payload = self._request(
            "POST",
            f"/repos/{repo}/pulls",
            json={"title": title, "body": body, "head": head, "base": base},
        ).json()
        if not isinstance(payload, dict):
            raise IntegrationError("GitHub pull request response was not an object")
        return payload
