# Quickstart & Validation Guide: Foundation, Shell & Auth

**Feature**: 001-foundation-shell-auth
**Date**: 2026-06-27
**Purpose**: Manual testing guide for verifying Phase 1 is complete and correct
before Phase 2 begins. Every checkpoint below MUST pass in a single continuous
session before `/speckit-tasks` is run for Phase 2.

---

## Prerequisites

- Python installed with PySide6 available (`pip install PySide6`).
- All 13 Phase 1 source files implemented per `plan.md` build order.
- No `data/store.db` file exists yet (delete it if present from a prior run to test
  first-launch behaviour).
- Run all commands from the `accounting_system/` project root.

---

## Launch Command

```
python main.py
```

---

## Checkpoint 1 — First-Run Auto-Setup

**Goal**: Verify database and admin account are created on a clean first run.

Steps:
1. Ensure `data/store.db` does NOT exist.
2. Run `python main.py`.
3. The Login Window appears.

Expected:
- `data/store.db` is created automatically (visible in the `data/` folder).
- Console/log output confirms all 6 tables created (or no error).
- Exactly one row exists in `Users` (verify via a SQLite browser or console query).

---

## Checkpoint 2 — Idempotent Seeding

**Goal**: Verify running the app a second time does not duplicate the admin row.

Steps:
1. Close the app from Checkpoint 1.
2. Run `python main.py` again.

Expected:
- Still exactly one row in `Users` — no duplicate insert.

---

## Checkpoint 3 — Auto-Focus on Login Window

**Goal**: Verify Username field receives focus automatically.

Steps:
1. With the Login Window open, without clicking anything, start typing.

Expected:
- Text appears in the Username field (it has focus on open, no click required).

---

## Checkpoint 4 — Failed Login

**Goal**: Verify incorrect credentials are rejected without opening Main Window.

Steps:
1. Enter any wrong username or wrong password (or both).
2. Click Login (or press Enter in the Password field).

Expected:
- An error message is displayed on the Login Window.
- The Main Window does NOT open.
- The app does not crash.

---

## Checkpoint 5 — Enter Key Submits Login

**Goal**: Verify pressing Enter in the Password field triggers login.

Steps:
1. Tab to the Password field (or click it), type the correct password.
2. Press Enter without clicking the Login button.

Expected:
- Login proceeds (success or failure message), same as clicking Login.

---

## Checkpoint 6 — Successful Login

**Goal**: Verify correct credentials open the Main Window on the Dashboard page.

Steps:
1. Enter the default Admin credentials (username: `admin`, password: `admin123` or
   whatever is defined in `config.py`).
2. Click Login.

Expected:
- Main Window opens and displays the Dashboard placeholder page.
- The Login Window closes.

---

## Checkpoint 7 — Sidebar Navigation

**Goal**: Verify all 5 sidebar page buttons work without crashes.

Steps:
1. Click Dashboard, Products, Sales, Purchases, Reports in any order.

Expected:
- Each page area switches correctly.
- No crash or unhandled exception on any page switch.
- Placeholder content (e.g. "Coming soon" label) is visible for each page.

---

## Checkpoint 8 — Window Minimum Size

**Goal**: Verify the Main Window cannot be resized below 900×600.

Steps:
1. Attempt to drag the Main Window to a very small size.

Expected:
- The window stops shrinking at 900×600.
- Layouts do not break at the minimum size.

---

## Checkpoint 9 — Change Password

**Goal**: Verify the full Change Password flow including validation and re-login.

Steps:
1. Click "Change Password" in the sidebar.
2. Enter an **incorrect** current password → click Save.
   - Expected: error message, password unchanged.
3. Enter the correct current password but mismatched new/confirm passwords → Save.
   - Expected: error message, password unchanged.
4. Enter the correct current password, a new valid password (≥ 4 chars), and matching
   confirm → Save.
   - Expected: success message, dialog closes.
5. Click Logout.
6. Attempt login with the **old** password → expected: fails.
7. Login with the **new** password → expected: succeeds.

---

## Checkpoint 10 — Backup Now

**Goal**: Verify a timestamped backup copy is created and confirmed to the user.

Steps:
1. Log in and click "Backup Now" in the sidebar.

Expected:
- No confirmation dialog appears before the action.
- A file named `store_backup_YYYYMMDD_HHMMSS.db` appears under `data/backups/`.
- A success `QMessageBox` shows the backup file path.
- The live `data/store.db` is unchanged and still openable.

---

## Checkpoint 11 — Logout & Re-Login

**Goal**: Verify Logout returns to Login Window without exiting the app.

Steps:
1. While logged in, click Logout.

Expected:
- The Main Window closes.
- The Login Window reappears (app still running).
- Closing the Login Window via its "X" button exits the application entirely.

---

## Checkpoint 12 — Error Handling (Unexpected Exception)

**Goal**: Verify no raw Python traceback ever reaches the user.

Steps:
1. If possible, temporarily introduce a deliberate error (e.g. make `backup_database()`
   raise an exception by pointing to a read-only path), trigger Backup Now.

Expected:
- A friendly `QMessageBox` error message is shown.
- No raw traceback appears in the UI.
- Technical details are printed to the developer console only.

---

## Exit Criteria

All 12 checkpoints above MUST pass before Phase 2 (`/speckit-tasks` for Products)
begins. Any failure is a blocker — Phase 2 MUST NOT start until Phase 1 is demoable
end-to-end with no regressions.
