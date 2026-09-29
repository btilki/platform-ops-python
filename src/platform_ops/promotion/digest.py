"""Digest and image-reference validation."""

from __future__ import annotations

import re

from platform_ops.exceptions import ValidationError

DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


def normalize_digest(value: str) -> str:
    digest = value.strip().lower()
    if digest.startswith("@"):
        digest = digest[1:]
    if not DIGEST_RE.fullmatch(digest):
        raise ValidationError(
            f"digest must be sha256:<64 hex chars>, got {value!r}. Mutable tags such as :latest are refused."
        )
    return digest


def assert_not_latest(reference: str) -> None:
    ref = reference.strip()
    if ref.endswith(":latest") or ":latest@" in ref or ref.endswith("/latest"):
        raise ValidationError(f"refusing mutable tag in {reference!r}")
    if re.search(r":latest(?:$|@)", ref):
        raise ValidationError(f"refusing mutable tag in {reference!r}")
