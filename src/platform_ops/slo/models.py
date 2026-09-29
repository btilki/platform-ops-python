"""SLO specification. Objectives must be in (0, 1)."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator


class SLI(BaseModel):
    good: str = Field(min_length=1, description="Instant-vector selector counted as good events")
    total: str = Field(min_length=1, description="Instant-vector selector counted as all events")


class BurnWindow(BaseModel):
    short: str
    long: str
    burn_rate: float = Field(gt=0)
    severity: Literal["page", "ticket"]


DEFAULT_BURNS: tuple[BurnWindow, ...] = (
    BurnWindow(short="5m", long="1h", burn_rate=14.4, severity="page"),
    BurnWindow(short="30m", long="6h", burn_rate=6.0, severity="page"),
    BurnWindow(short="2h", long="1d", burn_rate=3.0, severity="ticket"),
    BurnWindow(short="6h", long="3d", burn_rate=1.0, severity="ticket"),
)


class SLOSpec(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{1,61}[a-z0-9]$")
    service: str = Field(min_length=1)
    objective: float = Field(gt=0, lt=1, description="Availability or success-ratio target, e.g. 0.999")
    window: str = "30d"
    sli: SLI
    owner: str = "platform"
    burns: list[BurnWindow] = Field(default_factory=lambda: list(DEFAULT_BURNS))

    @field_validator("objective")
    @classmethod
    def objective_not_one(cls, value: float) -> float:
        if value >= 1:
            raise ValueError("objective must be < 1 so error budget is non-zero")
        return value

    @model_validator(mode="after")
    def burns_present(self) -> Self:
        if not self.burns:
            raise ValueError("at least one burn window is required")
        return self


class SLODocument(BaseModel):
    slos: list[SLOSpec] = Field(min_length=1)
