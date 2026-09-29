# Runbook — slo-kit

## Symptom

Compile fails or budget band looks wrong.

## Checks

1. `objective` in `(0, 1)` — `1.0` is rejected (zero error budget).
2. `sli.good` / `sli.total` must be instant-vector selectors; the compiler wraps `rate()[window]`.
3. `report`: remaining % uses `(1 - sli) / (1 - objective)`.

## Rollback

Keep the previously generated `PrometheusRule` in Git. Do not edit recording rules by hand if `slo-kit` owns them.
