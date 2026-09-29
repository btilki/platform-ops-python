"""Tenant spec. CLI renders manifests; a Kopf operator can consume the same schema later."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from platform_ops.exceptions import PolicyError

RESERVED_NAMESPACES = frozenset(
    {
        "default",
        "kube-system",
        "kube-public",
        "kube-node-lease",
        "argocd",
        "cert-manager",
        "observability",
        "gatekeeper-system",
        "kyverno",
    }
)


def assert_not_reserved(name: str) -> None:
    if name in RESERVED_NAMESPACES:
        raise PolicyError(f"refusing reserved namespace {name!r}")


class Quota(BaseModel):
    cpu: str = "2"
    memory: str = "4Gi"
    pods: str = "20"


class ArgoCD(BaseModel):
    model_config = {"populate_by_name": True}

    repo_url: str = Field(alias="repoURL", min_length=8)
    dest_server: str = Field(default="https://kubernetes.default.svc", alias="destServer")
    source_path: str = Field(default="gitops/apps", alias="sourcePath")


class TenantSpec(BaseModel):
    team: str = Field(pattern=r"^[a-z][a-z0-9-]{0,30}$")
    environment: str = Field(pattern=r"^(dev|staging|prod)$")
    quota: Quota = Field(default_factory=Quota)
    argocd: ArgoCD


class TenantDocument(BaseModel):
    api_version: str = Field(alias="apiVersion")
    kind: str
    metadata: dict[str, str]
    spec: TenantSpec

    model_config = {"populate_by_name": True}

    @field_validator("kind")
    @classmethod
    def kind_is_tenant(cls, value: str) -> str:
        if value != "Tenant":
            raise ValueError("kind must be Tenant")
        return value

    @model_validator(mode="after")
    def name_is_safe(self) -> Self:
        name = self.metadata.get("name", "")
        if not name:
            raise ValueError("metadata.name is required")
        allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
        if len(name) > 63 or not name[0].islower() or any(ch not in allowed for ch in name):
            raise ValueError(f"metadata.name {name!r} is not a DNS-1123 label")
        if name.endswith("-"):
            raise ValueError(f"metadata.name {name!r} is not a DNS-1123 label")
        return self

    @property
    def name(self) -> str:
        return self.metadata["name"]
