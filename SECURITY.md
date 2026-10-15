# Security

## Reporting vulnerabilities

If you discover a security issue, please report it responsibly. Do not open public issues for exploitable vulnerabilities.

**Contact:** Open a private security advisory on GitHub or email btilki@gmail.com.

## Design principles

- **Dry-run by default** — `--write` and `--open-pr` are explicit
- **No cluster apply** — Git is the deploy authority; Argo CD reconciles
- **No secrets in Git** — tokens only via environment (`PROMOTION_GITHUB_TOKEN`)
- **Digest-only images** — `:latest` is a validation error
- **Least surprise YAML** — `ruamel.yaml` round-trip so GitOps diffs stay reviewable

## Tokens

`promotion-bot --open-pr` needs a GitHub token or GitHub App installation token with `contents:write` and `pull_requests:write` on the GitOps repository. Prefer a GitHub App over a PAT.
