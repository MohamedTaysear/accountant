import hashlib
import hmac
import secrets

import auth_db
import config


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(32)
    dk   = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260000)
    return salt.hex() + ":" + dk.hex()


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split(":", 1)
        salt     = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        dk       = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260000)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def seed_default_admin() -> None:
    if auth_db.count_users() == 0:
        auth_db.insert_user(
            config.DEFAULT_ADMIN_USERNAME,
            hash_password(config.DEFAULT_ADMIN_PASSWORD)
        )


def check_login(username: str, password: str) -> bool:
    username = username.strip()
    password = password.strip()
    if not username or not password:
        return False
    user = auth_db.get_user(username)
    if user is None:
        return False
    return verify_password(password, user["password_hash"])


def change_password(
    username: str,
    current_password: str,
    new_password: str,
    confirm_password: str
) -> tuple:
    if not check_login(username, current_password):
        return (False, "Current password is incorrect.")
    if not new_password.strip():
        return (False, "New password cannot be empty.")
    if len(new_password) < config.MIN_PASSWORD_LENGTH:
        return (False, f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters.")
    if new_password != confirm_password:
        return (False, "New password and confirmation do not match.")
    auth_db.update_password(username, hash_password(new_password))
    return (True, "")
