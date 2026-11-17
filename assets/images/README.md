# Assets — diagrams

| File | What it shows |
| --- | --- |
| [platform-ops-python-cli-infographic.png](platform-ops-python-cli-infographic.png) | Portfolio poster: automation / observability / multi-environment pillars and EKS·AKS·GKE links |

## Infographic layout (2026-11)

- **Header:** `platform-ops-python` — “Python toolkit for platform operations, monitoring and automation”; pill **DevOps • SRE • Platform Engineering**; author signature.
- **Automation column:** GitOps-style flow (config → PR → reconcile). **In this repo:** `promotion-bot` (digest pin, optional `--open-pr`), `platform-tenant render` (tenant YAML).
- **Observability column:** SLO and alerting motif. **In this repo:** `slo-kit compile` (PrometheusRule YAML), `slo-kit report` (error-budget band). No dashboards or live Prometheus queries.
- **Multi-environment column:** dev → staging → prod and **EKS**, **AKS**, **GKE** (Boutique sibling repos).
- **Footer pipeline:** tests → build and scan → no critical issues → merge Git → Argo CD reconciles. **Not** `kubectl apply` from these CLIs.

**Not implemented in this repository:** cluster sync from the CLIs, runtime dashboards, package assignment managers, or deploy actions initiated by these commands.

The root [README](../../README.md) is the source of truth: three CLIs (`promotion-bot`, `slo-kit`, `platform-tenant`), dry-run by default, **no** `kubectl apply`. Package maturity is **Alpha** (`pyproject.toml`, README badge).

Referenced from the root README under **Portfolio overview**.