"""CLI: promote a digest into GitOps YAML. Default is dry-run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Optional
from uuid import uuid4

import typer
from pydantic_settings import BaseSettings, SettingsConfigDict

from platform_ops.cli_common import LogLevelOption, exit_from_error, init_runtime
from platform_ops.exceptions import PlatformOpsError, ValidationError
from platform_ops.logging import get_logger
from platform_ops.promotion.digest import normalize_digest
from platform_ops.promotion.github_pr import DryRunOpener, GitHubOpener, PullRequestOpener
from platform_ops.promotion.manifests import dump_manifest, load_manifest, render_manifest, update_service_digest
from platform_ops.promotion.policy import assert_adjacent_promotion
from platform_ops.promotion.scan import ScanPolicy, assert_scan_clean, findings_from_trivy
from platform_ops.promotion.verify import CosignVerifier, SignatureVerifier, SkipVerifier

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Promote digest-pinned images into GitOps manifests. CI never kubectl-applies.",
)


class PromotionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROMOTION_", extra="ignore")

    github_token: str = ""
    github_repository: str = ""
    github_api_url: str = "https://api.github.com"


def _opener(write_pr: bool, settings: PromotionSettings) -> PullRequestOpener:
    if not write_pr:
        return DryRunOpener()
    return GitHubOpener(token=settings.github_token, api_url=settings.github_api_url)


def _verifier(require_signature: bool) -> SignatureVerifier:
    if require_signature:
        return CosignVerifier()
    return SkipVerifier()


def _pr_body(
    *,
    service: str,
    digest: str,
    previous: str,
    source: str,
    target: str,
    signature: str,
    scan: str,
) -> str:
    return (
        "## Digest promotion\n\n"
        "| Field | Value |\n| --- | --- |\n"
        f"| Service | `{service}` |\n"
        f"| From env | `{source}` |\n"
        f"| To env | `{target}` |\n"
        f"| Previous digest | `{previous or 'none'}` |\n"
        f"| New digest | `{digest}` |\n"
        f"| Signature | {signature} |\n"
        f"| Scan | {scan} |\n\n"
        "CI never `kubectl apply`. Merge this PR; Argo CD reconciles.\n"
    )


@app.callback()
def _main(log_level: LogLevelOption = "info") -> None:
    init_runtime(log_level)


@app.command("promote")
def promote(
    manifest: Annotated[Path, typer.Option(help="Helm values or GitOps YAML with images.<svc>.digest")],
    service: Annotated[str, typer.Option(help="Service key under images:")],
    digest: Annotated[str, typer.Option(help="sha256:<64 hex>")],
    from_env: Annotated[str, typer.Option("--from-env", help="Source environment")] = "staging",
    to_env: Annotated[str, typer.Option("--to-env", help="Target environment")] = "prod",
    image: Annotated[str, typer.Option(help="Repository used for cosign verify")] = "",
    trivy_json: Annotated[
        Optional[Path],
        typer.Option(help="Optional Trivy JSON; HIGH/CRITICAL with a fix version block promotion"),
    ] = None,
    require_signature: Annotated[bool, typer.Option(help="Run cosign verify before mutating YAML")] = False,
    write: Annotated[bool, typer.Option("--write", help="Write the digest into the local manifest")] = False,
    open_pr: Annotated[bool, typer.Option("--open-pr", help="Open a GitHub PR (requires GITHUB_TOKEN)")] = False,
    repo: Annotated[str, typer.Option(help="owner/name for --open-pr")] = "",
    path_in_repo: Annotated[str, typer.Option(help="Path of the manifest inside the Git repo")] = "",
) -> None:
    """Update a digest pin. Dry-run unless --write and/or --open-pr is set."""
    log = get_logger("promotion-bot")
    settings = PromotionSettings()
    try:
        normalized = normalize_digest(digest)
        assert_adjacent_promotion(from_env, to_env)
        if not manifest.is_file():
            raise ValidationError(f"manifest not found: {manifest}")
        original = manifest.read_text(encoding="utf-8")
        data = load_manifest(manifest)
        previous = update_service_digest(data, service, normalized)
        rendered = render_manifest(data)

        scan_label = "skipped"
        if trivy_json is not None:
            payload = json.loads(trivy_json.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValidationError("Trivy JSON root must be an object")
            assert_scan_clean(findings_from_trivy(payload), ScanPolicy())
            scan_label = "passed"

        signature_label = "skipped"
        if require_signature:
            if not image:
                raise ValidationError("--image is required with --require-signature")
            _verifier(True).verify(image, normalized)
            signature_label = "verified"

        log.info(
            "promotion.planned",
            service=service,
            digest=normalized,
            previous=previous or None,
            from_env=from_env,
            to_env=to_env,
            dry_run=not write and not open_pr,
        )

        if original == rendered:
            typer.echo("No change: digest already at target.")
            raise typer.Exit(code=0)

        typer.echo(f"service: {service}")
        typer.echo(f"previous: {previous or 'none'}")
        typer.echo(f"new: {normalized}")
        typer.echo(f"path: {from_env} → {to_env}")
        typer.echo("--- yaml ---")
        typer.echo(rendered, nl=False)

        if write:
            dump_manifest(data, manifest)
            log.info("promotion.written", path=str(manifest))

        if open_pr:
            repository = repo or settings.github_repository
            if not repository:
                raise ValidationError("--repo or PROMOTION_GITHUB_REPOSITORY is required for --open-pr")
            git_path = path_in_repo or manifest.as_posix()
            branch = f"ci/digest-{service}-{uuid4().hex[:8]}"
            body = _pr_body(
                service=service,
                digest=normalized,
                previous=previous,
                source=from_env,
                target=to_env,
                signature=signature_label,
                scan=scan_label,
            )
            url = _opener(True, settings).open_pr(
                repo=repository,
                path=git_path,
                content=rendered,
                branch=branch,
                title=f"ci: promote {service} digest",
                body=body,
                commit_message=f"ci: pin {service} to {normalized}",
            )
            typer.echo(f"pull_request: {url}")
        elif not write:
            typer.echo("dry-run: pass --write to update the file, --open-pr to open a GitHub PR.")
    except PlatformOpsError as exc:
        exit_from_error(exc)
