# Documentation

| Path | Purpose |
| --- | --- |
| [adr/0001-python-not-go.md](adr/0001-python-not-go.md) | Why these tools are Python CLIs first |
| [adr/0002-ruamel-yaml.md](adr/0002-ruamel-yaml.md) | Why promotion uses `ruamel.yaml` round-trip |
| [adr/0003-multi-window-burn.md](adr/0003-multi-window-burn.md) | Why `slo-kit` emits multi-window burn pairs |
| [runbooks/promotion-bot.md](runbooks/promotion-bot.md) | Digests, promotion path, Trivy, `--open-pr` |
| [runbooks/slo-kit.md](runbooks/slo-kit.md) | Compile failures and error-budget math |
| [runbooks/platform-tenant.md](runbooks/platform-tenant.md) | Tenant name policy and render output |

## Exit codes

All three CLIs map `platform_ops.exceptions` types to stable exit codes (`src/platform_ops/exceptions.py`):

| Code | Meaning | Typical cause |
| --- | --- | --- |
| 0 | Success | Dry-run completed, or write/PR succeeded |
| 1 | General error | Unexpected `PlatformOpsError` base case |
| 2 | Validation | Bad flags, missing file, invalid YAML shape, invalid digest, `--require-signature` without `--image`, missing `--repo` / `PROMOTION_GITHUB_REPOSITORY` for `--open-pr` |
| 3 | Policy | Adjacent promotion refused, Trivy/cosign verify failed, reserved tenant name |
| 4 | Integration | Missing `cosign`, cosign verify timeout, missing `PROMOTION_GITHUB_TOKEN` for `--open-pr`, upstream API failure |

For `--open-pr` only: missing `--repo` / `PROMOTION_GITHUB_REPOSITORY` is exit **2** (validation), not 4.

Start with the root [README](../README.md) for install and try-it commands.
