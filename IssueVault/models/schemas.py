"""Dataclass schemas for service and repository communication."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class IssueSubmissionInput:
    """Structured payload required to create a new issue."""

    title: str
    description: str
    module_name: str
    environment: str
    severity: str
    priority: str
    category_id: int
    error_code: str | None = None
    steps_to_reproduce: str | None = None
    expected_result: str | None = None
    actual_result: str | None = None
    business_impact: str | None = None
    release_id: int | None = None
    assigned_to: int | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class IssueSearchFilters:
    """Flexible issue search parameters."""

    keyword: str | None = None
    title: str | None = None
    error_code: str | None = None
    module_name: str | None = None
    severity: str | None = None
    status: str | None = None
    category_id: int | None = None
    assigned_to: int | None = None
    created_from: date | None = None
    created_to: date | None = None
    reported_by: int | None = None


@dataclass
class ResolutionInput:
    """Payload to store issue resolution memory."""

    issue_id: int
    root_cause: str
    workaround: str
    final_fix: str
    resolution_steps: str
    resolver_id: int
    resolution_minutes: int
    resolved_at: datetime | None = None


@dataclass
class CommentInput:
    """Payload to create issue comments."""

    issue_id: int
    commented_by: int
    comment_text: str
    is_internal: bool = False


@dataclass
class AttachmentInput:
    """Metadata persisted for uploaded issue attachments."""

    issue_id: int
    original_filename: str
    stored_filename: str
    file_path: str
    file_size_bytes: int
    content_type: str | None
    uploaded_by: int


@dataclass
class SimilarIssue:
    """Similarity result object returned by the ranking service."""

    issue_id: int
    title: str
    status: str
    error_code: str | None
    module_name: str
    category_name: str
    score: float
    score_breakdown: dict[str, float]


@dataclass
class AuthUser:
    """User session payload used by Streamlit pages."""

    user_id: int
    username: str
    full_name: str
    email: str
    role_name: str
    team_name: str | None
