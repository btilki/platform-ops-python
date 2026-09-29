"""Render namespace, quota, network policy, and Argo CD AppProject."""

from __future__ import annotations

from io import StringIO

from ruamel.yaml import YAML

from platform_ops.tenant.models import TenantDocument


def render_tenant(tenant: TenantDocument) -> str:
    docs = [
        _namespace(tenant),
        _quota(tenant),
        _limit_range(tenant),
        _network_policy(tenant),
        _app_project(tenant),
    ]
    yaml = YAML()
    yaml.explicit_start = True
    yaml.width = 120
    yaml.indent(mapping=2, sequence=4, offset=2)
    buf = StringIO()
    yaml.dump_all(docs, buf)
    return buf.getvalue()


def _labels(tenant: TenantDocument) -> dict[str, str]:
    return {
        "app.kubernetes.io/managed-by": "platform-tenant",
        "platform.biroltilki.dev/tenant": tenant.name,
        "platform.biroltilki.dev/team": tenant.spec.team,
        "platform.biroltilki.dev/environment": tenant.spec.environment,
    }


def _namespace(tenant: TenantDocument) -> dict[str, object]:
    return {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": tenant.name, "labels": _labels(tenant)},
    }


def _quota(tenant: TenantDocument) -> dict[str, object]:
    return {
        "apiVersion": "v1",
        "kind": "ResourceQuota",
        "metadata": {"name": "tenant-quota", "namespace": tenant.name, "labels": _labels(tenant)},
        "spec": {
            "hard": {
                "requests.cpu": tenant.spec.quota.cpu,
                "requests.memory": tenant.spec.quota.memory,
                "pods": tenant.spec.quota.pods,
            }
        },
    }


def _limit_range(tenant: TenantDocument) -> dict[str, object]:
    return {
        "apiVersion": "v1",
        "kind": "LimitRange",
        "metadata": {"name": "tenant-limits", "namespace": tenant.name, "labels": _labels(tenant)},
        "spec": {
            "limits": [
                {
                    "type": "Container",
                    "defaultRequest": {"cpu": "50m", "memory": "64Mi"},
                    "default": {"cpu": "200m", "memory": "256Mi"},
                }
            ]
        },
    }


def _network_policy(tenant: TenantDocument) -> dict[str, object]:
    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {"name": "default-deny", "namespace": tenant.name, "labels": _labels(tenant)},
        "spec": {
            "podSelector": {},
            "policyTypes": ["Ingress", "Egress"],
            "egress": [
                {
                    "to": [{"namespaceSelector": {"matchLabels": {"kubernetes.io/metadata.name": "kube-system"}}}],
                    "ports": [{"protocol": "UDP", "port": 53}],
                }
            ],
        },
    }


def _app_project(tenant: TenantDocument) -> dict[str, object]:
    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "AppProject",
        "metadata": {"name": tenant.name, "namespace": "argocd", "labels": _labels(tenant)},
        "spec": {
            "description": f"Tenant {tenant.name} owned by {tenant.spec.team}",
            "sourceRepos": [tenant.spec.argocd.repo_url],
            "destinations": [
                {"namespace": tenant.name, "server": tenant.spec.argocd.dest_server},
            ],
            "namespaceResourceWhitelist": [
                {"group": "", "kind": "ConfigMap"},
                {"group": "", "kind": "Secret"},
                {"group": "apps", "kind": "Deployment"},
                {"group": "apps", "kind": "ReplicaSet"},
                {"group": "networking.k8s.io", "kind": "NetworkPolicy"},
            ],
            "clusterResourceWhitelist": [],
        },
    }
