# Assets — diagrams

| File | What it shows |
| --- | --- |
| [platform-ops-python-cli-infographic.png](platform-ops-python-cli-infographic.png) | Portfolio poster: Git PR → Argo CD, observability and multi-env pillars, EKS·AKS·GKE, safe-change footer |

## Infographic layout (2026-11, v2)

- **Header:** `platform-ops-python`, Python toolkit subtitle, pill **DevOps • SRE • Platform Engineering**, author signature.
- **Automation:** configs → GitHub PR → **Git PR → Argo CD** → platform changes via GitOps. Maps to **`promotion-bot`** (digest pin, `--open-pr`) and **`platform-tenant render`** (tenant YAML to Git).
- **Observability:** SLO-style monitor / analyze / improve motif. Maps to **`slo-kit compile`** (`PrometheusRule` YAML) and **`slo-kit report`** (error-budget band)—not live dashboards or Prometheus queries from this repo.
- **Multi-environment:** dev → staging → prod; logos **EKS**, **AKS**, **GKE** (Boutique sibling repos); adjacent promotion path in code (`dev → staging → prod`).
- **Footer (SAFE & RELIABLE):** run tests → build and scan → no critical issues → **Deploy** (end-to-end platform flow) → keep users happy. **Deploy here means merge GitOps and let Argo CD reconcile**—these CLIs do not deploy or `kubectl apply`.

**Outside these CLIs:** Argo CD API calls, `kubectl apply`, and cluster sync driven by Python.

The root [README](../../README.md) has commands, flags, exit codes, and examples.

Referenced from the root README under **Portfolio overview**.

**Art check:** If the Automation “Important” callout still reads **configuraations**, fix the spelling in your design file and re-export.