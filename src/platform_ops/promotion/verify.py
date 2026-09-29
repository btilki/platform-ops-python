"""Optional cosign verification. Default path skips it so CI helpers stay testable."""

from __future__ import annotations

import shutil
import subprocess
from typing import Protocol

from platform_ops.exceptions import IntegrationError, PolicyError


class SignatureVerifier(Protocol):
    def verify(self, image: str, digest: str) -> None: ...


class SkipVerifier:
    def verify(self, image: str, digest: str) -> None:
        return


class CosignVerifier:
    def __init__(self, binary: str = "cosign", timeout_s: float = 30.0) -> None:
        self.binary = binary
        self.timeout_s = timeout_s

    def verify(self, image: str, digest: str) -> None:
        if shutil.which(self.binary) is None:
            raise IntegrationError(f"{self.binary} is not on PATH; cannot verify {image}@{digest}")
        ref = f"{image}@{digest}"
        try:
            completed = subprocess.run(  # noqa: S603
                [self.binary, "verify", ref],
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
            )
        except subprocess.TimeoutExpired as exc:
            raise IntegrationError(f"cosign verify timed out for {ref}") from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            raise PolicyError(f"cosign verify failed for {ref}: {detail}")
