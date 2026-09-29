"""Compile SLO specs into PrometheusRule YAML."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

from platform_ops.exceptions import ValidationError
from platform_ops.slo.models import SLODocument, SLOSpec


def load_spec(path: Path) -> SLODocument:
    yaml = YAML(typ="safe")
    raw = yaml.load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValidationError("SLO spec must be a mapping with a slos: list")
    try:
        return SLODocument.model_validate(raw)
    except PydanticValidationError as exc:
        raise ValidationError(str(exc)) from exc


def compile_rules(document: SLODocument) -> str:
    payload = {
        "apiVersion": "monitoring.coreos.com/v1",
        "kind": "PrometheusRule",
        "metadata": {
            "name": "slo-kit",
            "labels": {
                "app.kubernetes.io/managed-by": "slo-kit",
                "app.kubernetes.io/part-of": "platform-ops-python",
            },
        },
        "spec": {"groups": [_group(spec) for spec in document.slos]},
    }
    yaml = YAML()
    yaml.explicit_start = False
    yaml.width = 120
    yaml.indent(mapping=2, sequence=4, offset=2)
    buf = StringIO()
    yaml.dump(payload, buf)
    return buf.getvalue()


def _group(spec: SLOSpec) -> dict[str, object]:
    budget = 1.0 - spec.objective
    rules: list[dict[str, object]] = [
        {
            "record": f"slo:sli_good:ratio_rate5m:{spec.name}",
            "expr": f"sum(rate({spec.sli.good}[5m])) / sum(rate({spec.sli.total}[5m]))",
        }
    ]
    for burn in spec.burns:
        expr = (
            f"(1 - (sum(rate({spec.sli.good}[{burn.long}])) / sum(rate({spec.sli.total}[{burn.long}]))))"
            f" / {budget} > {burn.burn_rate}\n"
            f"and\n"
            f"(1 - (sum(rate({spec.sli.good}[{burn.short}])) / sum(rate({spec.sli.total}[{burn.short}]))))"
            f" / {budget} > {burn.burn_rate}\n"
        )
        rules.append(
            {
                "alert": _alert_name(spec.name, burn.long, burn.severity),
                "expr": LiteralScalarString(expr),
                "labels": {
                    "severity": "critical" if burn.severity == "page" else "warning",
                    "slo": spec.name,
                    "service": spec.service,
                    "burn_window": burn.long,
                    "owner": spec.owner,
                },
                "annotations": {
                    "summary": f"{spec.name} is burning error budget ({burn.severity}, {burn.long})",
                    "description": (
                        f"Multi-window burn {burn.burn_rate}x over {burn.short}/{burn.long} "
                        f"for objective {spec.objective} (window {spec.window})."
                    ),
                },
            }
        )
    return {"name": f"slo.{spec.name}", "rules": rules}


def _alert_name(slo_name: str, window: str, severity: str) -> str:
    compact = "".join(part.capitalize() for part in slo_name.split("-"))
    return f"{compact}Burn{window}{severity.capitalize()}"
