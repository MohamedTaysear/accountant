# Tasks: UI Layout Polish

**Input**: `specs/001-ui-layout-polish/plan.md`, `spec.md`, `research.md`, `quickstart.md`

**Goal**: Fix action button clipping, standardise control heights, tighten alignment, and ensure every button is fully visible across all pages and d
ialogs — without changing any business logic, database code, or calculations.

---

## Engineering Rules (apply to every task)

These three rules govern every implementation decision. They override any task wording that would produce a result that violates them.

### Rule 1 — No Hardcoded UI Values

Never introduce a new numeric literal (width, height, spacing, margin, padding, radius) inside a page or dialog file when that value could be a design token or a shared constant.

- Spacing values → always use `theme._active.spacing_*` tokens.
- Repeated widths or heights → define a module-level constant in `theme.py`, not inline.
- If a number appears more than once anywhere in the codebase, it must become a shared constant before the phase is closed.

The reference constants table below already defines the button and column constants that belong in `theme.py`. Every one of them must live there, not in individual page files.

### Rule 2 — Prefer Reusable Helpers

If the same UI behaviour is needed in more than one file, it must be expressed as a shared helper in `theme.py`, not duplicated per file.

Current shared helpers that already exist and **must be used** (never reimplemented inline):
- `theme.apply_table_style(table)` — standard table configuration
- `theme.apply_actions_column(table, col)` — Actions column fixed width + Fixed resize mode
- `theme.make_empty_label(text)` — empty-state label

If a new pattern appears in two or more files during implementation (e.g., a button-row builder for dialogs, a section-title helper, a card-construction helper), extract it into `theme.py` before the phase ends.

### Rule 3 — Refactor After Every Phase

After completing each implementation phase (Phases 2–8), before moving to the next phase:

1. Read every file modified in that phase.
2. Remove any duplicated code (same logic expressed twice in different places).
3. Move any new inline constant that appears more than once into `theme.py`.
4. Confirm the solution uses the centralized design system rather than per-file overrides.
5. Only then mark the phase complete and proceed.

Each phase must leave the codebase cleaner than it was before. The final evaluation criterion is **visual quality AND maintainability**, not just visual quality alone.

---

## Reference Constants (all defined in `theme.py`, not in page files)

| Constant | Value | Location |
|----------|-------|----------|
| `_ACTIONS_COL_WIDTH` | `170` | `theme.py` — fixed width for any Actions column |
| `_BTN_MIN_EDIT` | `55` | `theme.py` — minimum width for "Edit" buttons |
| `_BTN_MIN_DELETE` | `62` | `theme.py` — minimum width for "Delete" buttons |
| `_BTN_MIN_DEACTIVATE` | `88` | `theme.py` — minimum width for "Deactivate" buttons |
| `_BTN_MIN_ACTIVATE` | `70` | `theme.py` — minimum width for "Activate" buttons |
| `_BTN_MIN_REMOVE` | `70` | `theme.py` — minimum width for "Remove" buttons |
| Standard control height | `30` | `theme.py` QSS `min-height` — already set |

**No new packages may be imported.** All imports must come from `PySide6.QtWidgets`, `PySide6.QtCore`, or `PySide6.QtGui`.

---

## Phase 1: Setup

No project structure changes needed. The existing `accounting_system/ui/` package is the only location modified.

**Checkpoint**: Skip directly to Phase 2.

---

## Phase 2: Foundational — Theme Helpers (`accounting_system/ui/theme.py`)

**Purpose**: Add the Actions column constant and helper that every page phase will use. Must be complete before Phase 3.

**CRITICAL**: Do NOT change any existing functions, constants, colours, or font sizes already in theme.py. Only ADD new items.

- [X] T001 Read `accounting_system/ui/theme.py` in full, then add all button-width constants and the Actions column constant immediately after the existing `_TABLE_HEADER_H` constant. Add exactly these lines as a block:

  ```python
  _ACTIONS_COL_WIDTH   = 170   # fixed width for any Actions column
  _BTN_MIN_EDIT        = 55    # minimum width for "Edit" buttons
  _BTN_MIN_DELETE      = 62    # minimum width for "Delete" buttons
  _BTN_MIN_DEACTIVATE  = 88    # minimum width for "Deactivate" buttons
  _BTN_MIN_ACTIVATE    = 70    # minimum width for "Activate" buttons
  _BTN_MIN_REMOVE      = 70    # minimum width for "Remove" buttons
  ```

  These constants must live only in `theme.py`. Do not define any of these values inside page or dialog files. (around line where `_TABLE_MIN_HEIGHT`, `_TABLE_MAX_HEIGHT`, `_TABLE_HEADER_H` are defined). The constant must be at module level, not inside any function or class.

- [X] T002 In `accounting_system/ui/theme.py`, add the following function immediately after the existing `_fit_table_height` function. Add it exactly as shown — do not modify `_fit_table_height` or `apply_table_style`:

  ```python
  def apply_actions_column(table: QTableWidget, col: int) -> None:
      """Set a fixed width on the Actions column and prevent user resize."""
      table.setColumnWidth(col, _ACTIONS_COL_WIDTH)
      table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
  ```

  Ensure `QHeaderView` is already imported in theme.py (it is, via `from PySide6.QtWidgets import ... QHeaderView ...`). If it is missing from the import line, add it.

**Checkpoint**: Open Python REPL, `from ui import theme`, call `theme.apply_actions_column` — verify it exists and is callable with no error.

**Phase 2 Refactor Gate** (Rule 3 — complete before Phase 3):
- [X] T002-R Re-read `accounting_system/ui/theme.py`. Confirm all 6 button-width constants and `_ACTIONS_COL_WIDTH` are present at module level. Confirm `apply_actions_column()` is defined once and only once. Confirm no numeric literal from the reference table appears anywhere except in these constant definitions. Remove any duplicate or stale constant definitions.

**Phase 2 Regression Check** — previously completed screens: *(none yet — this is the first implementation phase)*
- [X] T002-X Launch the application and confirm it starts without errors. Navigate to every page once (Dashboard, Products, Sales, Purchases, Expenses, Reports) and confirm no page throws a Python exception or displays a broken layout caused by the theme.py changes. This baseline confirms the new constants and helper did not break the import chain.

---

## Phase 3: Products Page — Action Buttons & Header Alignment (US1)

**File**: `accounting_system/ui/products_page.py`

**Goal**: Actions column shows Edit + Delete/Deactivate/Activate buttons fully visible; header search row controls are aligned.

**Independent Test** (quickstart Scenario 1 & 2): Launch app → Products page → all action buttons visible, no clipping; search row controls same height.

- [X] T003 Read `accounting_system/ui/products_page.py` in full before making any changes.

- [X] T004 [US1] In `accounting_system/ui/products_page.py`, find where the products table (`self.table`) is built and `theme.apply_table_style(self.table)` is called. Immediately after that call, add:
  ```python
  theme.apply_actions_column(self.table, ACTION_COL)
  ```
  where `ACTION_COL` is the integer index of the Actions column (identify it from the `setHorizontalHeaderLabels` call — it is the last column). If there is no named constant, substitute the integer directly (e.g., `theme.apply_actions_column(self.table, 5)` if the Actions column is index 5).

- [X] T005 [US1] In `accounting_system/ui/products_page.py`, find the method that populates table rows (likely `_rebuild_table`, `_load_products`, or similar — search for `setCellWidget` or `QPushButton`). For each `QPushButton` created and placed in the Actions column, add a `setMinimumWidth` call using the constants from `theme.py` (imported as `from ui import theme` or already in scope as `theme`):
  - "Edit" button: add `btn.setMinimumWidth(theme._BTN_MIN_EDIT)` immediately after `btn = QPushButton("Edit")`
  - "Delete" button: add `btn.setMinimumWidth(theme._BTN_MIN_DELETE)` immediately after `btn = QPushButton("Delete")`
  - "Deactivate" button: add `btn.setMinimumWidth(theme._BTN_MIN_DEACTIVATE)` immediately after `btn = QPushButton("Deactivate")`
  - "Activate" button: add `btn.setMinimumWidth(theme._BTN_MIN_ACTIVATE)` immediately after `btn = QPushButton("Activate")`
  Do not use raw integers. Do not change the button text, signal connections, or any logic.

- [X] T006 [P] [US1] In `accounting_system/ui/products_page.py`, find the header/toolbar row that contains the search input, "Show Inactive" checkbox, and "+ Add Product" button. Ensure that row's QHBoxLayout has `setAlignment(Qt.AlignVCenter)` called on it. If the layout variable is named (e.g., `toolbar_layout`), add `toolbar_layout.setAlignment(Qt.AlignVCenter)`. If inline, set it on the QHBoxLayout object directly. Import `Qt` from `PySide6.QtCore` if not already imported.

- [X] T007 [P] [US1] In `accounting_system/ui/products_page.py`, verify the Name column (or the first text column) has `QHeaderView.Stretch` set. Search for `setSectionResizeMode`. If the stretch column is not set, add:
  ```python
  self.table.horizontalHeader().setSectionResizeMode(NAME_COL, QHeaderView.Stretch)
  ```
  where `NAME_COL` is the index of the Name column (typically 0). Do NOT set Stretch on any other column.

- [X] T008 [US1] In `accounting_system/ui/products_page.py`, verify a `layout.addStretch()` call exists after the table widget is added to the main layout. If missing, add it immediately after `layout.addWidget(self.table)` (or after the empty-state label widget if one exists). This prevents the background below the table from becoming a large white container.

**Checkpoint**: Launch app → Products page → at least one product visible → Edit and Delete/Deactivate buttons fully visible with no clipping. Resize to 900×600 → horizontal scrollbar on table viewport; Actions column still accessible by scrolling.

**Phase 3 Refactor Gate** (Rule 3 — complete before Phase 4):
- [X] T008-R Re-read `accounting_system/ui/products_page.py`. Verify: (a) no raw integer appears where a `theme._BTN_MIN_*` or `theme._active.spacing_*` constant should be used; (b) no UI logic is duplicated that already exists in a `theme.py` helper; (c) `theme.apply_actions_column` and `theme.apply_table_style` are the only table-configuration calls (no competing `setColumnWidth` or `setSectionResizeMode` on the Actions column that would override the helper). Fix any violation found.

**Phase 3 Regression Check** — previously completed screens: Phase 2 (theme.py)
- [X] T008-X Launch the application. Verify the following acceptance criteria for Phase 2 have not regressed:
  - `from ui import theme` in a Python shell imports without error.
  - `theme._ACTIONS_COL_WIDTH` equals `170`.
  - `theme._BTN_MIN_DEACTIVATE` equals `88`.
  - `theme.apply_actions_column` is callable.
  - `theme.apply_table_style` is callable.
  If any of these fail, fix `theme.py` before proceeding to Phase 4.

---

## Phase 4: Form Pages — Add-Item Card Layout (US2)

**Files**: `accounting_system/ui/sales_page.py`, `accounting_system/ui/purchases_page.py`, `accounting_system/ui/expenses_page.py`

**Goal**: Add-item card controls share equal height; line-item table Remove column buttons are visible.

**Independent Test** (quickstart Scenario 4): Launch → Sales page → product combo, qty spinbox, and Add button appear at same visual height. Same for Purchases and Expenses.

### Sales Page (`accounting_system/ui/sales_page.py`)

- [X] T009 Read `accounting_system/ui/sales_page.py` in full before making any changes.

- [X] T010 [US2] In `accounting_system/ui/sales_page.py`, find the add-item card's QHBoxLayout (the row with product combo + qty spinbox + add button). Add `setAlignment(Qt.AlignVCenter)` on that layout object so all controls are vertically centred. Import `Qt` from `PySide6.QtCore` if not already imported.

- [X] T011 [US2] In `accounting_system/ui/sales_page.py`, find where the line-items table (`self.table`) is built and `theme.apply_table_style(self.table)` is called. Immediately after that call, add:
  ```python
  theme.apply_actions_column(self.table, REMOVE_COL)
  ```
  where `REMOVE_COL` is the integer index of the remove/actions column (the last column — check `setHorizontalHeaderLabels` to find it; it typically has header `""`).

- [X] T012 [P] [US2] In `accounting_system/ui/sales_page.py`, find the method that rebuilds the line-items table rows (`_rebuild_table` or similar — look for `insertRow` and `setCellWidget`). For the "Remove" QPushButton created there, add `remove_btn.setMinimumWidth(theme._BTN_MIN_REMOVE)` immediately after `remove_btn = QPushButton("Remove")`. Use the theme constant — not the raw integer `70`.

### Purchases Page (`accounting_system/ui/purchases_page.py`)

- [X] T013 Read `accounting_system/ui/purchases_page.py` in full before making any changes.

- [X] T014 [US2] In `accounting_system/ui/purchases_page.py`, apply the same three changes as T010–T012:
  1. `setAlignment(Qt.AlignVCenter)` on the add-item QHBoxLayout
  2. `theme.apply_actions_column(self.table, REMOVE_COL)` after `apply_table_style`
  3. `remove_btn.setMinimumWidth(theme._BTN_MIN_REMOVE)` for Remove buttons in the rebuild method (use the constant, not `70`)

### Expenses Page (`accounting_system/ui/expenses_page.py`)

- [X] T015 Read `accounting_system/ui/expenses_page.py` in full before making any changes.

- [X] T016 [US2] In `accounting_system/ui/expenses_page.py`, the add-item card has two QHBoxLayout rows (row1: Category + Amount; row2: Description + Notes + Add Line). Apply `setAlignment(Qt.AlignVCenter)` to **both** row layouts (row1 and row2) separately.

- [X] T017 [US2] In `accounting_system/ui/expenses_page.py`, apply:
  1. `theme.apply_actions_column(self.items_table, REMOVE_COL)` after `apply_table_style(self.items_table)`
  2. `btn.setMinimumWidth(theme._BTN_MIN_REMOVE)` for the "Remove" QPushButton in `_rebuild_items_table` (use the constant, not `70`)

**Checkpoint**: Launch app → Sales page → add-item row controls at same visual height → add 1 line → Remove button fully visible. Repeat for Purchases and Expenses.

**Phase 4 Refactor Gate** (Rule 3 — complete before Phase 5):
- [X] T017-R Re-read `sales_page.py`, `purchases_page.py`, and `expenses_page.py` in sequence. Check that the three files use identical patterns for: (a) `apply_actions_column` call on the Remove column; (b) `_BTN_MIN_REMOVE` on the Remove button; (c) `setSizePolicy(Expanding, Fixed)` on add-item card and footer card; (d) `addStretch()` after footer card. If any file deviates from the pattern without a documented reason, align it. If an identical multi-line block appears in all three files and could be extracted into a `theme.py` helper (e.g., `make_action_button(label, min_width)`), extract it now and update all three call sites.

**Phase 4 Regression Check** — previously completed screens: Phase 2 (theme.py), Phase 3 (Products page)
- [X] T017-X Launch the application and verify the following have not regressed:
  - **Products page**: Navigate to Products. Confirm Edit and Delete/Deactivate buttons are still fully visible in the Actions column with no clipping. Confirm the search toolbar row controls are still vertically aligned. Confirm the table still adapts its height to content (no large empty white area below rows).
  - **Application startup**: No Python exception or traceback appears in the terminal on launch.
  If any regression is found, fix it in the relevant file before proceeding to Phase 5. Do not carry a known regression forward.

---

## Phase 5: Dashboard Page (US3)

**File**: `accounting_system/ui/dashboard_page.py`

**Goal**: KPI cards equal height and aligned; Low Stock and Recent Transactions tables adaptive.

**Independent Test** (quickstart Scenario — Dashboard): Launch → Dashboard → KPI cards same height, same spacing; tables sized to content.

- [X] - [X] T018 Read `accounting_system/ui/dashboard_page.py` in full before making any changes.

- [X] - [X] T019 [US3] In `accounting_system/ui/dashboard_page.py`, find the KPI card row layout (the QHBoxLayout that holds the KPI metric cards). Ensure each KPI card frame has `setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)` set so all cards share the same fixed height and expand equally. Also ensure the row QHBoxLayout uses equal stretch for all cards. If cards are added with `addWidget(card)`, change to `addWidget(card, 1)` so all cards get equal stretch factor 1.

- [X] - [X] T020 [P] [US3] In `accounting_system/ui/dashboard_page.py`, find the Low Stock table and the Recent Transactions/Activity table. Verify `theme.apply_table_style(table)` is called for both. If either call is missing, add it immediately after the table is constructed (after `setColumnCount`, `setHorizontalHeaderLabels`). Do not remove any existing `setColumnWidth` or `setSectionResizeMode` calls — only add `apply_table_style` if missing.

- [X] - [X] T021 [P] [US3] In `accounting_system/ui/dashboard_page.py`, verify the page outer layout (`QVBoxLayout`) uses `setSpacing(theme._active.spacing_lg)` consistently between Dashboard sections. If spacing is set to a different value, change it to `theme._active.spacing_lg` (which equals 16 px in the current theme).

**Checkpoint**: Launch app → Dashboard → KPI cards same height, equal width, equal spacing; Low Stock and Recent Transactions tables sized to their content with no large empty white area below.

**Phase 5 Refactor Gate** (Rule 3 — complete before Phase 6):
- [X] - [X] T021-R Re-read `accounting_system/ui/dashboard_page.py`. Verify: (a) no spacing integer is hardcoded where `theme._active.spacing_*` should be used; (b) KPI card sizing uses theme tokens for margins and radii (not hardcoded pixel values); (c) `apply_table_style` is called on both tables; (d) no constant defined here duplicates one already in `theme.py`. Fix any violation.

**Phase 5 Regression Check** — previously completed screens: Phase 2 (theme.py), Phase 3 (Products), Phase 4 (Sales, Purchases, Expenses)
- [X] - [X] T021-X Launch the application and verify the following have not regressed:
  - **Products page**: Edit/Deactivate/Delete buttons still fully visible in Actions column. Table height still adaptive.
  - **Sales page**: Product combo, qty spinbox, and Add button still appear at equal height in the add-item card. Footer card still compact (no large empty area below it).
  - **Purchases page**: Same checks as Sales page.
  - **Expenses page**: Both add-item rows still aligned; Add Line button still visible.
  - **Application startup**: No exception in terminal.
  If any regression is found, fix it before proceeding to Phase 6.

---

## Phase 6: Reports Page Verification (US4)

**File**: `accounting_system/ui/reports_page.py`

**Goal**: Confirm the prior section-panel redesign is complete and correct; fix any remaining issues.

**Independent Test** (quickstart Scenario 5): Launch → Reports → each of 6 sections shows bold plain title + separator + filters + table; no heavy GroupBox frame around titles.

- [X] - [X] T022 Read `accounting_system/ui/reports_page.py` in full before making any changes.

- [X] - [X] T023 [US4] In `accounting_system/ui/reports_page.py`, verify that all six history/analytics panels are constructed using the `_section_panel(title)` static method (or equivalent). Check the method returns a `(QFrame, QVBoxLayout)` tuple where the layout adds: (1) a bold QLabel title, (2) a 1 px QFrame horizontal separator, (3) the filter/search controls, (4) the table. If any panel still uses the old uppercase-label style, replace it with `_section_panel()`.

- [X] - [X] T024 [P] [US4] In `accounting_system/ui/reports_page.py`, verify `theme.apply_table_style(table)` is called for all six report tables (Sales History, Purchases History, Expenses History, Top Selling Products, Top Purchased Products, Top Expense Categories). Add any missing calls.

- [X] - [X] T025 [P] [US4] In `accounting_system/ui/reports_page.py`, verify `_section_panel`'s `vl.setContentsMargins` uses `spacing_sm` (8 px) for top and bottom margins — NOT `spacing_lg` (16 px). If the values are wrong, correct them to `(spacing_md, spacing_sm, spacing_md, spacing_sm)`.

**Checkpoint**: Launch app → Reports page → all 6 sections display with compact bold title at the top, no heavy bordered frame around the title text.

**Phase 6 Refactor Gate** (Rule 3 — complete before Phase 7):
- [X] - [X] T025-R Re-read `accounting_system/ui/reports_page.py`. Verify: (a) `_section_panel()` is the only place that constructs section title + separator — no inline equivalent exists elsewhere in the file; (b) all six panels call `_section_panel()` (no panel builds its title independently); (c) all six tables call `apply_table_style()`; (d) no spacing or colour value is hardcoded where a theme token should be used. If `_section_panel()` would be useful on other pages, consider moving it to `theme.py` as `make_section_panel(title)` — but only if it would actually be reused; do not move it speculatively.

**Phase 6 Regression Check** — previously completed screens: Phase 2 (theme.py), Phase 3 (Products), Phase 4 (Forms), Phase 5 (Dashboard)
- [X] - [X] T025-X Launch the application and verify the following have not regressed:
  - **Products page**: Action buttons still fully visible. Table height still adaptive.
  - **Sales / Purchases / Expenses pages**: Add-item row controls still equal height. Remove buttons still visible in line-item tables. Footer card still compact.
  - **Dashboard**: KPI cards still equal height and equally spaced. Low Stock and Recent Transactions tables still sized to content.
  - **Application startup**: No exception in terminal.
  If any regression is found, fix it before proceeding to Phase 7.

---

## Phase 7: Dialog Button Audit (US5)

**Files**: `accounting_system/ui/product_dialog.py`, `accounting_system/ui/invoice_detail_dialog.py`, `accounting_system/ui/expense_detail_dialog.py`, `accounting_system/ui/change_password_dialog.py`

**Goal**: Every button in every dialog is fully visible with no text clipping at 1280×800.

**Independent Test** (quickstart Scenario 7): Open each dialog → all buttons visible, text not clipped.

**Pattern to apply in each dialog**: Find the button row QHBoxLayout. Ensure:
1. `addStretch()` is called **before** the first button (so buttons are right-aligned) OR buttons use `addWidget(btn)` with a `addStretch()` at the beginning of the row.
2. Each button has no `setFixedWidth` call that clips its text — remove any `setFixedWidth` on dialog action buttons.
3. Each button has at minimum 8 px horizontal padding (this comes from the theme QSS — do not add manual padding).

### Product Dialog

- [X] - [X] T026 Read `accounting_system/ui/product_dialog.py` in full before making changes.

- [X] - [X] T027 [US5] In `accounting_system/ui/product_dialog.py`, find the button row (Save + Cancel buttons). Ensure the row uses `QHBoxLayout` with `addStretch()` as the first item so buttons are right-aligned. Ensure neither button has `setFixedWidth()`. If `setFixedWidth` exists on either button, replace it with `setMinimumWidth(80)` (or remove the fixed width call entirely).

### Invoice Detail Dialog

- [X] - [X] T028 Read `accounting_system/ui/invoice_detail_dialog.py` in full before making changes.

- [X] - [X] T029 [US5] In `accounting_system/ui/invoice_detail_dialog.py`, find all QPushButton instances. For the "Void Invoice" button: ensure it uses `setEnabled(False)` (disabled, but visible) when the invoice is already voided — NOT `setVisible(False)` or `hide()`. A hidden Void button is a failed audit; a disabled (greyed) one is correct. Ensure the button row uses `addStretch()` before the first button.

- [X] - [X] T030 [P] [US5] In `accounting_system/ui/invoice_detail_dialog.py`, ensure the "Close" button has no `setFixedWidth` call. If present, remove it or replace with `setMinimumWidth(70)`.

### Expense Detail Dialog

- [X] - [X] T031 Read `accounting_system/ui/expense_detail_dialog.py` in full before making changes.

- [X] - [X] T032 [US5] In `accounting_system/ui/expense_detail_dialog.py`, apply the same pattern: button row has `addStretch()` before first button; no `setFixedWidth` on action buttons; all buttons visible.

### Change Password Dialog

- [X] - [X] T033 Read `accounting_system/ui/change_password_dialog.py` in full before making changes.

- [X] - [X] T034 [US5] In `accounting_system/ui/change_password_dialog.py`, ensure the "Change Password" and "Cancel" buttons are in a QHBoxLayout with `addStretch()` before the first button. Ensure neither button has `setFixedWidth`. Ensure the dialog has a minimum width (call `self.setMinimumWidth(380)` in `__init__` if not already set) so buttons never clip at any system font size.

**Checkpoint**: Open each dialog from within the running app → all action buttons show their full text with no clipping.

**Phase 7 Refactor Gate** (Rule 3 — complete before Phase 8):
- [X] - [X] T034-R Re-read all four dialog files. Verify: (a) all four use the same button-row pattern (`QHBoxLayout` + `addStretch()` before buttons); (b) no dialog uses `setFixedWidth` on an action button; (c) all four use `self.setMinimumWidth(...)` to prevent layout collapse at small sizes. If the button-row pattern is identical across three or more dialogs, extract a helper into `theme.py`:

  ```python
  def make_dialog_button_row(*buttons) -> QHBoxLayout:
      """Returns an HBoxLayout with addStretch() before right-aligned buttons."""
      row = QHBoxLayout()
      row.addStretch()
      for btn in buttons:
          row.addWidget(btn)
      return row
  ```

  Update all dialog files to use this helper if extracted. This is only worth extracting if three or more dialogs share the identical pattern — do not over-engineer for two.

**Phase 7 Regression Check** — previously completed screens: Phase 2 (theme.py), Phase 3 (Products), Phase 4 (Forms), Phase 5 (Dashboard), Phase 6 (Reports)
- [X] - [X] T034-X Launch the application and verify the following have not regressed:
  - **Products page**: Edit/Delete/Deactivate/Activate buttons still fully visible. Table height adaptive.
  - **Sales page**: Add-item row equal height. Remove buttons visible. Footer card compact.
  - **Purchases page**: Same checks as Sales.
  - **Expenses page**: Both add-item rows aligned. Remove buttons visible. Footer compact.
  - **Dashboard**: KPI cards equal height and spaced. Tables sized to content.
  - **Reports page**: All 6 section panels show bold plain title (no heavy frame). Tables sized to content.
  - **Application startup**: No exception in terminal.
  If any regression is found, fix it before proceeding to Phase 8.

---

## Phase 8: Polish & Full Visual Review

**Goal**: Walk every screen against the 7 Success Criteria in quickstart.md and fix any remaining issues found. Phase 8 also serves as the cumulative regression gate for Phases 2–7 — every previously completed screen is checked here as part of the full sweep (T035–T042).

- [ ] T035 Launch the application and navigate to **Products** page. Verify against quickstart Scenario 1 (action buttons visible) and Scenario 2 (header row alignment). Log any failures.

- [ ] T036 [P] Navigate to **Sales** page. Verify quickstart Scenario 4 (add-item row cohesion, form compactness). Log failures.

- [ ] T037 [P] Navigate to **Purchases** page. Apply same checks as T036.

- [ ] T038 [P] Navigate to **Expenses** page. Apply same checks as T036.

- [ ] T039 Navigate to **Reports** page. Verify quickstart Scenario 5 (section layout). Log failures.

- [ ] T040 [P] Navigate to **Dashboard**. Verify KPI card alignment and table adaptive sizing. Log failures.

- [ ] T041 Open all four dialogs in sequence (Product, Invoice Detail, Expense Detail, Change Password). Verify quickstart Scenario 7 (button visibility). Log failures.

- [ ] T042 Resize the application window from 1280×800 down to 900×600. On each page, verify quickstart Scenario 8 (resize stability): no clipping, no disappearing buttons, table-only horizontal scrollbar where applicable. Log failures.

- [ ] T043 Fix any failures logged in T035–T042. If a fix requires a new task pattern not covered in Phases 2–7, apply the closest matching pattern from the relevant phase (e.g., missing `setMinimumWidth` → add it; wrong layout alignment → add `setAlignment(Qt.AlignVCenter)`).

- [ ] T044 Re-run the full quickstart.md scenario checklist and mark each row Pass or Fail. All 8 scenarios must pass before the feature is considered complete.

**Phase 8 Refactor Gate** (Rule 3 — complete before Phase 9):
- [X] T044-R Do a final codebase sweep across all modified files (`theme.py`, `products_page.py`, `sales_page.py`, `purchases_page.py`, `expenses_page.py`, `dashboard_page.py`, `reports_page.py`, and all four dialog files). For each file, verify:
  1. No raw integer appears where a `theme._active.spacing_*`, `theme._BTN_MIN_*`, or `theme._ACTIONS_COL_WIDTH` constant should be used.
  2. No UI helper is implemented inline that duplicates an existing `theme.py` helper.
  3. No dead code, commented-out layout code, or stale `setFixedHeight` calls remain.
  4. Every table in every file calls `theme.apply_table_style()`.
  5. Every Actions/Remove column in every table calls `theme.apply_actions_column()`.
  Fix all violations found. The codebase must be clean before the visual audit begins.

---

## Phase 9: Visual Consistency Audit — MANDATORY

**Purpose**: Verify the entire application feels like one coherent commercial product. This phase is not optional. The feature must not be marked complete until every task in this phase passes.

**The audit question is not "did every task execute?" — it is "would a paying customer consider this professional software?"**

**Method**: Launch the application and visually inspect every screen. Where a task says "verify", that means look at the running UI and judge it. Where it says "fix", that means open the relevant source file, make the correction, and re-launch to confirm.

---

### 9A — Screenshot Comparison

- [ ] T045 Take a fresh screenshot of every page and dialog at 1280×800 (Dashboard, Products, Sales, Purchases, Expenses, Reports, and all four dialogs). Compare each screenshot side by side against the baseline screenshots already captured this session. For every screen where the new screenshot shows a visible layout difference — tighter spacing, different alignment, changed element sizes — determine whether the change is an improvement or a regression. Log regressions and fix them before proceeding.

---

### 9B — Cross-Page Consistency Audit

**Every page must feel like it was designed by the same person in the same session.**

- [X] T046 Open Dashboard, then Products, then Sales in sequence without closing the window. Evaluate: do the page title sizes, margins from the window edge, card corner radii, and card border colours all appear identical? If any page looks noticeably different from the others, read its source file and align its `setContentsMargins`, card `border-radius`, and `spacing` values to match `theme._active` constants (`spacing_xl` for page outer margins, `card_border_radius` for card frames, `spacing_lg` between page sections).

- [X] T047 Open Purchases, then Expenses, then Reports in sequence. Apply the same cross-page comparison as T046. These three pages must match Dashboard, Products, and Sales exactly in margin, card styling, and section spacing.

- [X] T048 Verify that every page title ("Dashboard", "Products", "New Sale Invoice", "New Purchase Invoice", "New Expense Invoice", "Reports") uses the same font size (`theme._active.size_page_title` = 13 pt) and bold weight, and the same colour (`theme._active.text_primary`). If any page title deviates, correct its `QFont` or stylesheet in that page's source file.

---

### 9C — Typography Audit

**One visual hierarchy. Zero deviations.**

- [X] T049 Inspect every **page title** (the large label at the top of each page). Verify: 13 pt, bold, `text_primary` colour, `background: transparent`. Fix any deviation found in the relevant `*_page.py` file.

- [X] T050 Inspect every **section heading** inside cards or panels (e.g., "Sales History", "Top Selling Products", card sub-titles). Verify: 11 pt, bold, `text_primary` colour, `background: transparent`. Fix any deviation in `reports_page.py` or other files.

- [X] T051 Inspect every **table column header** across all tables. Verify they appear bold and are clearly visually heavier than body cell text. Qt's default table header renders at system weight; if headers look too light, add to the QSS block for `QHeaderView::section` in `theme.py`: `font-weight: bold;`. Do this only if headers currently look unbolded — do not add duplicate rules.

- [X] T052 Inspect every **label** next to a form field (e.g., "Category:", "Amount:", "Product:", "Qty:", "Unit Price:"). Verify they all use `theme._active.text_secondary` colour and `background: transparent`. Fix any label that uses a hard-coded colour string instead of the theme token.

- [X] T053 Inspect every **empty-state label** (the centred message shown when a table has no rows). Verify they all use the same style: centred, `text_secondary` colour, 10 pt (normal weight), `background: transparent`. If any empty-state label uses a different size or colour, fix it in the source file or in `theme.make_empty_label()` in `theme.py`.

- [X] T054 Inspect every **dialog title** (the window title bar text set via `setWindowTitle`). Verify dialog titles are concise, title-case, and consistent in style. No dialog title should be all-caps or start with a verb like "Do you want to...". Fix any inconsistent `setWindowTitle` call.

---

### 9D — Layout Grid Audit

**One spacing system. No ad-hoc values.**

The permitted spacing values are defined in `theme._active`:

| Token | Value |
|-------|-------|
| `spacing_xs` | 4 px |
| `spacing_sm` | 8 px |
| `spacing_md` | 12 px |
| `spacing_lg` | 16 px |
| `spacing_xl` | 24 px |
| `spacing_xxl` | 32 px |

- [X] T055 Read `accounting_system/ui/sales_page.py`, `purchases_page.py`, and `expenses_page.py`. Search for any `setContentsMargins(...)` or `setSpacing(...)` call that uses a hard-coded integer **not** equal to one of the 6 permitted spacing values above. Replace each violation with the nearest permitted value using `theme._active.spacing_*`. Do not change margins/spacing that are already using theme tokens.

- [X] T056 Read `accounting_system/ui/dashboard_page.py` and `reports_page.py`. Apply the same audit as T055 — replace any hard-coded spacing integer that does not match a permitted spacing token.

- [X] T057 Read `accounting_system/ui/products_page.py`. Apply the same audit as T055.

- [X] T058 [P] Read all four dialog files (`product_dialog.py`, `invoice_detail_dialog.py`, `expense_detail_dialog.py`, `change_password_dialog.py`). Apply the same audit as T055 — dialogs must also use theme spacing tokens, not arbitrary integers.

- [X] T059 Launch the application and visually verify that the space between the page title and the first card below it is consistent across Dashboard, Products, Sales, Purchases, Expenses, and Reports. It should look the same on every page. If any page has noticeably more or less space here, read its source file and align its `layout.setSpacing(theme._active.spacing_lg)` and `layout.setContentsMargins` to match the others.

---

### 9E — Table Consistency Audit

**Every table in the application must feel like it belongs to one design system.**

Tables in scope: Products table, Sales line-items, Purchases line-items, Expenses line-items, Dashboard Low Stock, Dashboard Recent Transactions, Reports Sales History, Reports Purchases History, Reports Expenses History, Reports Top Selling Products, Reports Top Purchased Products, Reports Top Expense Categories.

- [X] T060 Launch the application. Open Products page, then Sales page (add one line item so the table is visible), then Dashboard. Look at the three visible tables. Verify: row height is visually identical across all three; header row height is visually identical; alternating row colours (if enabled) use the same shade. If any table looks different, read `theme.py` and verify `apply_table_style()` is called on that table. If it is not, add the call in the relevant source file.

- [X] T061 Inspect every table's **column resize policy**. For each table, choose the most appropriate policy for each column using this guide:
  - **Primary content column** (Name, Description, Product name): `QHeaderView.Stretch` — exactly one column per table should stretch.
  - **Numeric columns** (Qty, Price, Amount, Stock): `QHeaderView.Fixed` with a width that fits the longest expected value (e.g., `90` px for currency columns, `70` px for quantity columns).
  - **Short code columns** (SKU, Invoice #): `QHeaderView.Fixed`, sized to fit the longest code (e.g., `100` px).
  - **Actions column**: `QHeaderView.Fixed` at `_ACTIONS_COL_WIDTH` (170 px) — already handled by `apply_actions_column()`.
  - **Date/time columns**: `QHeaderView.Fixed` at `140` px.
  
  Read each page's source file and verify that every column has an explicit resize mode set. Add any missing `setSectionResizeMode` calls. Do not set `Stretch` on more than one column per table.

- [X] T062 Verify empty-state behaviour for every table: when a table has zero rows, the table widget is hidden and the corresponding `make_empty_label` is shown; when rows exist, the label is hidden and the table is shown. If any table stays visible as an empty white rectangle when it has no rows, fix its row-rebuild method to call `table.setVisible(row_count > 0)` and `empty_label.setVisible(row_count == 0)`.

- [X] T063 Verify that every table has `setAlternatingRowColors(True)` active (this is set by `apply_table_style()`). If any table still shows uniform white rows with no alternation, re-check that `apply_table_style()` is called after `setColumnCount` and before the table is added to the layout.

---

### 9F — Control Consistency Audit

**Every interactive control must look like it came from one design system.**

- [X] T064 Launch the application. On the **Products** page, inspect the search field, the "Show Inactive" checkbox, and the "+ Add Product" button. They must appear at the same visual height (30 px). If the checkbox appears shorter or misaligned, add to the QSS block for `QCheckBox` in `theme.py`: `min-height: 30px;` — but only if not already present.

- [X] T065 On the **Sales** page, inspect the product combo, qty spinbox, and "+ Add to Invoice" button in the add-item card. They must appear at the same visual height. On **Purchases**, inspect product combo, qty spinbox, unit price spinbox, and Add button. On **Expenses**, inspect category combo, amount field, description field, notes field, and Add Line button. All controls on each row must be the same height. If any control appears taller or shorter, check its `setFixedHeight` or `setMaximumHeight` calls and remove any that override the 30 px minimum from the theme QSS.

- [ ] T066 On the **Reports** page, inspect the search/filter controls in each section panel (search field, combo boxes, date pickers). Verify they all appear at the same 30 px height and share the same left alignment within their section. Fix any control that looks taller, shorter, or misaligned.

- [ ] T067 Open each dialog (Product, Invoice Detail, Expense Detail, Change Password). Verify that every text input, combo box, and button inside the dialog is at the same 30 px height. Fix any control that deviates inside its dialog's source file.

---

### 9G — Button Visibility Final Sweep

**Zero tolerance. No button may be anything other than fully visible and clickable.**

- [ ] T068 On the **Products** page with at least 3 products visible, inspect every row's Edit and Delete/Deactivate/Activate buttons. Confirm: button text is not clipped; buttons do not extend outside the cell boundary; both buttons in a row do not overlap. If any button fails, re-check that `theme.apply_actions_column()` was called and that button `setMinimumWidth` values from the reference table at the top of this file are set.

- [ ] T069 On the **Sales** page, add 2 line items. Inspect the Remove buttons in the line-items table. Confirm full visibility. Repeat for **Purchases** and **Expenses**.

- [X] T070 On the **Reports** page, inspect the "Void" or action buttons in the Sales/Purchases History tables (if present as cell widgets). Confirm full visibility.

- [ ] T071 [P] Open the **Product dialog**. Confirm "Save" and "Cancel" are both fully visible with unclipped text. Click Cancel to close.

- [ ] T072 [P] Open the **Invoice Detail dialog** (from Reports or Sales History). Confirm "Void Invoice" (disabled or enabled depending on status) and "Close" are both fully visible.

- [ ] T073 [P] Open the **Expense Detail dialog**. Confirm all action buttons are fully visible.

- [ ] T074 [P] Open the **Change Password dialog**. Confirm "Change Password" and "Cancel" are both fully visible.

- [X] T075 Navigate to any page that has a **Backup / Restore** or **Settings** control visible in the main window chrome (sidebar, toolbar, or menu). Confirm all controls in that area are fully visible and not cropped. Fix any cropped control in `accounting_system/ui/main_window.py`.

---

### 9H — Color Contrast Audit

**Every text element must be readable against its background.**

WCAG AA minimum ratios: 4.5:1 for normal text, 3:1 for large text (18 pt+ or 14 pt bold+).

- [X] T076 In `accounting_system/ui/theme.py`, read the `LightTheme` colour values. For each foreground/background pairing below, manually verify the combination is readable (high contrast, not same-family hue at similar lightness). Fix any combination that looks unreadable by adjusting the foreground colour token — not the background. **Do not change the primary brand colour or the surface/background colours.**

  Pairings to verify:
  - `text_primary` on `surface` (card backgrounds) — main body text
  - `text_secondary` on `surface` — label text next to fields
  - `text_secondary` on `background` — page-level secondary text
  - `primary` (brand colour) on `surface` — invoice numbers, KPI values in primary colour
  - Table header text on header background
  - Selected row text on selected row background (`selection` colour token)
  - Placeholder text (Qt renders this at ~50% opacity of `text_primary` by default — verify it remains readable)
  - Disabled button text on disabled button background (Qt renders disabled at reduced opacity — verify still legible)

- [ ] T077 Launch the application and navigate to each page. Look specifically at any greyed-out or muted text (labels, placeholders, disabled controls, empty-state messages). If any text is so light it is difficult to read at normal screen brightness, increase its contrast by using `text_primary` instead of `text_secondary`, or by adjusting the `text_secondary` token value in `LightTheme` if it is globally too light.

---

### 9I — Reports Page Critical Evaluation

- [ ] T078 Navigate to the **Reports** page. Set it to a state with real data (at least 5 sales, 5 purchases, 5 expenses in the database). Look at the page critically for 60 seconds as if you were a first-time user. Ask: does this page immediately communicate what it contains? Are the six sections easy to distinguish? Is there unnecessary visual noise (extra borders, redundant labels, dense padding)? Write a one-sentence assessment. If the answer is "no, it still feels crowded or confusing", identify the single most impactful change and make it (e.g., increase the splitter handle width, increase inter-section spacing in the top card, reduce the number of visible controls in the summary card).

- [X] T079 On the Reports page, verify the horizontal splitter proportions: the left panel (Sales + Purchases + Expenses History) and the right panel (Top Products + Top Categories) should open at a ratio of approximately 60% left / 40% right at 1280×800. If the splitter opens at an unbalanced ratio, set initial sizes in the source file: `self.splitter.setSizes([768, 512])` (adjust numbers to match actual window content width). Read `reports_page.py` first and find the splitter widget.

---

### 9J — Dashboard Final Review

- [ ] T080 Navigate to the **Dashboard** with real data loaded (at least 5 products, 5 sales). Inspect the KPI row(s). Verify: all cards in a row are exactly the same height; cards have equal left and right margins from the window edge; the spacing between the KPI row and the table(s) below it is consistent with `theme._active.spacing_lg`. Fix any asymmetry found in `dashboard_page.py`.

- [X] T081 On the Dashboard, verify the Low Stock and Recent Transactions section titles match the same style as section titles on other pages (bold, 11 pt, `text_primary`). If they use a different style, correct the QLabel stylesheet in `dashboard_page.py` to match.

---

### 9K — Responsive Layout Final Review

- [X] T082 With the application open on the **Products** page showing 5+ products, slowly resize the window from 1280×800 down to 900×600. Watch continuously. If at any intermediate size a button disappears, a layout breaks, or a widget overlaps another, stop and record the window width at which it breaks. Fix the issue in the relevant source file. Common fixes: add `setMinimumWidth` to the window or page widget; remove any `setFixedWidth` on a layout container that prevents shrinking.

- [ ] T083 [P] Repeat T082 for the **Sales** page (with one line item visible in the table), the **Reports** page, and the **Dashboard**.

- [X] T084 Resize the application back to 1280×800. Verify the layout restores cleanly with no residual misalignment.

---

### 9L — Final Commercial UI Audit

**This is the gating task. No task after this may be skipped.**

- [ ] T085 Conduct a full end-to-end walkthrough of the entire application:
  1. Log in.
  2. View the Dashboard.
  3. Add a new product (via the Product dialog).
  4. Create and save a Sale invoice (at least 2 line items).
  5. Create and save a Purchase invoice (at least 2 line items).
  6. Create and save an Expense invoice (at least 2 line items).
  7. View the Reports page with data loaded.
  8. Open an Invoice Detail dialog and inspect the Void button state.
  9. Open the Change Password dialog.
  10. Close the application.
  
  During this walkthrough, evaluate the application holistically. Do not look for individual pixel issues — look for whether the application feels like a polished commercial product. Apply the standard: **"Would I be comfortable showing this to a client as finished software?"**

- [ ] T086 Based on the T085 walkthrough, identify up to 5 remaining visual issues (if any) — things that still look unpolished, inconsistent, or amateurish. For each issue, make the smallest possible change that fixes it without risk of regression. Document each change in a comment next to the fix (one line: `# Visual audit fix: <what and why>`).

- [ ] T087 After all fixes from T086 are applied, re-run the walkthrough from T085. The application passes the final audit when the answer to "Would I be comfortable showing this to a client as finished software?" is **yes** for every screen.

---

**MANDATORY GATE**: The feature is complete **only when T087 passes**. No implementation task completion, no checklist percentage, and no individual scenario pass substitutes for T087.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 2 (Foundational)**: Must complete before Phases 3–7. `apply_actions_column()` must exist in theme.py before any page file imports it.
- **Phases 3–7**: Can begin once Phase 2 is done. Each page/dialog is independent — they touch different files.
- **Phase 8 (Visual Review)**: Must be last among implementation phases. Depends on all Phases 3–7 complete.
- **Phase 9 (Visual Consistency Audit)**: Must be last of all. Depends on Phase 8 passing. Cannot be skipped or abbreviated.

### User Story Dependencies

- **US1 (Products, Phase 3)**: Depends only on Phase 2.
- **US2 (Forms, Phase 4)**: Depends only on Phase 2. Independent from US1.
- **US3 (Dashboard, Phase 5)**: Depends only on Phase 2. Independent from US1, US2.
- **US4 (Reports, Phase 6)**: Depends only on Phase 2. Independent from US1–US3.
- **US5 (Dialogs, Phase 7)**: Depends only on Phase 2. Independent from US1–US4.

### Parallel Opportunities

Phases 3, 4, 5, 6, and 7 can all run in parallel once Phase 2 is complete (they touch completely separate files). Within Phase 4, tasks for `sales_page.py`, `purchases_page.py`, and `expenses_page.py` can also run in parallel. Within Phase 9, sections 9B–9K can largely be run in parallel; 9L (T085–T087) must be last.

---

## Implementation Strategy

### MVP First (Phase 2 + Phase 3 only)

1. Complete Phase 2 (theme.py additions — T001, T002)
2. Complete Phase 3 (Products page — T003–T008)
3. **STOP and VALIDATE**: Launch app, check Products page — all action buttons visible, no clipping
4. Proceed to remaining phases if Products passes

### Incremental Delivery

1. Phase 2 → Phase 3 → validate Products → Phase 4 → validate Forms → Phase 5 → validate Dashboard → Phase 6 → validate Reports → Phase 7 → validate Dialogs → Phase 8 (functional review) → Phase 9 (commercial quality audit)

---

## Notes

- **Do not change**: Any method that saves, loads, calculates, or validates data. Only change UI construction code (layout setup, widget creation, style assignments).
- **Safe to change**: `__init__`, `_build_ui`, `_setup_ui`, or equivalent — the parts that create and arrange widgets.
- **Read before edit**: Always read the full target file before making changes (T003, T009, T013, T015, T018, T022, T026, T028, T031, T033 are explicit read tasks — do not skip them).
- **`[P]` tasks** = different files, no dependencies between them — safe to run simultaneously.
- **Constant values** are defined in `theme.py` and referenced via `theme._BTN_MIN_*` etc. — do not redeclare them in page files.
- **Import rule**: If a new PySide6 symbol is needed (e.g., `Qt`), add it to the existing `from PySide6.QtCore import ...` line — never add a new import line for a symbol that is already available in the same module.
- **Engineering Rules 1–3** (defined at the top of this file) override any task instruction that would produce hardcoded values, duplicated helpers, or a phase left in an unclean state. When in doubt, centralise first, then implement.
- **Regression rule**: A phase is not complete until its own acceptance criteria pass AND its regression check task (T002-X, T008-X, T017-X, T021-X, T025-X, T034-X) passes. Never carry a known regression into the next phase.
