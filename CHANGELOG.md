# Changelog

## Unreleased

- Portfolio infographic v2 (Git PR → Argo CD, SAFE & RELIABLE footer); refresh `assets/images/README.md`
- Rename README section to **Portfolio overview**; map infographic pillars to real CLIs in `assets/images/README.md`
- Replace CLI infographic art; document accurate capabilities vs poster copy
- Link boutique-gke-sre `manifest-digest-pr` workflow; document `--path-in-repo` and promotion exit codes
- README summary table includes LimitRange; `make validate` documents Ruff format check
- ADR 0003 band label `sev2`; promotion runbook env vars; CONTRIBUTING gitleaks note

## 0.2.0 — 2026-11-17

- Remove the deleted playbook link; keep EKS, AKS, and GKE references
- Align promotion token docs with `PROMOTION_GITHUB_TOKEN` / `PROMOTION_GITHUB_REPOSITORY` / `PROMOTION_GITHUB_API_URL`
- Fix slo-kit remaining-budget formula in the runbook
- Align error-budget band wording with `_band()` (≥50% normal); note GKE policy uses >50% at exactly 50%
- Document that tenant `sourcePath` is accepted but not rendered into `AppProject`
- Document promotion env vars in the README
- Soften cross-repo wording so this repo describes complementary CLIs, not live platform wiring
- Pin CI lint to Ruff 0.16.9; sync pre-commit Ruff hook to v0.16.9
- Clarify default four burn-window pairs; document Dockerfile entrypoint and pre-commit
- Add Trivy blocked-example command
- Normalize ADR status wording; name the README summary-table columns
- Rename `platform-tenant apply` to `render`
- Add `docs/README.md` index with exit-code table; soften package description wording
- Add CLI infographic and `assets/images/README.md` diagram catalog
- Document Docker build/run examples, GitHub Actions CI, README badges, and cosign prerequisites

## 0.1.0 — 2026-09-13

- Initial scaffold: `promotion-bot`, `slo-kit`, `platform-tenant`
- Dry-run defaults, tests, and GitHub Actions CI