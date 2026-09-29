"""Shared Typer helpers."""

from __future__ import annotations

from typing import Annotated

import typer

from platform_ops.exceptions import PlatformOpsError
from platform_ops.logging import configure_logging

LogLevelOption = Annotated[
    str,
    typer.Option("--log-level", help="debug, info, warning, error", envvar="LOG_LEVEL"),
]


def init_runtime(log_level: str) -> None:
    configure_logging(log_level)


def exit_from_error(exc: PlatformOpsError) -> None:
    typer.secho(str(exc), err=True, fg=typer.colors.RED)
    raise typer.Exit(code=exc.exit_code) from exc
