"""Error-budget arithmetic used by slo-kit report and by generated alerts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from platform_ops.exceptions import ValidationError

BudgetBand = Literal["normal", "cautious", "freeze", "sev2"]


class BudgetReport(BaseModel):
    sli: float
    objective: float
    error_budget: float
    consumed: float
    remaining: float
    remaining_pct: float
    band: BudgetBand
    window_minutes: float = Field(description="Approximate error-budget minutes in a 30-day month")


def remaining_budget(sli: float, objective: float) -> BudgetReport:
    if not 0 <= sli <= 1:
        raise ValidationError(f"sli must be in [0, 1], got {sli}")
    if not 0 < objective < 1:
        raise ValidationError(f"objective must be in (0, 1), got {objective}")
    error_budget = 1.0 - objective
    consumed = max(0.0, (1.0 - sli) / error_budget)
    remaining = max(0.0, 1.0 - consumed)
    band = _band(remaining)
    minutes = error_budget * 30 * 24 * 60
    return BudgetReport(
        sli=sli,
        objective=objective,
        error_budget=error_budget,
        consumed=min(consumed, 1.0),
        remaining=remaining,
        remaining_pct=round(remaining * 100, 2),
        band=band,
        window_minutes=round(minutes, 1),
    )


def _band(remaining: float) -> BudgetBand:
    if remaining <= 0:
        return "sev2"
    if remaining < 0.25:
        return "freeze"
    if remaining < 0.50:
        return "cautious"
    return "normal"
