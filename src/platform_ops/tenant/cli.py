"""CLI: render a tenant. Dry-run by default; --write emits YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError as PydanticValidationError
from ruamel.yaml import YAML

from platform_ops.cli_common import LogLevelOption, exit_from_error, init_runtime
from platform_ops.exceptions import PlatformOpsError, ValidationError
from platform_ops.logging import get_logger
from platform_ops.tenant.models import TenantDocument, assert_not_reserved
from platform_ops.tenant.render import render_tenant

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Render a Kubernetes tenant (namespace, quota, NetworkPolicy, Argo CD AppProject).",
)


@app.callback()
def _main(log_level: LogLevelOption = "info") -> None:
    init_runtime(log_level)


def load_tenant(path: Path) -> TenantDocument:
    yaml = YAML(typ="safe")
    raw = yaml.load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValidationError("tenant config must be a mapping")
    try:
        tenant = TenantDocument.model_validate(raw)
    except PydanticValidationError as exc:
        raise ValidationError(str(exc)) from exc
    assert_not_reserved(tenant.name)
    return tenant


@app.command("apply")
def apply_cmd(
    config: Annotated[Path, typer.Option(help="Tenant YAML (apiVersion/kind/metadata/spec)")],
    out: Annotated[Path | None, typer.Option(help="Directory for rendered manifests")] = None,
    write: Annotated[bool, typer.Option("--write", help="Write files instead of printing")] = False,
) -> None:
    log = get_logger("platform-tenant")
    try:
        tenant = load_tenant(config)
        rendered = render_tenant(tenant)
        log.info(
            "tenant.rendered",
            name=tenant.name,
            team=tenant.spec.team,
            environment=tenant.spec.environment,
            dry_run=not write,
        )
        if write:
            directory = out or Path("out") / tenant.name
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / "tenant.yaml"
            path.write_text(rendered, encoding="utf-8")
            typer.echo(f"wrote {path}")
        else:
            typer.echo(rendered, nl=False)
            typer.echo("dry-run: pass --write to emit files. This CLI does not kubectl-apply.")
    except PlatformOpsError as exc:
        exit_from_error(exc)
