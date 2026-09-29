"""Typed failures with stable process exit codes."""

from __future__ import annotations


class PlatformOpsError(Exception):
    """Base error for CLI tools in this repository."""

    exit_code = 1


class ValidationError(PlatformOpsError):
    """User input or file contents failed validation."""

    exit_code = 2


class PolicyError(PlatformOpsError):
    """A safety policy refused to continue."""

    exit_code = 3


class IntegrationError(PlatformOpsError):
    """An upstream API or subprocess failed."""

    exit_code = 4
