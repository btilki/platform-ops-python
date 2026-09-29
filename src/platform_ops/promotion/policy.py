"""Environment promotion rules. CI never skips the adjacent path."""

from __future__ import annotations

from platform_ops.exceptions import PolicyError

ENV_ORDER: tuple[str, ...] = ("dev", "staging", "prod")


def assert_adjacent_promotion(source: str, target: str) -> None:
    try:
        src_idx = ENV_ORDER.index(source)
        dst_idx = ENV_ORDER.index(target)
    except ValueError as exc:
        raise PolicyError(f"environments must be one of {list(ENV_ORDER)}, got {source!r} → {target!r}") from exc
    if dst_idx != src_idx + 1:
        raise PolicyError(f"promotions must be adjacent ({' → '.join(ENV_ORDER)}); refusing {source} → {target}")
