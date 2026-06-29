# Feature Specification: Foundation, Shell & Auth

**Feature Branch**: `001-foundation-shell-auth`

**Created**: 2026-06-27

**Status**: Draft

**Input**: Phase 1 of the Store Accounting System Implementation Plan — establish the
full technical foundation, application shell, and authentication layer so every later
phase only adds page content without touching plumbing.

---

## User Scenarios & Testing

### User Story 1 — First Launch & Auto-Setup (Priority: P1)

When the application is run for the first time on a fresh machine (no `data/store.db`
exists), it self-initialises: the database file and all tables are created
automatically, and a single default Admin account is seeded — all without any action
from the user.

**Why this priority**: Nothing else in the application can function until the database
exists and has a valid admin row. This is the absolute prerequisite for every other
user story in every phase.

**Independent Test**: Delete `data/store.db`, run `main.py`, and confirm the file is
re-created, all tables exist, and exactly one row is present in the `Users` table —
without logging in or clicking anything.

**Acceptance Scenarios**:

1. **Given** no `data/store.db` file exists, **When** `main.py` is executed,
   **Then** `data/store.db` is created automatically and all six tables
   (`Users`, `Products`, `Sales`, `SaleItems`, `Purchases`, `PurchaseItems`) exist
   with the correct schema.
2. **Given** the database was just created, **When** the application starts,
   **Then** exactly one row exists in `Users` (the default Admin account with a
   securely hashed password).
3. **Given** the application has been run before (database already exists with an Admin
   row), **When** `main.py` is executed again, **Then** no additional row is inserted
   into `Users` — the seed operation is idempotent.

---

### User Story 2 — Login & Logout (Priority: P1)

The Admin user authenticates via a Login Window before accessing any part of the
application. Incorrect credentials are rejected with a visible error. After working,
the user can log out and return to the Login Window without closing the application.

**Why this priority**: All application features sit behind the login gate. Without a
working login/logout cycle, no phase can be manually tested end-to-end.

**Independent Test**: Launch the app, attempt login with wrong credentials (error
shown, no navigation), then log in with the correct default credentials (Main Window
opens), then click Logout (Main Window closes, Login Window reappears). All steps pass
with no crashes.

**Acceptance Scenarios**:

1. **Given** the Login Window is open, **When** it appears, **Then** the Username
   field has keyboard focus automatically — no click required.
2. **Given** the Login Window is open, **When** the user presses Enter in the Password
   field, **Then** login is attempted (same as clicking the Login button).
3. **Given** the user submits an incorrect username or password, **When** the Login
   button is clicked (or Enter pressed), **Then** an error message is shown on the
   Login Window and the Main Window does not open.
4. **Given** the user submits the correct Admin credentials, **When** the Login button
   is clicked, **Then** the Main Window opens showing the Dashboard page, and the
   Login Window closes.
5. **Given** the user is on any page of the Main Window, **When** Logout is clicked,
   **Then** the Main Window closes and the Login Window reappears — the application
   does not exit.
6. **Given** the Login Window is visible, **When** the user closes it via the window's
   "X" button, **Then** the entire application exits.

---

### User Story 3 — Main Window Shell & Navigation (Priority: P1)

After login, the user sees a Main Window with a sidebar that lets them navigate between
five pages (Dashboard, Products, Sales, Purchases, Reports). In Phase 1, pages other
than the Change Password dialog show placeholder content; the shell itself is fully
functional.

**Why this priority**: The shell is the container that every later phase fills in. It
must be solid and navigable from the start.

**Independent Test**: Log in, then click each sidebar button and confirm the correct
page area becomes visible with no crash. Resize the window to confirm it cannot be
made smaller than the defined minimum, but can be maximized.

**Acceptance Scenarios**:

1. **Given** the user is logged in, **When** any sidebar navigation button is clicked,
   **Then** the corresponding page area is displayed and no crash occurs.
2. **Given** the Main Window is open, **When** the user attempts to resize it below
   the defined minimum dimensions, **Then** the window stops shrinking at that
   minimum and does not break any layout.
3. **Given** the Main Window is open, **When** the Backup Now sidebar action is
   triggered, **Then** a timestamped copy of the database file is created in the
   backups folder and a confirmation message shows the backup file path — no
   navigation occurs and no pre-action confirmation dialog is shown.

---

### User Story 4 — Change Password (Priority: P2)

The Admin user can change their account password at any time via a modal dialog
reachable from the sidebar. The dialog enforces the current password before accepting
a new one, and the new login session must use the updated password.

**Why this priority**: This is account security maintenance. It depends on the login
flow (US2) and the shell (US3) already working, but is otherwise self-contained and
important to validate before any later phase is built on top.

**Independent Test**: Open Change Password, submit a wrong current password (rejected),
then submit the correct current password with a valid new password (accepted). Log out
and log back in with the new password — succeeds.

**Acceptance Scenarios**:

1. **Given** the Change Password dialog is open, **When** the user submits an
   incorrect current password, **Then** the dialog shows an error and the password
   is not changed.
2. **Given** the Change Password dialog is open, **When** the new password and the
   confirm-password fields do not match, **Then** the dialog shows an error and the
   password is not changed.
3. **Given** the Change Password dialog is open, **When** the new password is too
   short (below the minimum length), **Then** the dialog shows an error and the
   password is not changed.
4. **Given** the user submits a correct current password and a valid, matching new
   password, **When** Save is clicked, **Then** a success message is shown and the
   dialog closes.
5. **Given** the password was changed successfully, **When** the user logs out and
   attempts to log in with the old password, **Then** login fails; logging in with
   the new password succeeds.

---

### Edge Cases

- What happens when `data/` directory does not exist at first run? The app must create
  it automatically (along with `store.db`) — no manual folder creation required from
  the user.
- What happens if the `data/backups/` folder does not exist when Backup Now is
  triggered? The folder is created automatically on first backup.
- What happens if a disk error (e.g. full disk, permissions) occurs during backup? A
  friendly error message is shown; the live database is never touched or corrupted.
- What happens if an unexpected exception occurs during login or backup? A top-level
  handler catches it, logs the detail to console, and shows the user a generic friendly
  message — the application does not crash.

---

## Requirements

### Functional Requirements

- **FR-001**: The system MUST automatically create the `data/store.db` file and all
  required database tables on first run if they do not already exist.
- **FR-002**: The system MUST seed exactly one default Admin account on first run;
  re-running MUST NOT create duplicate admin rows.
- **FR-003**: The admin password MUST be stored as a securely hashed value (salted
  SHA-256); the plaintext password MUST never be persisted.
- **FR-004**: The Login Window MUST reject empty or non-matching credentials with a
  visible error message on the same window.
- **FR-005**: The Login Window MUST auto-focus the Username field on open, and MUST
  submit login when Enter is pressed in the Password field.
- **FR-006**: On successful login, the Main Window MUST open displaying the Dashboard
  area, and the Login Window MUST close.
- **FR-007**: The Logout action MUST close the Main Window and reopen the Login Window
  without exiting the application.
- **FR-008**: Closing the Login Window via its "X" button MUST exit the application.
- **FR-009**: The Main Window MUST contain a sidebar with navigation to Dashboard,
  Products, Sales, Purchases, and Reports pages, plus Change Password, Backup Now, and
  Logout actions.
- **FR-010**: The Main Window MUST be resizable with a minimum size enforced; shrinking
  below the minimum MUST be blocked.
- **FR-011**: In Phase 1, pages for Dashboard, Products, Sales, Purchases, and Reports
  MUST exist as placeholder widgets — visible and crash-free when navigated to, but
  without real content.
- **FR-012**: The Backup Now action MUST copy the live database file to a
  timestamped backup file in the backups folder, creating the folder if needed, and
  MUST show a result message (path on success, error on failure) — with no
  pre-action confirmation dialog.
- **FR-013**: The Change Password dialog MUST verify the current password before
  accepting a new one, enforce a minimum new-password length, and require the
  new password and confirm-password fields to match.
- **FR-014**: All database SQL MUST use parameterized queries; string-formatted or
  concatenated SQL is never permitted.
- **FR-015**: Every unexpected exception in critical actions (login, backup, change
  password) MUST be caught by a top-level handler, logged to console, and shown to the
  user as a friendly message — a raw traceback MUST never reach the user.

### Key Entities

- **Users**: Single-row table — stores the Admin account's username and hashed
  password. The row identity never changes; only the `password_hash` column is ever
  updated (via Change Password).
- **Database file** (`data/store.db`): The SQLite file housing all six tables. Created
  at startup; backed up on demand.
- **Backup file**: A timestamped copy of `store.db` written to `data/backups/` — read-
  only artifact, never modified by the app after creation.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: On first launch, the application reaches the Login Window in under
  3 seconds with all tables created and the admin account seeded — with no user
  intervention beyond running the app.
- **SC-002**: An incorrect login attempt is rejected and an error is displayed within
  1 second, without opening the Main Window.
- **SC-003**: A correct login attempt opens the Main Window within 1 second.
- **SC-004**: Switching between all 5 sidebar pages produces no errors or visual
  glitches, at both minimum and maximum tested window sizes.
- **SC-005**: A password change round-trip (change → logout → login with new password)
  completes successfully with every validation rule exercised at least once.
- **SC-006**: Backup Now produces a valid, readable copy of the database within
  2 seconds and shows the backup file path in the confirmation message.
- **SC-007**: All 10 manual testing checkpoints defined in the Implementation Plan for
  Phase 1 pass in a single continuous test session.

---

## Assumptions

- The default Admin credentials (username and initial password) are defined as
  constants in `config.py`; the initial password is intentionally simple since this
  is a single-user local app (the user is expected to change it on first use, but is
  not forced to).
- The minimum new-password length is 4 characters, consistent with the Blueprint's
  rationale for a single local user.
- The Main Window minimum size is 900×600 pixels; the Login Window is fixed at
  400×250 pixels — both defined as constants in `config.py`.
- No network connectivity is required or used at any point in this phase.
- All five placeholder pages are minimal widgets (e.g. a `QLabel` saying "Coming soon"
  or similar) — they will be completely replaced in later phases with no shared code
  from the placeholder retained.
- The `data/` directory will be located relative to the application's root directory,
  not the user's home directory or any OS-specific app-data folder.
- The backup operation uses Python's standard `shutil.copy2` — no third-party library
  is required.
- There is no session timeout, login throttle, or account lockout — appropriate for a
  single-user local desktop application.
