# ADR 0001 — Python, not Go

## Status

Accepted for this repository.

## Context

Platform teams often expect Kubernetes controllers in Go (`controller-runtime`). This candidate's public work is Terraform/GitOps, and Python is the language already used for CI glue.

## Decision

Ship three Python CLIs first. If a tenant **operator** is added later, use Kopf and state in the README: hot-path or upstream-quality controllers would be Go.

## Consequences

Hiring managers can read real Python that talks to Git, Prometheus rules, and Kubernetes YAML. We do not claim a production Go operator.
