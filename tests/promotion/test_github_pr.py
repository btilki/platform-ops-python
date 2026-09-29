from __future__ import annotations

import httpx
import respx

from platform_ops.promotion.github_pr import GitHubOpener


@respx.mock
def test_open_pr_happy_path() -> None:
    api = "https://api.github.com"
    respx.get(f"{api}/repos/acme/gitops/git/ref/heads/main").mock(
        return_value=httpx.Response(200, json={"object": {"sha": "aaa111"}})
    )
    respx.post(f"{api}/repos/acme/gitops/git/refs").mock(return_value=httpx.Response(201, json={}))
    respx.get(f"{api}/repos/acme/gitops/contents/gitops/values.yaml").mock(
        return_value=httpx.Response(200, json={"sha": "file-sha"})
    )
    respx.put(f"{api}/repos/acme/gitops/contents/gitops/values.yaml").mock(return_value=httpx.Response(200, json={}))
    respx.post(f"{api}/repos/acme/gitops/pulls").mock(
        return_value=httpx.Response(201, json={"html_url": "https://github.com/acme/gitops/pull/42"})
    )

    opener = GitHubOpener(token="test-token")
    url = opener.open_pr(
        repo="acme/gitops",
        path="gitops/values.yaml",
        content="images: {}\n",
        branch="ci/digest-frontend",
        title="ci: promote frontend",
        body="body",
        commit_message="ci: pin frontend",
    )
    opener.close()
    assert url.endswith("/pull/42")
