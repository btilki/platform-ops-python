# Contributing

## Local loop

```bash
make sync
make validate
```

`make validate` is ruff + mypy --strict + pytest (coverage gate 80%).

Optional: `pre-commit install` after `make sync`. Hook revisions are in `.pre-commit-config.yaml` and should stay aligned with the Ruff pin in `pyproject.toml`.

## Rules

- Prefer tests that fail on policy mistakes (digest format, reserved namespaces, SLO objective = 1)
- Do not add `kubectl apply` or cloud provisioners
- Commit messages: short imperative summary that states why the change exists
- No secrets in fixtures
