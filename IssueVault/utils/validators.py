"""Validation utilities for ResolveHub inputs."""

from __future__ import annotations

from datetime import date
from typing import Any

from config import get_settings
from models.enums import PriorityEnum, SeverityEnum
from models.schemas import IssueSearchFilters, IssueSubmissionInput, ResolutionInput


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


def validate_issue_submission(payload: IssueSubmissionInput) -> list[str]:
    """Validate issue submission payload."""
    errors: list[str] = []

    if _is_blank(payload.title) or len(payload.title.strip()) < 5:
        errors.append("Title must be at least 5 characters.")
    if _is_blank(payload.description) or len(payload.description.strip()) < 15:
        errors.append("Description must be at least 15 characters.")
    if _is_blank(payload.module_name):
        errors.append("Module is required.")
    if _is_blank(payload.environment):
        errors.append("Environment is required.")
    if payload.severity not in {item.value for item in SeverityEnum}:
        errors.append("Severity is invalid.")
    if payload.priority not in {item.value for item in PriorityEnum}:
        errors.append("Priority is invalid.")
    if payload.category_id <= 0:
        errors.append("Issue category is required.")

    return errors


def validate_resolution_input(payload: ResolutionInput) -> list[str]:
    """Validate resolution payload."""
    errors: list[str] = []
    if payload.issue_id <= 0:
        errors.append("Issue id is invalid.")
    if _is_blank(payload.root_cause):
        errors.append("Root cause is required.")
    if _is_blank(payload.final_fix):
        errors.append("Final fix is required.")
    if _is_blank(payload.resolution_steps):
        errors.append("Resolution steps are required.")
    if payload.resolution_minutes <= 0:
        errors.append("Resolution minutes must be greater than 0.")
    if payload.resolver_id <= 0:
        errors.append("Resolver id is invalid.")
    return errors


def validate_search_filters(filters: IssueSearchFilters) -> list[str]:
    """Validate issue search filters."""
    errors: list[str] = []
    if filters.created_from and filters.created_to and filters.created_from > filters.created_to:
        errors.append("Created from date cannot be after created to date.")
    return errors


def validate_attachment(file_obj: Any) -> str | None:
    """
    Validate uploaded file extension and size.

    Returns:
        str | None: Error message when invalid.
    """
    if file_obj is None:
        return None

    settings = get_settings()
    name = getattr(file_obj, "name", "")
    size = getattr(file_obj, "size", 0)

    if "." not in name:
        return "Attachment must have a valid file extension."

    ext = name.rsplit(".", 1)[1].lower()
    if ext not in settings.allowed_extensions:
        return (
            f"Unsupported file extension '.{ext}'. "
            f"Allowed: {', '.join(settings.allowed_extensions)}"
        )

    max_size_bytes = settings.max_upload_mb * 1024 * 1024
    if size > max_size_bytes:
        return f"Attachment exceeds max size of {settings.max_upload_mb}MB."

    return None


def parse_optional_date(value: date | None) -> date | None:
    """Pass-through helper to keep date parsing centralized."""
    return value
