# Research: Foundation, Shell & Auth

**Feature**: 001-foundation-shell-auth
**Date**: 2026-06-27
**Status**: Complete — all decisions pre-made in `BLUEPRINT.md`

No open unknowns existed at planning time. This document records the rationale for
each key technical decision so that later phases have a single reference point.

---

## Decision Log

### Password Hashing

**Decision**: Use Python's `hashlib` with PBKDF2-HMAC-SHA256 and a random salt
generated via `secrets.token_bytes()`.

**Rationale**: The Blueprint specifies "securely hashed (salted SHA-256)". PBKDF2-HMAC
adds a per-password iteration cost on top of a simple sha256(salt+password), making
offline brute-force attacks significantly harder with no extra dependency.
`secrets.token_bytes()` is the stdlib's cryptographically secure random source.

**Alternatives considered**:
- `hashlib.sha256(salt + password)`: meets the Blueprint letter but lacks iteration
  stretching; rejected in favour of PBKDF2 for the same stdlib cost.
- `bcrypt` / `argon2-cffi`: stronger, but add a third-party dependency; Constitution
  Principle II prohibits dependencies beyond Python + PySide6 + SQLite.

**How to store**: `password_hash` column stores `salt_hex:hash_hex` as a single
string, both components encoded as hex. `verify_password()` splits on `:`, decodes,
and re-runs PBKDF2 for comparison.

---

### Database Connection Strategy

**Decision**: Each function in `*_db.py` opens its own `sqlite3.connect()`, performs
the operation, and closes the connection (or uses a `with` context manager that commits
and closes automatically).

**Rationale**: Constitution Principle II mandates no connection pooling. Single-user
desktop app with low concurrency makes pooling unnecessary. Short-lived connections
also eliminate the risk of a dangling open connection corrupting the file.

**Alternatives considered**:
- Module-level singleton connection: simpler per-call but risks leaving the connection
  open across calls, complicating the backup operation (which copies the file). Rejected.
- SQLAlchemy session: violates Principle II. Rejected.

---

### Password Storage Format

**Decision**: `auth_db.py` stores and retrieves the full `salt:hash` string as a
single `TEXT` column. There is no separate salt column.

**Rationale**: Combining salt and hash into one field keeps the schema minimal and
avoids a join or multi-column fetch. The format is self-contained and all parsing
happens in `auth.py` — the data layer never needs to understand the encoding.

---

### Default Admin Credentials

**Decision**: Default username `admin`, default password `admin123` — both defined as
constants in `config.py` (`DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`).

**Rationale**: Blueprint says credentials are intentionally simple for a single local
user. A readable constant in `config.py` (never committed with a real secret) satisfies
the "user can change it on first use" pattern. The Change Password dialog is the
designed update path.

---

### Placeholder Page Strategy

**Decision**: Each placeholder page (`dashboard_page.py`, `products_page.py`, etc.) is
a minimal `QWidget` subclass containing a single centered `QLabel` (e.g. "Dashboard —
coming in Phase 5"). No state, no signals, no external imports.

**Rationale**: The placeholder files must exist for `main_window.py` to import them,
but retaining zero functional code makes later full replacement clean — the Phase N
implementer simply overwrites the file rather than untangling placeholder logic from
real logic.

---

### Window Sizing

**Decision**:
- Login Window: fixed size 400×250 (set via `setFixedSize`).
- Main Window: resizable, minimum size 900×600 (set via `setMinimumSize`).

**Rationale**: Directly from Blueprint Section 3.1/3.2 and confirmed by the
Constitution's UI Behavior Constraints section. `setFixedSize` prevents any resize;
`setMinimumSize` allows enlargement while blocking shrinkage below the safe minimum.

---

### Backup Implementation

**Decision**: `database.backup_database()` uses `shutil.copy2(src, dst)` where `src`
is the live `data/store.db` path and `dst` is `data/backups/store_backup_YYYYMMDD_HHMMSS.db`.
`os.makedirs(backups_dir, exist_ok=True)` creates the folder if absent.

**Rationale**: `shutil.copy2` is stdlib, preserves file metadata, and is atomic at
the OS level for a file of this size. Blueprint Section 6 specifies this approach
explicitly. No pre-action confirmation is required (Constitution Confirmation Dialog Policy).

---

### Error Handling Pattern

**Decision**: Critical action handlers (login button click, save in Change Password
dialog, Backup Now) are wrapped in `try/except Exception as e:` blocks. On unexpected
exception: `print(traceback.format_exc())` to console + `QMessageBox.critical(...)` with
a generic user message. Validation errors and expected business-rule failures surface as
specific `QMessageBox.warning(...)` calls before any DB work is attempted.

**Rationale**: Constitution Principle V. The two-tier approach (specific message for
known failures, generic + console log for unexpected) gives the user actionable feedback
without exposing stack traces, while preserving full diagnostic info for the developer.
