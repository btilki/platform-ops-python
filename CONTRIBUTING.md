# Contributing

## Local loop

```bash
make sync
make validate
```

`make validate` is ruff + mypy --strict + pytest (coverage gate 80%).

## Rules

- Prefer tests that fail on policy mistakes (digest format, reserved namespaces, SLO objective = 1)
- Do not add `kubectl apply` or cloud provisioners
- Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`)
- No secrets in fixtures
