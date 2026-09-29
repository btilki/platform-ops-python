"""CLI: compile SLO YAML and report remaining error budget."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from platform_ops.cli_common import LogLevelOption, exit_from_error, init_runtime
from platform_ops.exceptions import PlatformOpsError
from platform_ops.logging import get_logger
from platform_ops.slo.budget import remaining_budget
from platform_ops.slo.compile import compile_rules, load_spec

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Compile SLO specs to PrometheusRule YAML and report remaining error budget.",
)


@app.callback()
def _main(log_level: LogLevelOption = "info") -> None:
    init_runtime(log_level)


@app.command("compile")
def compile_cmd(
    spec: Annotated[Path, typer.Option(help="YAML document with slos: []")],
    out: Annotated[Path | None, typer.Option(help="Write PrometheusRule YAML here")] = None,
    stdout: Annotated[bool, typer.Option("--stdout", help="Print generated YAML")] = False,
) -> None:
    log = get_logger("slo-kit")
    try:
        document = load_spec(spec)
        rendered = compile_rules(document)
        log.info("slo.compiled", count=len(document.slos), names=[item.name for item in document.slos])
        if stdout or out is None:
            typer.echo(rendered, nl=False)
        if out is not None:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(rendered, encoding="utf-8")
            typer.echo(f"wrote {out}", err=True)
    except PlatformOpsError as exc:
        exit_from_error(exc)


@app.command("report")
def report_cmd(
    sli: Annotated[float, typer.Option(help="Observed good/total ratio in [0, 1]")],
    objective: Annotated[float, typer.Option(help="SLO objective in (0, 1), e.g. 0.999")],
) -> None:
    log = get_logger("slo-kit")
    try:
        report = remaining_budget(sli, objective)
        log.info("slo.budget", **report.model_dump())
        typer.echo(f"sli: {report.sli}")
        typer.echo(f"objective: {report.objective}")
        typer.echo(f"remaining: {report.remaining_pct}%")
        typer.echo(f"band: {report.band}")
        typer.echo(f"budget_minutes_per_30d: {report.window_minutes}")
    except PlatformOpsError as exc:
        exit_from_error(exc)
