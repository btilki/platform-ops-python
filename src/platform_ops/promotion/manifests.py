"""Round-trip Helm/Kustomize YAML so GitOps PRs do not reformat the whole file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from platform_ops.exceptions import ValidationError
from platform_ops.promotion.digest import normalize_digest


def yaml_rt() -> YAML:
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.width = 120
    yaml.explicit_start = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def load_manifest(path: Path) -> Any:
    yaml = yaml_rt()
    with path.open(encoding="utf-8") as handle:
        return yaml.load(handle)


def dump_manifest(data: Any, path: Path) -> str:
    yaml = yaml_rt()
    from io import StringIO

    buf = StringIO()
    yaml.dump(data, buf)
    text = buf.getvalue()
    path.write_text(text, encoding="utf-8")
    return text


def render_manifest(data: Any) -> str:
    yaml = yaml_rt()
    from io import StringIO

    buf = StringIO()
    yaml.dump(data, buf)
    return buf.getvalue()


def update_service_digest(data: Any, service: str, digest: str) -> str:
    """Set images.<service>.digest in boutique-style Helm values."""
    normalized = normalize_digest(digest)
    images = _require_map(data, "images")
    if service not in images:
        known = ", ".join(sorted(str(key) for key in images))
        raise ValidationError(f"service {service!r} not found under images:; known: {known}")
    entry = images[service]
    if isinstance(entry, CommentedSeq | list):
        raise ValidationError(f"images.{service} is a list; expected mapping with repository/digest")
    service_map = _as_map(entry, f"images.{service}")
    previous = str(service_map.get("digest", ""))
    service_map["digest"] = normalized
    return previous


def _require_map(data: Any, key: str) -> CommentedMap:
    if not isinstance(data, dict | CommentedMap):
        raise ValidationError("manifest root must be a mapping")
    value = data.get(key)
    return _as_map(value, key)


def _as_map(value: Any, path: str) -> CommentedMap:
    if isinstance(value, CommentedMap):
        return value
    if isinstance(value, dict):
        return CommentedMap(value)
    raise ValidationError(f"{path} must be a mapping")
