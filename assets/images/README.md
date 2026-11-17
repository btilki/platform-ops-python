# Assets — diagrams

| File | What it shows |
| --- | --- |
| [platform-ops-python-cli-infographic.png](platform-ops-python-cli-infographic.png) | Three CLIs (`promotion-bot`, `slo-kit`, `platform-tenant`), GitOps reconcile flow, EKS·AKS·GKE siblings, safe-change footer |

## Infographic layout (2026-11, v3)

- **Header:** `platform-ops-python`, subtitle, pill **DevOps • SRE • Platform Engineering** and **dry-run by default**, author signature.
- **`promotion-bot`:** digest pin → GitHub PR → Argo CD reconciles; Trivy/cosign/`--open-pr` bullets as on the art.
- **`slo-kit`:** SLO YAML → compile `PrometheusRule` → error-budget report; no live Prometheus query.
- **`platform-tenant`:** Tenant YAML → five objects → Git → Argo CD reconciles; no `kubectl apply`.
- **Boutique strip:** EKS, AKS, GKE sibling repos (not this repository).
- **Footer:** `make validate` → build & scan → no critical issues → Promote digest in Git → Argo CD reconciles; **GitOps only**. Repo URL and **Argo CD is the reconciler**.

The root [README](../../README.md) has commands, flags, exit codes, and examples.

Referenced from the root README under **Portfolio overview**.