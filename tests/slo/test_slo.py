from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from platform_ops.exceptions import ValidationError
from platform_ops.slo.budget import remaining_budget
from platform_ops.slo.cli import app
from platform_ops.slo.compile import compile_rules, load_spec

SPEC = Path(__file__).resolve().parents[2] / "examples" / "slo" / "boutique.yaml"
RUNNER = CliRunner()


def test_remaining_budget_bands() -> None:
    normal = remaining_budget(sli=0.9996, objective=0.999)
    assert normal.band == "normal"
    assert normal.remaining > 0.5

    freeze = remaining_budget(sli=0.9991, objective=0.999)
    assert freeze.band == "freeze"

    sev2 = remaining_budget(sli=0.99, objective=0.999)
    assert sev2.band == "sev2"
    assert sev2.remaining == 0


def test_invalid_objective() -> None:
    with pytest.raises(ValidationError):
        remaining_budget(0.99, 1.0)


def test_compile_contains_multi_window_burns() -> None:
    document = load_spec(SPEC)
    rendered = compile_rules(document)
    assert "kind: PrometheusRule" in rendered
    assert "browse-availability" in rendered
    assert "checkout-availability" in rendered
    assert "14.4" in rendered
    assert "and" in rendered
    assert "app.kubernetes.io/managed-by: slo-kit" in rendered


def test_compile_rejects_objective_one(tmp_path: Path) -> None:
    spec = tmp_path / "bad.yaml"
    spec.write_text(
        """
slos:
  - name: too-perfect
    service: demo
    objective: 1.0
    sli:
      good: metric_good
      total: metric_total
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_spec(spec)


def test_cli_report() -> None:
    result = RUNNER.invoke(app, ["report", "--sli", "0.9992", "--objective", "0.999"])
    assert result.exit_code == 0, result.output
    assert "band:" in result.output


def test_cli_compile_stdout() -> None:
    result = RUNNER.invoke(app, ["compile", "--spec", str(SPEC), "--stdout"])
    assert result.exit_code == 0, result.output
    assert "PrometheusRule" in result.output
