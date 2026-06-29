---
description: "Task list for Phase 1 — Foundation, Shell & Auth"
---

# Tasks: Foundation, Shell & Auth

**Input**: Design documents from `specs/001-foundation-shell-auth/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | data-model.md ✅ | research.md ✅ | quickstart.md ✅

**Tests**: Not requested — no test tasks generated.

**Organization**: Tasks follow the strict bottom-up build order from plan.md. Each
task is written so that an implementer can complete it with only this file,
`data-model.md`, and `plan.md` as context — no additional decisions are required.

**Project root**: `accounting_system/` (all file paths below are relative to it)

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (touches different files, no cross-task dependency)
- **[Story]**: Which user story this task belongs to (US1–US4 from spec.md)
- Every task includes the exact target file path

---

## Phase 1: Setup

**Purpose**: Create the directory skeleton and the one file every other file depends on.

- [x] T001 Create the project directory structure: `accounting_system/` at the repo
  root containing `ui/`, `logic/`, `data/` subdirectories and empty `ui/__init__.py`,
  `logic/__init__.py` files. Do NOT create `data/store.db` — it is generated at runtime.

- [x] T002 Create `config.py` with all app-wide constants:
  ```python
  # config.py
  import os

  # Paths (relative to project root — resolve from this file's location)
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  DATA_DIR = os.path.join(BASE_DIR, "data")
  DB_PATH  = os.path.join(DATA_DIR, "store.db")
  BACKUPS_DIR = os.path.join(DATA_DIR, "backups")

  # Window sizes
  LOGIN_WINDOW_WIDTH  = 400
  LOGIN_WINDOW_HEIGHT = 250
  MAIN_WINDOW_MIN_WIDTH  = 900
  MAIN_WINDOW_MIN_HEIGHT = 600

  # App info
  APP_NAME = "Store Accounting System"

  # Default admin credentials (user should change on first run)
  DEFAULT_ADMIN_USERNAME = "admin"
  DEFAULT_ADMIN_PASSWORD = "admin123"

  # Password policy
  MIN_PASSWORD_LENGTH = 4
  ```
  This file has NO imports from the project — only `os` from the standard library.

---

## Phase 2: Foundation (Blocking Prerequisites)

**Purpose**: Database layer and auth logic — MUST be complete before any UI work.

**⚠️ CRITICAL**: No UI file can be started until T003–T007 are all complete.

- [x] T003 Create `database.py`. Implement three functions:

  **`get_connection() -> sqlite3.Connection`**
  - Opens and returns a new `sqlite3.connect(config.DB_PATH)` connection.
  - Calls `conn.row_factory = sqlite3.Row` so rows can be accessed by column name.
  - Creates `config.DATA_DIR` with `os.makedirs(config.DATA_DIR, exist_ok=True)`
    before connecting, so the folder is never missing.
  - Returns the open connection. Caller is responsible for commit/close.

  **`initialize_database() -> None`**
  - Calls `get_connection()`, then runs `CREATE TABLE IF NOT EXISTS` for all 6 tables
    in this exact order (to satisfy foreign key declaration order):
    1. `Users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)`
    2. `Products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, sku TEXT UNIQUE, unit TEXT NOT NULL DEFAULT 'pcs', purchase_price REAL NOT NULL DEFAULT 0, selling_price REAL NOT NULL DEFAULT 0, stock_quantity REAL NOT NULL DEFAULT 0, reorder_level REAL NOT NULL DEFAULT 5, is_active INTEGER NOT NULL DEFAULT 1)`
    3. `Sales (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_number TEXT UNIQUE NOT NULL, customer_name TEXT, discount_amount REAL NOT NULL DEFAULT 0, total_amount REAL NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'active', created_at TEXT DEFAULT CURRENT_TIMESTAMP)`
    4. `SaleItems (id INTEGER PRIMARY KEY AUTOINCREMENT, sale_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity REAL NOT NULL, unit_price REAL NOT NULL, purchase_price_at_sale REAL NOT NULL, subtotal REAL NOT NULL, FOREIGN KEY (sale_id) REFERENCES Sales(id), FOREIGN KEY (product_id) REFERENCES Products(id))`
    5. `Purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_number TEXT UNIQUE NOT NULL, supplier_name TEXT, total_amount REAL NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'active', created_at TEXT DEFAULT CURRENT_TIMESTAMP)`
    6. `PurchaseItems (id INTEGER PRIMARY KEY AUTOINCREMENT, purchase_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity REAL NOT NULL, unit_price REAL NOT NULL, subtotal REAL NOT NULL, FOREIGN KEY (purchase_id) REFERENCES Purchases(id), FOREIGN KEY (product_id) REFERENCES Products(id))`
  - Commits and closes the connection.

  **`backup_database() -> str`**
  - Creates `config.BACKUPS_DIR` with `os.makedirs(config.BACKUPS_DIR, exist_ok=True)`.
  - Generates filename: `store_backup_` + `datetime.now().strftime("%Y%m%d_%H%M%S")` + `.db`.
  - Copies `config.DB_PATH` to that filename using `shutil.copy2(src, dst)`.
  - Returns the full destination path as a string.
  - Does NOT catch exceptions — the caller wraps this in try/except.

  Imports needed: `sqlite3`, `os`, `shutil`, `datetime`, `config`.

- [x] T004 Create `auth_db.py`. Implement four functions — all use parameterized SQL,
  all open their own connection via `database.get_connection()` and close it when done:

  **`get_user(username: str) -> sqlite3.Row | None`**
  - `SELECT id, username, password_hash FROM Users WHERE username = ?`
  - Returns the single row or `None` if not found.

  **`count_users() -> int`**
  - `SELECT COUNT(*) FROM Users`
  - Returns the integer count.

  **`insert_user(username: str, password_hash: str) -> None`**
  - `INSERT INTO Users (username, password_hash) VALUES (?, ?)`
  - Commits.

  **`update_password(username: str, new_hash: str) -> None`**
  - `UPDATE Users SET password_hash = ? WHERE username = ?`
  - Commits.

  Imports needed: `sqlite3`, `database`.

- [x] T005 Create `auth.py`. Implement five functions. No PySide6 imports — this is
  pure logic/stdlib only:

  **`hash_password(password: str) -> str`**
  - Generates a 32-byte random salt: `salt = secrets.token_bytes(32)`.
  - Derives hash: `dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 260000)`.
  - Returns `salt.hex() + ':' + dk.hex()` as a single string.

  **`verify_password(password: str, stored_hash: str) -> bool`**
  - Splits `stored_hash` on `':'` → `salt_hex, hash_hex`.
  - Decodes: `salt = bytes.fromhex(salt_hex)`, `expected = bytes.fromhex(hash_hex)`.
  - Re-derives: `dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 260000)`.
  - Returns `hmac.compare_digest(dk, expected)` (timing-safe comparison).
  - Returns `False` on any exception (malformed stored_hash).

  **`seed_default_admin() -> None`**
  - If `auth_db.count_users() == 0`: calls
    `auth_db.insert_user(config.DEFAULT_ADMIN_USERNAME, hash_password(config.DEFAULT_ADMIN_PASSWORD))`.
  - Otherwise: does nothing (idempotent).

  **`check_login(username: str, password: str) -> bool`**
  - Trims `username` and `password`.
  - If either is empty: returns `False`.
  - Fetches row: `user = auth_db.get_user(username)`.
  - If `user is None`: returns `False`.
  - Returns `verify_password(password, user['password_hash'])`.

  **`change_password(username: str, current_password: str, new_password: str, confirm_password: str) -> tuple[bool, str]`**
  - Returns `(False, "Current password is incorrect.")` if `check_login(username, current_password)` is False.
  - Returns `(False, "New password cannot be empty.")` if `new_password.strip() == ""`.
  - Returns `(False, f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters.")` if `len(new_password) < config.MIN_PASSWORD_LENGTH`.
  - Returns `(False, "New password and confirmation do not match.")` if `new_password != confirm_password`.
  - Otherwise: calls `auth_db.update_password(username, hash_password(new_password))` and returns `(True, "")`.

  Imports needed: `hashlib`, `hmac`, `secrets`, `config`, `auth_db`.

**Checkpoint**: Foundation ready — run a quick sanity check: `python -c "import database; database.initialize_database(); print('OK')"` must print `OK` with no errors before proceeding.

---

## Phase 3: User Story 1 — First Launch & Auto-Setup (Priority: P1)

**Goal**: Running `main.py` on a clean machine creates `data/store.db`, all 6 tables,
and one Admin row — automatically, with no user action.

**Independent Test** (quickstart.md Checkpoints 1 & 2):
Delete `data/store.db`, run `python main.py`, verify the file exists with 1 row in
`Users`. Run again, verify still 1 row (idempotent).

- [x] T006 [US1] Create `main.py` — the application entry point:
  ```python
  import sys
  import traceback
  from PySide6.QtWidgets import QApplication, QMessageBox
  import database
  import auth
  from ui.login_window import LoginWindow

  def main():
      app = QApplication(sys.argv)
      app.setApplicationName("Store Accounting System")

      try:
          database.initialize_database()
          auth.seed_default_admin()
      except Exception as e:
          print(traceback.format_exc())
          QMessageBox.critical(None, "Startup Error",
              "Failed to initialize the database.\n\nThe application will now exit.")
          sys.exit(1)

      window = LoginWindow()
      window.show()
      sys.exit(app.exec())

  if __name__ == "__main__":
      main()
  ```

**Checkpoint (US1)**: `python main.py` → Login Window appears, `data/store.db` exists,
`Users` table has exactly 1 row. Second run → still 1 row.

---

## Phase 4: User Story 2 — Login & Logout (Priority: P1)

**Goal**: Admin can authenticate via Login Window; incorrect credentials are rejected;
logout returns to Login Window without exiting the app.

**Independent Test** (quickstart.md Checkpoints 3–6 and 11):
Wrong credentials → error shown, no navigation. Correct credentials → Main Window opens.
Logout → Login Window reappears. Closing Login Window "X" → app exits.

*Implement in order — each file depends on the previous one being complete.*

- [x] T007 [US2] Create all 5 placeholder page widgets. Each file follows the same
  minimal pattern — just swap the class name and label text:

  **`ui/dashboard_page.py`**:
  ```python
  from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
  from PySide6.QtCore import Qt

  class DashboardPage(QWidget):
      def __init__(self, parent=None):
          super().__init__(parent)
          layout = QVBoxLayout(self)
          label = QLabel("Dashboard — coming in Phase 5")
          label.setAlignment(Qt.AlignCenter)
          layout.addWidget(label)
  ```

  Create four more files with the same pattern:
  - `ui/products_page.py` → class `ProductsPage`, label `"Products — coming in Phase 2"`
  - `ui/sales_page.py` → class `SalesPage`, label `"Sales — coming in Phase 4"`
  - `ui/purchases_page.py` → class `PurchasesPage`, label `"Purchases — coming in Phase 3"`
  - `ui/reports_page.py` → class `ReportsPage`, label `"Reports — coming in Phase 5"`

- [x] T008 [US2] Create `ui/change_password_dialog.py` — modal dialog for changing
  the admin password. The dialog stores the current username passed in from the caller.

  **Constructor `__init__(self, username: str, parent=None)`**:
  - Calls `super().__init__(parent)` with `Qt.Dialog` window flag.
  - Sets window title to `"Change Password"`.
  - Sets `self.username = username`.
  - Creates three `QLineEdit` fields, all with `setEchoMode(QLineEdit.Password)`:
    - `self.current_password_input`
    - `self.new_password_input`
    - `self.confirm_password_input`
  - Creates `self.save_btn = QPushButton("Save")` and `self.cancel_btn = QPushButton("Cancel")`.
  - Layout: `QFormLayout` with rows labelled "Current Password:", "New Password:",
    "Confirm New Password:"; below it a `QHBoxLayout` with Cancel then Save buttons.
  - Connects `self.save_btn.clicked` → `self._on_save`.
  - Connects `self.cancel_btn.clicked` → `self.reject`.
  - Sets `setFixedWidth(360)`.

  **`_on_save(self)`**:
  ```python
  import traceback
  from PySide6.QtWidgets import QMessageBox
  import auth

  def _on_save(self):
      current  = self.current_password_input.text()
      new_pw   = self.new_password_input.text()
      confirm  = self.confirm_password_input.text()
      try:
          success, message = auth.change_password(self.username, current, new_pw, confirm)
          if success:
              QMessageBox.information(self, "Success", "Password changed successfully.")
              self.accept()
          else:
              QMessageBox.warning(self, "Error", message)
      except Exception as e:
          print(traceback.format_exc())
          QMessageBox.critical(self, "Unexpected Error",
              "An unexpected error occurred. Please try again.")
  ```

  Imports needed at top of file: `from PySide6.QtWidgets import (QDialog, QLineEdit,
  QPushButton, QFormLayout, QHBoxLayout, QVBoxLayout, QMessageBox)`,
  `from PySide6.QtCore import Qt`, `import traceback`, `import auth`.

- [x] T009 [US2] Create `ui/main_window.py` — the main application shell.

  **Class `MainWindow(QMainWindow)`**:

  **Constructor `__init__(self, username: str, parent=None)`**:
  - Calls `super().__init__(parent)`.
  - `self.username = username` — stored for passing to Change Password dialog.
  - Sets window title to `config.APP_NAME`.
  - Sets minimum size: `self.setMinimumSize(config.MAIN_WINDOW_MIN_WIDTH, config.MAIN_WINDOW_MIN_HEIGHT)`.
  - Calls `self._build_ui()`.

  **`_build_ui(self)`**:
  - Creates a `QWidget` as central widget with a `QHBoxLayout`.
  - **Left sidebar** (`QWidget` with `QVBoxLayout`, fixed width 180px):
    - Navigation buttons (top group, `QVBoxLayout`):
      - `QPushButton("Dashboard")` → connects to `lambda: self._switch_page(0)`
      - `QPushButton("Products")` → connects to `lambda: self._switch_page(1)`
      - `QPushButton("Sales")` → connects to `lambda: self._switch_page(2)`
      - `QPushButton("Purchases")` → connects to `lambda: self._switch_page(3)`
      - `QPushButton("Reports")` → connects to `lambda: self._switch_page(4)`
    - Add `layout.addStretch()` to push the next group to the bottom.
    - Action buttons (bottom group, `QVBoxLayout`):
      - `QPushButton("Change Password")` → connects to `self._on_change_password`
      - `QPushButton("Backup Now")` → connects to `self._on_backup`
      - `QPushButton("Logout")` → connects to `self._on_logout`
  - **Right content area** (`QStackedWidget` named `self.stack`):
    - `self.stack.addWidget(DashboardPage())`   # index 0
    - `self.stack.addWidget(ProductsPage())`    # index 1
    - `self.stack.addWidget(SalesPage())`       # index 2
    - `self.stack.addWidget(PurchasesPage())`   # index 3
    - `self.stack.addWidget(ReportsPage())`     # index 4
  - Sidebar and stack share the horizontal layout; sidebar has a fixed width.

  **`_switch_page(self, index: int)`**:
  - `self.stack.setCurrentIndex(index)`

  **`_on_change_password(self)`**:
  ```python
  from ui.change_password_dialog import ChangePasswordDialog
  dlg = ChangePasswordDialog(self.username, self)
  dlg.exec()
  ```

  **`_on_backup(self)`**:
  ```python
  import traceback
  from PySide6.QtWidgets import QApplication, QMessageBox
  from PySide6.QtCore import Qt
  import database

  def _on_backup(self):
      QApplication.setOverrideCursor(Qt.WaitCursor)
      try:
          backup_path = database.backup_database()
          QApplication.restoreOverrideCursor()
          QMessageBox.information(self, "Backup Complete",
              f"Database backed up to:\n{backup_path}")
      except Exception as e:
          QApplication.restoreOverrideCursor()
          print(traceback.format_exc())
          QMessageBox.critical(self, "Backup Failed",
              "An error occurred during backup. Please check disk space and permissions.")
  ```

  **`_on_logout(self)`**:
  - Emits a custom signal `logged_out = Signal()` (declared at class level:
    `from PySide6.QtCore import Signal`).
  - Then calls `self.close()`.

  Imports needed at top of file:
  ```python
  import traceback
  from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
      QStackedWidget, QPushButton, QApplication, QMessageBox)
  from PySide6.QtCore import Qt, Signal
  import config
  import database
  from ui.dashboard_page  import DashboardPage
  from ui.products_page   import ProductsPage
  from ui.sales_page      import SalesPage
  from ui.purchases_page  import PurchasesPage
  from ui.reports_page    import ReportsPage
  ```

- [x] T010 [US2] Create `ui/login_window.py` — the login screen.

  **Class `LoginWindow(QWidget)`**:

  **Constructor `__init__(self, parent=None)`**:
  - Calls `super().__init__(parent)`.
  - Sets window title to `config.APP_NAME`.
  - Sets fixed size: `self.setFixedSize(config.LOGIN_WINDOW_WIDTH, config.LOGIN_WINDOW_HEIGHT)`.
  - Sets `self.main_window = None` (will be assigned on successful login).
  - Calls `self._build_ui()`.

  **`_build_ui(self)`**:
  - Outer `QVBoxLayout` with `setAlignment(Qt.AlignCenter)`.
  - App title label: `QLabel(config.APP_NAME)` with font size 16, bold, centred.
  - `self.username_input = QLineEdit()` with placeholder `"Username"`.
  - `self.password_input = QLineEdit()` with placeholder `"Password"` and
    `setEchoMode(QLineEdit.Password)`.
  - `self.login_btn = QPushButton("Login")`.
  - `self.error_label = QLabel("")` with red text colour and hidden by default
    (`self.error_label.hide()`).
  - Layout order (top to bottom, centred, with small spacing): title, username field,
    password field, login button, error label.
  - Connect `self.login_btn.clicked` → `self._on_login`.
  - Connect `self.password_input.returnPressed` → `self._on_login`.
  - After layout is built: `self.username_input.setFocus()`.

  **`_on_login(self)`**:
  ```python
  import traceback
  import auth

  def _on_login(self):
      username = self.username_input.text().strip()
      password = self.password_input.text()
      self.error_label.hide()
      try:
          if auth.check_login(username, password):
              self._open_main_window(username)
          else:
              self.error_label.setText("Invalid username or password.")
              self.error_label.show()
              self.password_input.clear()
      except Exception as e:
          print(traceback.format_exc())
          self.error_label.setText("An unexpected error occurred. Please try again.")
          self.error_label.show()
  ```

  **`_open_main_window(self, username: str)`**:
  ```python
  from ui.main_window import MainWindow

  def _open_main_window(self, username: str):
      self.main_window = MainWindow(username)
      self.main_window.logged_out.connect(self._on_logged_out)
      self.main_window.show()
      self.hide()
  ```

  **`_on_logged_out(self)`**:
  ```python
  def _on_logged_out(self):
      self.username_input.clear()
      self.password_input.clear()
      self.error_label.hide()
      self.username_input.setFocus()
      self.show()
  ```

  Imports needed at top of file:
  ```python
  import traceback
  from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
  from PySide6.QtCore import Qt
  from PySide6.QtGui import QFont, QColor
  import config
  import auth
  ```

**Checkpoint (US2)**: `python main.py` → Login Window appears with Username focused.
Wrong credentials → error shown. Correct credentials → Main Window opens on Dashboard.
Logout → Login Window reappears. "X" on Login Window → app exits.

---

## Phase 5: User Story 3 — Main Window Shell & Navigation (Priority: P1)

**Goal**: The sidebar switches between all 5 pages, the window has enforced minimum
size, and Backup Now creates a timestamped backup file.

**Independent Test** (quickstart.md Checkpoints 7, 8, 10):
Click each sidebar button → correct placeholder visible, no crash.
Drag window below min size → stops at 900×600.
Click Backup Now → file appears in `data/backups/`, success message shown.

*T009 (main_window.py) already implements all of US3. No additional files to create.*
*Verify the three checkpoints above pass with the code written in T009.*

- [ ] T011 [US3] Verify main_window.py navigation and backup behaviour by running
  through quickstart.md Checkpoints 7, 8, and 10 manually. Confirm:
  - Each of the 5 sidebar nav buttons switches the `QStackedWidget` page.
  - Window cannot be dragged below 900×600.
  - Backup Now creates `data/backups/store_backup_YYYYMMDD_HHMMSS.db` and shows the
    path in the confirmation message box.
  - If any of these fail, fix the relevant code in `ui/main_window.py` before continuing.

**Checkpoint (US3)**: Checkpoints 7, 8, and 10 from quickstart.md all pass.

---

## Phase 6: User Story 4 — Change Password (Priority: P2)

**Goal**: Admin can change their password; the dialog enforces all validation rules;
the new password works on the next login.

**Independent Test** (quickstart.md Checkpoint 9):
Wrong current password → rejected. Mismatched new/confirm → rejected. Too short →
rejected. Valid submission → success, logout, re-login with new password succeeds.

*T008 (change_password_dialog.py) already implements US4. No additional files to create.*
*Verify the checkpoint passes with the code written in T008.*

- [ ] T012 [US4] Verify change_password_dialog.py by running through quickstart.md
  Checkpoint 9 manually. Confirm:
  - Incorrect current password → error message, dialog stays open.
  - Mismatched new/confirm → error message, dialog stays open.
  - New password shorter than 4 chars → error message, dialog stays open.
  - Valid submission → success message, dialog closes.
  - Logout then login with new password → succeeds.
  - Login with old password after change → fails.
  - If any of these fail, fix the relevant code in `ui/change_password_dialog.py`.

**Checkpoint (US4)**: Checkpoint 9 from quickstart.md passes completely.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation pass ensuring every cross-cutting requirement is met.

- [x] T013 [P] Verify layering compliance across all Phase 1 files. Open each file and
  confirm:
  - No `ui/*.py` file imports `sqlite3` directly (exception: none in this phase).
  - No `ui/*.py` file imports `database.py` directly, EXCEPT `main_window.py` which
    imports `database.backup_database()` — this is the one documented exception.
  - `auth.py` has zero PySide6 imports.
  - `auth_db.py` has zero business logic — only SQL queries.
  - Fix any violation found before marking this task complete.

- [x] T014 [P] Verify error handling compliance. For each of the three critical actions
  below, confirm a `try/except Exception` block wraps the operation and shows a
  `QMessageBox` (never a raw traceback) on failure:
  - Login button handler (`login_window.py → _on_login`)
  - Save button handler (`change_password_dialog.py → _on_save`)
  - Backup Now handler (`main_window.py → _on_backup`)
  Fix any missing handler before marking complete.

- [x] T015 [P] Verify auto-focus behaviour:
  - Login Window: `username_input.setFocus()` is called after the layout is built in
    `_build_ui()`.
  - Confirm that when `_on_logged_out()` is called, `username_input.setFocus()` is
    also called to restore focus for the next login attempt.
  Fix in `login_window.py` if missing.

- [ ] T016 Run the complete Phase 1 manual testing checklist from `quickstart.md`
  (Checkpoints 1–12) in a single continuous session. Mark each checkpoint as passed.
  Do NOT mark T016 complete until every checkpoint passes. Any failure is a bug —
  fix it and re-run from the top.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1 — T001–T002)**: No dependencies. Start immediately.
- **Foundation (Phase 2 — T003–T005)**: Depends on T002 (`config.py`). BLOCKS all UI work.
- **US1 (Phase 3 — T006)**: Depends on T003, T004, T005.
- **US2 (Phase 4 — T007–T010)**: Depends on T003, T004, T005. Can start alongside T006.
- **US3 (Phase 5 — T011)**: Depends on T009 (main_window.py, which is T009 in Phase 4).
- **US4 (Phase 6 — T012)**: Depends on T008 (change_password_dialog.py).
- **Polish (Phase 7 — T013–T016)**: Depends on all prior phases complete.

### Within Phase 4 (US2) — Strict Order

T007 → T008 → T009 → T010

Explanation:
- T007 (placeholder pages) must exist before T009 (main_window.py) can import them.
- T008 (change_password_dialog.py) must exist before T009 can open it.
- T009 (main_window.py) must exist before T010 (login_window.py) can import it.
- T010 (login_window.py) must exist before T006's `main.py` can import it.
  *(T006 should be written after T010 even though it's in an earlier phase — or
  reorder: do T007→T008→T009→T010 before finalising T006.)*

### Parallel Opportunities

```
# Phase 1 — these two can overlap (different files):
T001  (directory structure)
T002  (config.py) — can start as soon as T001 creates the directory

# Phase 2 — strictly sequential (each imports the previous):
T003 → T004 → T005

# Phase 3 and 4 can overlap once T005 is done:
T006  (main.py)          # writes the entry point, no UI imports yet needed
T007  (placeholder pages) # in parallel with T006 — different files

# T008, T009, T010 must be sequential after T007
T007 → T008 → T009 → T010

# Polish tasks T013, T014, T015 can run in parallel:
T013  T014  T015  (all read-only verification tasks, different files)
# T016 must be last:
T013 + T014 + T015 → T016
```

---

## Implementation Notes for the Implementer

These notes are here so a smaller model can work without needing to re-read all source
documents:

1. **Password hash format**: `"salt_hex:pbkdf2_hex"` — both parts are `.hex()` encoded
   bytes. Always split on `':'` in `verify_password`. Use 260,000 PBKDF2 iterations.

2. **Idempotent seeding**: `seed_default_admin()` calls `count_users()` first. If > 0,
   it does nothing. Never call `insert_user` unconditionally on startup.

3. **Connection lifecycle**: Every `*_db.py` function opens its own connection, does
   its work, commits if writing, and closes. Never store a connection as a module-level
   variable.

4. **Logout signal pattern**: `MainWindow` declares `logged_out = Signal()` at the class
   level (not inside `__init__`). `LoginWindow._open_main_window()` connects
   `main_window.logged_out` to `self._on_logged_out`. When Logout is clicked,
   `MainWindow._on_logout()` emits `self.logged_out.emit()` then calls `self.close()`.
   `LoginWindow._on_logged_out()` shows the login window again and resets fields.

5. **Wait cursor for Backup Now**: In `_on_backup`, always call
   `QApplication.restoreOverrideCursor()` in both the success path and the except path,
   or the cursor will stay as a spinner after an error.

6. **`data/` directory creation**: `database.get_connection()` calls
   `os.makedirs(config.DATA_DIR, exist_ok=True)` before connecting, so `data/store.db`
   can always be created even on first run when the folder doesn't exist yet.

7. **No `logic/` files in Phase 1**: The `logic/` directory exists (created in T001)
   but `logic/__init__.py` is the only file in it at the end of this phase.

8. **Import order in `main.py`**: Import `database` and `auth` before importing any
   `ui` file, because `ui/login_window.py` eventually imports `main_window.py` which
   imports the placeholder pages — all of which require `config.py` to already be
   importable, which it will be since it has no internal dependencies.
