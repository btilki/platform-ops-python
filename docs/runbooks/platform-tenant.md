# Runbook — platform-tenant

## Symptom

Apply exits non-zero or rendered YAML is rejected by policy.

## Checks

1. `metadata.name` is a DNS-1123 label.
2. Reserved names (`kube-system`, `argocd`, …) exit 3.
3. Output is files only. A human or GitOps PR applies them.

## Rollback

Delete the tenant YAML from Git and let Argo CD prune, or `kubectl delete namespace <name>` after confirming the AppProject is gone.
