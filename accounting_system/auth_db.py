import sqlite3

import database


def get_user(username: str):
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT id, username, password_hash FROM Users WHERE username = ?",
            (username,)
        ).fetchone()
        return row
    finally:
        conn.close()


def count_users() -> int:
    conn = database.get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) FROM Users").fetchone()
        return row[0]
    finally:
        conn.close()


def insert_user(username: str, password_hash: str) -> None:
    conn = database.get_connection()
    try:
        conn.execute(
            "INSERT INTO Users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
    finally:
        conn.close()


def update_password(username: str, new_hash: str) -> None:
    conn = database.get_connection()
    try:
        conn.execute(
            "UPDATE Users SET password_hash = ? WHERE username = ?",
            (new_hash, username)
        )
        conn.commit()
    finally:
        conn.close()
