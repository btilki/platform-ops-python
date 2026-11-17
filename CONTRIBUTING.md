# Contributing

## Local loop

```bash
make sync
make validate
```

`make validate` is ruff check, ruff format --check, mypy --strict, and pytest (coverage gate 80%).

Optional: `pre-commit install` after `make sync` (Ruff, mypy, gitleaks). Hook revisions are in `.pre-commit-config.yaml`; keep the Ruff hook aligned with the pin in `pyproject.toml`.

## Rules

- Prefer tests that fail on policy mistakes (digest format, reserved namespaces, SLO objective = 1)
- Do not add `kubectl apply` or cloud provisioners
- Commit messages: short imperative summary that states why the change exists
- No secrets in fixtures
