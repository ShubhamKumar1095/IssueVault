"""Enumerations used across ResolveHub."""

from __future__ import annotations

from enum import Enum


class RoleEnum(str, Enum):
    """Application roles."""

    END_USER = "end_user"
    SUPPORT_ANALYST = "support_analyst"
    CONSULTANT = "consultant"
    MANAGER = "manager"
    ADMIN = "admin"


class IssueStatusEnum(str, Enum):
    """Issue lifecycle statuses."""

    NEW = "New"
    UNDER_REVIEW = "Under Review"
    KNOWN_ISSUE = "Known Issue"
    IN_PROGRESS = "In Progress"
    WAITING_FOR_USER = "Waiting for User"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    REOPENED = "Reopened"


class SeverityEnum(str, Enum):
    """Issue severity levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class PriorityEnum(str, Enum):
    """Issue priority levels."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class LinkTypeEnum(str, Enum):
    """Issue relationship link types."""

    DUPLICATE = "duplicate"
    PARENT = "parent"
    DEPENDENT = "dependent"
    RECURRING = "recurring"
    BLOCKER = "blocker"
