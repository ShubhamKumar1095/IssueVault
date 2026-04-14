"""Application-specific exception classes."""

from __future__ import annotations


class IssueVaultError(Exception):
    """Base application exception."""


class ValidationError(IssueVaultError):
    """Raised when input validation fails."""


class AuthenticationError(IssueVaultError):
    """Raised when authentication fails."""


class AuthorizationError(IssueVaultError):
    """Raised when user is not allowed to perform operation."""


class NotFoundError(IssueVaultError):
    """Raised when entity was not found."""
