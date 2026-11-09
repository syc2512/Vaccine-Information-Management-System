"""Password hashing helpers used by authentication and user management."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets


SCHEME = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 600_000


def hash_password(password: str, iterations: int | None = None) -> str:
    if not isinstance(password, str):
        raise TypeError("密码必须是字符串")
    rounds = iterations or int(os.getenv("VACCINE_PASSWORD_ITERATIONS", DEFAULT_ITERATIONS))
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return "$".join(
        [
            SCHEME,
            str(rounds),
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        ]
    )


def is_password_hash(value: object) -> bool:
    return isinstance(value, str) and value.startswith(f"{SCHEME}$") and value.count("$") == 3


def verify_password(password: str, encoded: object) -> bool:
    if not isinstance(password, str) or not is_password_hash(encoded):
        return False
    try:
        _, rounds_text, salt_text, digest_text = encoded.split("$", 3)
        rounds = int(rounds_text)
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return hmac.compare_digest(actual, expected)


def generate_initial_password() -> str:
    return secrets.token_urlsafe(12)


def validate_new_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("密码至少需要 8 个字符")
    if len(password) > 128:
        raise ValueError("密码不能超过 128 个字符")
