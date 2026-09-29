# ADR 0002 — ruamel.yaml for GitOps mutation

## Status

Accepted.

## Context

`PyYAML` dumps lose comments and reorder keys. GitOps reviewers reject PRs that reformat an entire `values-images.yaml`.

## Decision

Load and dump promotion targets with `ruamel.yaml` round-trip (`typ="rt"`).

## Consequences

Slightly heavier dependency. Diffs stay scoped to the digest field, matching Boutique Helm values.
