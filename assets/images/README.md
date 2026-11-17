# Assets — diagrams

| File | What it shows |
| --- | --- |
| [platform-ops-python-cli-infographic.png](platform-ops-python-cli-infographic.png) | Portfolio overview: three pillars (automation / observability / multi-environment), EKS·AKS·GKE links, safe-change pipeline footer |

## Infographic layout (2026-11)

- **Header:** `platform-ops-python` — “Python toolkit for platform operations, monitoring and automation”; pill **DevOps • SRE • Platform Engineering**; author signature.
- **Automation:** config read → update → GitHub PR → cluster sync motif; bullets on digest updates, SLO-related automation, multi-environment support.
- **Observability:** SLO track → alert → analyze → improve; Prometheus-oriented bullets.
- **Multi-environment:** dev → staging → production → cloud (K8s); **EKS**, **AKS**, **GKE** logos.
- **Footer pipeline:** run tests → build and scan → no critical issues → deploy → keep users happy.
- **Repo link:** `github.com/btilki/platform-ops-python`.

The root [README](../../README.md) is the source of truth for behaviour: three CLIs (`promotion-bot`, `slo-kit`, `platform-tenant`), dry-run by default, **no** `kubectl apply` and **no** deploy from these tools. Argo CD reconciles after Git changes.

Package maturity is **Alpha** (`pyproject.toml`, README badge). The infographic is positioning copy, not a maturity label.

Referenced from the root README under **Repository map and navigation**.