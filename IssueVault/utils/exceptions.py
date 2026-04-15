"""Application-specific exception classes."""

from __future__ import annotations


class ResolveHubError(Exception):
    """Base application exception."""


class ValidationError(ResolveHubError):
    """Raised when input validation fails."""


class AuthenticationError(ResolveHubError):
    """Raised when authentication fails."""


class AuthorizationError(ResolveHubError):
    """Raised when user is not allowed to perform operation."""


class NotFoundError(ResolveHubError):
    """Raised when entity was not found."""


# Backward-compatible alias.
IssueVaultError = ResolveHubError
