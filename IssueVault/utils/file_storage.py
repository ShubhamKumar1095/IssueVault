"""Local file storage helper for issue attachments."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import uuid
from typing import Any

from config import get_settings


def _safe_filename(name: str) -> str:
    """Sanitize filename while preserving extension."""
    clean = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("._")
    return clean or "attachment.bin"


def get_issue_upload_dir(issue_id: int) -> Path:
    """Return and create issue-specific upload folder path."""
    settings = get_settings()
    root = Path(settings.upload_dir)
    folder = root / f"issue_{issue_id}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_attachment(file_obj: Any, issue_id: int) -> dict[str, object]:
    """
    Save uploaded file to local disk.

    Returns metadata needed by attachment repository.
    """
    issue_dir = get_issue_upload_dir(issue_id)
    original_name = getattr(file_obj, "name", "upload.bin")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = uuid.uuid4().hex[:8]
    stored_name = f"{timestamp}_{suffix}_{_safe_filename(original_name)}"
    file_path = issue_dir / stored_name

    with open(file_path, "wb") as out_file:
        out_file.write(file_obj.getbuffer())

    return {
        "original_filename": original_name,
        "stored_filename": stored_name,
        "file_path": str(file_path).replace("\\", "/"),
        "file_size_bytes": int(getattr(file_obj, "size", file_path.stat().st_size)),
        "content_type": getattr(file_obj, "type", None),
    }
