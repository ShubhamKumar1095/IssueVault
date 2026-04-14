"""Security helpers for password hashing and verification."""

from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_password(password: str, salt: str | None = None) -> str:
    """
    Hash password for storage.

    Format: sha256$<salt>$<hex_digest>
    """
    if not salt:
        salt = secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return f"sha256${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Safely verify password against stored hash."""
    if not stored_hash:
        return False

    parts = stored_hash.split("$")
    if len(parts) != 3 or parts[0] != "sha256":
        return False

    _, salt, expected_digest = parts
    check_digest = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return hmac.compare_digest(check_digest, expected_digest)
