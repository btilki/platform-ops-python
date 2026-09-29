from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from platform_ops.exceptions import PolicyError, ValidationError
from platform_ops.promotion.cli import app
from platform_ops.promotion.digest import assert_not_latest, normalize_digest
from platform_ops.promotion.manifests import load_manifest, render_manifest, update_service_digest
from platform_ops.promotion.policy import assert_adjacent_promotion
from platform_ops.promotion.scan import ScanPolicy, assert_scan_clean, findings_from_trivy

FIXTURE = Path(__file__).resolve().parents[2] / "examples" / "gitops" / "values-images.yaml"
RUNNER = CliRunner()


def test_normalize_digest_accepts_sha256() -> None:
    digest = "sha256:" + ("a" * 64)
    assert normalize_digest("@" + digest.upper()) == digest


def test_normalize_digest_rejects_tag() -> None:
    with pytest.raises(ValidationError):
        normalize_digest("latest")


def test_assert_not_latest() -> None:
    with pytest.raises(ValidationError):
        assert_not_latest("gcr.io/demo/frontend:latest")


def test_adjacent_promotion() -> None:
    assert_adjacent_promotion("staging", "prod")
    with pytest.raises(PolicyError):
        assert_adjacent_promotion("dev", "prod")


def test_update_preserves_comment(tmp_path: Path) -> None:
    path = tmp_path / "values.yaml"
    path.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    data = load_manifest(path)
    new = "sha256:" + ("b" * 64)
    previous = update_service_digest(data, "frontend", new)
    text = render_manifest(data)
    assert previous.startswith("sha256:")
    assert new in text
    assert "No floating tags" in text
    assert "checkoutservice:" in text


def test_unknown_service(tmp_path: Path) -> None:
    path = tmp_path / "values.yaml"
    path.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    data = load_manifest(path)
    with pytest.raises(ValidationError, match="not found"):
        update_service_digest(data, "paymentservice", "sha256:" + ("c" * 64))


def test_scan_blocks_fixable_high() -> None:
    findings = findings_from_trivy(
        {"Results": [{"Vulnerabilities": [{"VulnerabilityID": "CVE-1", "Severity": "HIGH", "FixedVersion": "1.0"}]}]}
    )
    with pytest.raises(PolicyError, match="CVE-1"):
        assert_scan_clean(findings, ScanPolicy())


def test_scan_allows_unfixable_high() -> None:
    findings = findings_from_trivy(
        {"Results": [{"Vulnerabilities": [{"VulnerabilityID": "CVE-2", "Severity": "HIGH"}]}]}
    )
    assert_scan_clean(findings, ScanPolicy())


def test_cli_dry_run_does_not_write(tmp_path: Path) -> None:
    path = tmp_path / "values.yaml"
    original = FIXTURE.read_text(encoding="utf-8")
    path.write_text(original, encoding="utf-8")
    digest = "sha256:" + ("d" * 64)
    result = RUNNER.invoke(
        app,
        [
            "promote",
            "--manifest",
            str(path),
            "--service",
            "frontend",
            "--digest",
            digest,
            "--from-env",
            "staging",
            "--to-env",
            "prod",
        ],
    )
    assert result.exit_code == 0, result.output
    assert digest in result.output
    assert path.read_text(encoding="utf-8") == original


def test_cli_write_updates_file(tmp_path: Path) -> None:
    path = tmp_path / "values.yaml"
    path.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    digest = "sha256:" + ("e" * 64)
    result = RUNNER.invoke(
        app,
        [
            "promote",
            "--manifest",
            str(path),
            "--service",
            "frontend",
            "--digest",
            digest,
            "--from-env",
            "staging",
            "--to-env",
            "prod",
            "--write",
        ],
    )
    assert result.exit_code == 0, result.output
    assert digest in path.read_text(encoding="utf-8")
