# Runbook — promotion-bot

## Symptom

Promotion refused or PR not opened.

## Checks

1. Digest shape: must be `sha256:` + 64 hex. `:latest` is always an error.
2. Path: only `dev→staging` or `staging→prod`.
3. Trivy JSON: fixable HIGH/CRITICAL block the run. Allow-list is in `ScanPolicy.allow` (empty by default; the CLI does not expose a flag for it yet). Reproduce a block with `--trivy-json examples/gitops/trivy-blocked.json`.
4. `--require-signature`: `cosign` on `PATH`, `--image` repository, verify target `image@digest`. Missing `--image` → exit 2; verify failure → exit 3; missing `cosign` or verify timeout → exit 4.
5. `--open-pr`: `PROMOTION_GITHUB_TOKEN` and `--repo owner/name`.
6. YAML: `images.<service>.digest` must exist (Boutique Helm layout).

## Rollback

Revert the GitOps PR. Argo CD is still the only deployer. Do not `kubectl set image`.
