"""Evaluate a Trivy-style JSON report before a digest is eligible to promote."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from platform_ops.exceptions import PolicyError


class ScanPolicy(BaseModel):
    fail_on: tuple[str, ...] = ("CRITICAL", "HIGH")
    allow: tuple[str, ...] = ()
    require_fixable: bool = True


class Finding(BaseModel):
    vulnerability_id: str
    severity: str
    fixed_by: str | None = None


class ScanVerdict(BaseModel):
    blocked: list[Finding] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.blocked


def findings_from_trivy(payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for result in payload.get("Results") or []:
        for vuln in result.get("Vulnerabilities") or []:
            findings.append(
                Finding(
                    vulnerability_id=str(vuln.get("VulnerabilityID", "UNKNOWN")),
                    severity=str(vuln.get("Severity", "UNKNOWN")).upper(),
                    fixed_by=vuln.get("FixedVersion") or None,
                )
            )
    return findings


def evaluate_findings(findings: list[Finding], policy: ScanPolicy) -> ScanVerdict:
    blocked: list[Finding] = []
    allow = set(policy.allow)
    fail_on = {item.upper() for item in policy.fail_on}
    for finding in findings:
        if finding.vulnerability_id in allow:
            continue
        if finding.severity not in fail_on:
            continue
        if policy.require_fixable and not finding.fixed_by:
            continue
        blocked.append(finding)
    return ScanVerdict(blocked=blocked)


def assert_scan_clean(findings: list[Finding], policy: ScanPolicy) -> None:
    verdict = evaluate_findings(findings, policy)
    if verdict.ok:
        return
    ids = ", ".join(f"{item.vulnerability_id}({item.severity})" for item in verdict.blocked)
    raise PolicyError(f"scan policy blocked promotion: {ids}")
