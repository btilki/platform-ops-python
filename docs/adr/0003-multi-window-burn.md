# ADR 0003 — Multi-window burn rates

## Status

Accepted.

## Context

[boutique-gke-sre](https://github.com/btilki/boutique-gke-sre) documents 14.4×/1h, 6×/6h, 3×/1d, 1×/3d burns. Hand-written rules drift.

## Decision

`slo-kit` emits paired short/long windows from the SRE workbook (5m+1h, 30m+6h, 2h+1d, 6h+3d) with those multipliers. Error-budget bands follow the Boutique policy thresholds as implemented: ≥50% normal, 25%–under 50% cautious, under 25% freeze, 0% SEV2.

## Consequences

Generated `PrometheusRule` objects target a Prometheus-backed path. Boutique GKE documents the same burn and budget policy with Cloud Monitoring YAML as the reference alert definitions.
