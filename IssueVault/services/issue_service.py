"""Issue lifecycle orchestration service."""

from __future__ import annotations

from typing import Any

from models.enums import IssueStatusEnum, RoleEnum
from models.schemas import AttachmentInput, IssueSearchFilters, IssueSubmissionInput
from repositories.attachment_repository import AttachmentRepository
from repositories.comment_repository import CommentRepository
from repositories.issue_repository import IssueRepository
from repositories.resolution_repository import ResolutionRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.search_service import SearchService
from services.similarity_service import SimilarityService
from utils.exceptions import AuthorizationError, NotFoundError, ValidationError
from utils.file_storage import save_attachment
from utils.validators import validate_attachment, validate_issue_submission


class IssueService:
    """Service for submit, triage, search, and collaboration workflows."""

    def __init__(self) -> None:
        self.issue_repo = IssueRepository()
        self.comment_repo = CommentRepository()
        self.attachment_repo = AttachmentRepository()
        self.resolution_repo = ResolutionRepository()
        self.user_repo = UserRepository()
        self.auth_service = AuthService()
        self.search_service = SearchService()
        self.similarity_service = SimilarityService()

    def get_submission_metadata(self) -> dict[str, list[dict[str, Any]]]:
        """Return reference data required by submit/search/admin pages."""
        users = self.user_repo.list_users()
        assignable = [
            item
            for item in users
            if item.get("role_name") in {RoleEnum.SUPPORT_ANALYST.value, RoleEnum.CONSULTANT.value}
        ]
        return {
            "categories": self.issue_repo.list_categories(),
            "releases": self.issue_repo.list_releases(),
            "tags": self.issue_repo.list_tags(),
            "assignable_users": assignable,
            "roles": self.user_repo.list_roles(),
            "teams": self.user_repo.list_teams(),
            "users": users,
        }

    def preview_similar_issues(self, payload: IssueSubmissionInput) -> list[dict[str, Any]]:
        """Find likely duplicate/similar issues before save."""
        category_name = None
        for category in self.issue_repo.list_categories():
            if int(category["category_id"]) == int(payload.category_id):
                category_name = str(category["category_name"])
                break

        similar = self.similarity_service.find_similar_issues(
            title=payload.title,
            description=payload.description,
            module_name=payload.module_name,
            category_name=category_name,
            error_code=payload.error_code,
            top_n=5,
        )
        return [
            {
                "issue_id": item.issue_id,
                "title": item.title,
                "status": item.status,
                "error_code": item.error_code,
                "module_name": item.module_name,
                "category_name": item.category_name,
                "score": item.score,
                "score_breakdown": item.score_breakdown,
            }
            for item in similar
        ]

    def submit_issue(
        self,
        payload: IssueSubmissionInput,
        reporter_user: dict[str, Any],
        uploaded_files: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Validate and create issue with optional attachments."""
        if not self.auth_service.can_submit_issue(reporter_user):
            raise AuthorizationError("Your role is not allowed to submit issues.")

        errors = validate_issue_submission(payload)
        if errors:
            raise ValidationError("; ".join(errors))

        issue_id = self.issue_repo.create_issue(payload, int(reporter_user["user_id"]))
        self.issue_repo.add_status_history(
            issue_id=issue_id,
            old_status=None,
            new_status=IssueStatusEnum.NEW.value,
            changed_by=int(reporter_user["user_id"]),
            notes="Issue submitted.",
        )

        for tag in payload.tags:
            tag_name = tag.strip().lower()
            if not tag_name:
                continue
            tag_id = self.issue_repo.get_or_create_tag(tag_name)
            self.issue_repo.add_issue_tag(issue_id=issue_id, tag_id=tag_id, created_by=int(reporter_user["user_id"]))

        attachment_rows: list[dict[str, Any]] = []
        for file_obj in uploaded_files or []:
            if file_obj is None:
                continue
            error_msg = validate_attachment(file_obj)
            if error_msg:
                raise ValidationError(f"{getattr(file_obj, 'name', 'file')}: {error_msg}")

            metadata = save_attachment(file_obj, issue_id=issue_id)
            attachment_id = self.attachment_repo.add_attachment(
                AttachmentInput(
                    issue_id=issue_id,
                    original_filename=str(metadata["original_filename"]),
                    stored_filename=str(metadata["stored_filename"]),
                    file_path=str(metadata["file_path"]),
                    file_size_bytes=int(metadata["file_size_bytes"]),
                    content_type=str(metadata["content_type"]) if metadata.get("content_type") else None,
                    uploaded_by=int(reporter_user["user_id"]),
                )
            )
            attachment_rows.append({"attachment_id": attachment_id, **metadata})

        return {"issue_id": issue_id, "attachments": attachment_rows}

    def get_issue_bundle(self, issue_id: int, viewer_user: dict[str, Any]) -> dict[str, Any]:
        """Return detailed issue payload with collaboration and resolution memory."""
        issue = self.issue_repo.get_issue_by_id(issue_id)
        if not issue:
            raise NotFoundError("Issue not found.")

        if not self.auth_service.can_view_issue(viewer_user, issue):
            raise AuthorizationError("You do not have permission to view this issue.")

        include_internal = viewer_user.get("role_name") != RoleEnum.END_USER.value
        comments = self.comment_repo.list_comments(issue_id=issue_id, include_internal=include_internal)
        attachments = self.attachment_repo.list_attachments(issue_id=issue_id)
        status_history = self.issue_repo.list_issue_status_history(issue_id=issue_id)
        linked_issues = self.issue_repo.list_linked_issues(issue_id=issue_id)
        resolution = self.resolution_repo.get_resolution_by_issue_id(issue_id=issue_id)
        feedback = self.resolution_repo.list_solution_feedback(issue_id=issue_id) if resolution else []
        tags = self.issue_repo.list_issue_tags(issue_id)

        return {
            "issue": issue,
            "comments": comments,
            "attachments": attachments,
            "status_history": status_history,
            "linked_issues": linked_issues,
            "resolution": resolution,
            "solution_feedback": feedback,
            "tags": tags,
        }

    def search_issues(self, filters: IssueSearchFilters, user: dict[str, Any]) -> list[dict[str, Any]]:
        """Search issues with role-aware scope."""
        return self.search_service.search_issues(filters, user)

    def list_my_issues(self, user: dict[str, Any]) -> list[dict[str, Any]]:
        """List current user's issues."""
        return self.search_service.list_my_issues(user)

    def update_issue_status(
        self,
        issue_id: int,
        new_status: str,
        actor_user: dict[str, Any],
        notes: str | None = None,
    ) -> None:
        """Transition issue status and capture status history."""
        issue = self.issue_repo.get_issue_by_id(issue_id)
        if not issue:
            raise NotFoundError("Issue not found.")
        if not self.auth_service.can_update_issue(actor_user, issue):
            raise AuthorizationError("You do not have permission to update this issue.")

        old_status = str(issue["status"])
        if old_status == new_status:
            return

        self.issue_repo.update_issue_status(issue_id, new_status)
        self.issue_repo.add_status_history(
            issue_id=issue_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=int(actor_user["user_id"]),
            notes=notes,
        )

    def assign_issue(self, issue_id: int, assigned_to: int | None, actor_user: dict[str, Any]) -> None:
        """Assign issue to support/consultant user."""
        role_name = actor_user.get("role_name")
        if role_name not in {
            RoleEnum.ADMIN.value,
            RoleEnum.SUPPORT_ANALYST.value,
            RoleEnum.CONSULTANT.value,
        }:
            raise AuthorizationError("You are not allowed to assign issues.")

        issue = self.issue_repo.get_issue_by_id(issue_id)
        if not issue:
            raise NotFoundError("Issue not found.")

        self.issue_repo.assign_issue(issue_id, assigned_to)

    def add_comment(
        self,
        issue_id: int,
        actor_user: dict[str, Any],
        comment_text: str,
        is_internal: bool = False,
    ) -> None:
        """Add issue comment with role checks."""
        issue = self.issue_repo.get_issue_by_id(issue_id)
        if not issue:
            raise NotFoundError("Issue not found.")
        if not self.auth_service.can_view_issue(actor_user, issue):
            raise AuthorizationError("You do not have access to comment on this issue.")

        if actor_user.get("role_name") == RoleEnum.END_USER.value:
            is_internal = False

        text = comment_text.strip()
        if not text:
            raise ValidationError("Comment cannot be empty.")

        self.comment_repo.add_comment(
            issue_id=issue_id,
            commented_by=int(actor_user["user_id"]),
            comment_text=text,
            is_internal=is_internal,
        )

    def link_issues(
        self,
        issue_id: int,
        linked_issue_id: int,
        link_type: str,
        actor_user: dict[str, Any],
    ) -> None:
        """Create issue relationship link."""
        issue = self.issue_repo.get_issue_by_id(issue_id)
        if not issue:
            raise NotFoundError("Issue not found.")
        if not self.auth_service.can_update_issue(actor_user, issue):
            raise AuthorizationError("You do not have permission to link this issue.")
        if issue_id == linked_issue_id:
            raise ValidationError("Issue cannot be linked to itself.")

        self.issue_repo.create_issue_link(
            issue_id=issue_id,
            linked_issue_id=linked_issue_id,
            link_type=link_type,
            created_by=int(actor_user["user_id"]),
        )
