# Changelog

## Unreleased

- Document Docker build/run examples and GitHub Actions CI in the README
- Add `assets/images/README.md` diagram catalog
- Add README badges, exit-code table in `docs/README.md`, cosign prerequisites

## 0.2.0 — 2026-11-17

- Remove the deleted playbook link; keep EKS, AKS, and GKE references
- Align promotion token docs with `PROMOTION_GITHUB_TOKEN` / `PROMOTION_GITHUB_REPOSITORY` / `PROMOTION_GITHUB_API_URL`
- Fix slo-kit remaining-budget formula in the runbook
- Align error-budget band wording with `_band()` (≥50% normal)
- Document that tenant `sourcePath` is accepted but not rendered into `AppProject`
- Document promotion env vars in the README
- Soften cross-repo wording so this repo describes complementary CLIs, not live platform wiring
- Pin CI lint to Ruff 0.16.9
- Clarify default four burn-window pairs; document Dockerfile entrypoint and pre-commit
- Sync pre-commit Ruff hook to v0.16.9; add Trivy blocked-example command
- Normalize ADR status wording; name the README summary-table columns
- Rename `platform-tenant apply` to `render`
- Add `docs/README.md` index; soften package description wording
- Add CLI infographic to the root README

## 0.1.0 — 2026-09-13

- Initial scaffold: `promotion-bot`, `slo-kit`, `platform-tenant`
- Dry-run defaults, tests, and GitHub Actions CI