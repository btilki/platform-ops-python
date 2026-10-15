# ADR 0001 — Python, not Go

## Status

Accepted for this repository.

## Context

Platform teams often expect Kubernetes controllers in Go (`controller-runtime`). These tools are CI and GitOps glue: they validate inputs and emit YAML. Python fits that job.

## Decision

Ship three Python CLIs first. If a tenant **operator** is added later, use Kopf. Hot-path or upstream-quality controllers would be Go.

## Consequences

The CLIs talk to Git, Prometheus rules, and Kubernetes YAML. This repository does not claim a production Go operator.
