from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from platform_ops.exceptions import PolicyError, ValidationError
from platform_ops.tenant.cli import app, load_tenant
from platform_ops.tenant.models import assert_not_reserved
from platform_ops.tenant.render import render_tenant

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "tenant" / "payments.yaml"
RUNNER = CliRunner()


def test_render_contains_controls() -> None:
    tenant = load_tenant(EXAMPLE)
    text = render_tenant(tenant)
    assert "kind: Namespace" in text
    assert "kind: ResourceQuota" in text
    assert "kind: LimitRange" in text
    assert "kind: NetworkPolicy" in text
    assert "kind: AppProject" in text
    assert "default-deny" in text
    assert "payments" in text
    assert "checkout" in text


def test_reserved_names() -> None:
    with pytest.raises(PolicyError):
        assert_not_reserved("kube-system")
    with pytest.raises(PolicyError):
        assert_not_reserved("argocd")


def test_cli_dry_run(tmp_path: Path) -> None:
    result = RUNNER.invoke(app, ["apply", "--config", str(EXAMPLE), "--out", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "kind: Namespace" in result.output
    assert list(tmp_path.iterdir()) == []


def test_cli_write(tmp_path: Path) -> None:
    result = RUNNER.invoke(
        app,
        ["apply", "--config", str(EXAMPLE), "--out", str(tmp_path), "--write"],
    )
    assert result.exit_code == 0, result.output
    written = tmp_path / "tenant.yaml"
    assert written.is_file()
    assert "AppProject" in written.read_text(encoding="utf-8")


def test_cli_rejects_reserved(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(
        EXAMPLE.read_text(encoding="utf-8").replace("name: payments", "name: kube-system"),
        encoding="utf-8",
    )
    result = RUNNER.invoke(app, ["apply", "--config", str(path)])
    assert result.exit_code == 3
    assert "reserved" in result.output.lower()


def test_invalid_name(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(
        EXAMPLE.read_text(encoding="utf-8").replace("name: payments", "name: Payments"),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_tenant(path)
