# Tasks: Expenses Management

**Input**: Design documents from `specs/006-expenses-management/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**Tests**: No test tasks generated (not requested in spec).

**Organization**: Tasks grouped by user story to enable independent implementation and validation of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks in the same phase)
- **[Story]**: Which user story this task belongs to (US1–US6, maps to spec.md)
- All source paths are relative to `accounting_system/`

---

## Phase 1: Setup

**Purpose**: Confirm the existing application runs cleanly before any changes are made.

- [x] T001 Launch the application (`python accounting_system/main.py`), log in, and verify all five existing pages (Dashboard, Products, Sales, Purchases, Reports) load without errors — document any pre-existing issues before touching any file

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema and full data-access + logic layers for Expenses. These must be complete before any UI work can begin.

**⚠️ CRITICAL**: No user story UI work can begin until this phase is complete.

- [x] T002 Add `CREATE TABLE IF NOT EXISTS Expenses` DDL to `initialize_database()` in `database.py` — fields: id, expense_number TEXT UNIQUE, expense_datetime TEXT, category TEXT, description TEXT, amount REAL, notes TEXT DEFAULT '', created_at TEXT — see `data-model.md` for exact DDL
- [x] T003 [P] Create `expenses_db.py` with all seven data-access functions per `contracts/expenses_db.md`: `insert_expense`, `update_expense`, `delete_expense`, `get_expense_by_id`, `get_all_expenses`, `get_expenses_for_report`, `get_distinct_categories`, `get_total_expenses` — no SQL in any other file
- [x] T004 [P] Add `get_today_expenses()`, `get_this_month_expenses()`, and `get_net_profit()` functions to `logic/report_logic.py` per `contracts/expenses_logic.md` — import `expenses_db`; no PySide6
- [x] T005 Create `logic/expenses_logic.py` with functions: `validate_expense`, `add_expense`, `update_expense`, `delete_expense`, `get_expenses`, `get_categories`, `get_expenses_for_report` per `contracts/expenses_logic.md` — delegates to `expenses_db`; no PySide6; no direct SQL

**Checkpoint**: All data-access and logic functions are importable and correct. Launch the app and confirm it still starts with no schema errors. Manually test via Python REPL if desired: `from expenses_db import insert_expense`.

---

## Phase 3: User Story 1 — Record a New Expense (Priority: P1) 🎯 MVP

**Goal**: The accountant can open the Expenses page, click Add Expense, fill in required fields, and save. The new expense appears in the table with a sequential EXP-XXXXXX number and current date/time.

**Independent Test**: Launch app → click Expenses in sidebar → click Add Expense → fill Category="Rent", Description="June rent", Amount=1500 → Save → verify EXP-000001 appears in the table with correct values.

- [x] T006 Create `ui/expense_dialog.py` with `ExpenseDialog(QDialog)` class per `contracts/expenses_page.md` — Add mode only (expense_id=None): QDateTimeEdit (default now_cairo()), plain QComboBox editable (categories loaded from `logic.expenses_logic.get_categories()`), QLineEdit description, QDoubleSpinBox amount (min=0.01, decimals=2), QLineEdit notes, Save/Cancel buttons — calls `logic.expenses_logic.add_expense()` on Save; shows QMessageBox.warning on ValueError; busy cursor around save; no autocomplete yet (added in Phase 4)
- [x] T007 Create `ui/expenses_page.py` with `ExpensesPage(QWidget)` per `contracts/expenses_page.md` — layout: Add Expense button (search box added in Phase 6; Edit/Delete added in Phase 5), QTableWidget 7 columns (Expense #, Date & Time, Category, Description, Amount, Notes, Actions), sorted expense_datetime DESC — `_load_expenses()` calls `logic.expenses_logic.get_expenses()`; `showEvent` calls `_load_expenses()`; Add button opens `ExpenseDialog` and reloads on Accepted; Actions column cells are empty placeholders for now (stubs to avoid index errors)
- [x] T008 Update `ui/main_window.py` — add `("Expenses", 5)` to nav_buttons list; import and instantiate `ExpensesPage` from `ui.expenses_page`; add it to `self.stack` at index 5 — leave "Expenses Report" (index 6) for Phase 8; existing indices 0–4 unchanged

**Checkpoint**: App runs. Expenses page accessible from sidebar. Can add an expense and see EXP-000001 in the table. Validation errors shown for blank Category, blank Description, Amount ≤ 0.

---

## Phase 4: User Story 2 — Smart Category Autocomplete (Priority: P2)

**Goal**: The Category field in ExpenseDialog shows previously used categories as case-insensitive suggestions. Typing a new category and saving makes it available for future suggestions automatically.

**Independent Test**: Add expense with Category="Fuel". Open Add Expense again — "Fuel" appears in dropdown. Type "fuel" (lowercase) — "Fuel" is suggested. Type "Packaging" (new) — no match; save; reopen dialog — "Packaging" now appears.

- [x] T009 Update `ui/expense_dialog.py` — attach a `QCompleter` to the category QComboBox with `Qt.CaseInsensitive` match mode (use `setCompleter` after `setEditable(True)`); populate completer model from `logic.expenses_logic.get_categories()` called at dialog open; after a successful save, do not reload categories in-dialog (parent page reload is sufficient)

**Checkpoint**: Open Add Expense dialog — dropdown shows existing categories. Typing partial name filters suggestions case-insensitively. New category saved once becomes available on next dialog open.

---

## Phase 5: User Story 3 — Edit and Delete an Expense (Priority: P2)

**Goal**: Each expense row has Edit and Delete action buttons. Edit opens the pre-filled dialog; Delete asks for confirmation then removes the row.

**Independent Test**: Add an expense. Click Edit — dialog opens with all fields pre-filled. Change Amount. Save. Table reflects new amount. Click Delete on another expense — confirmation dialog appears. Cancel → expense stays. Confirm → expense removed.

- [x] T010 Update `ui/expense_dialog.py` — add Edit mode: accept optional `expense_id: int` parameter; when provided, call `expenses_db.get_expense_by_id(expense_id)` at `__init__` to load data and pre-fill all fields; on Save call `logic.expenses_logic.update_expense(expense_id, ...)` instead of `add_expense`; dialog title changes to "Edit Expense" vs "Add Expense"
- [x] T011 Update `ui/expenses_page.py` — replace Actions column stubs with real per-row QWidget containing Edit and Delete QPushButton; store `row['id']` in each button via `setProperty('expense_id', row['id'])`; Edit button: open `ExpenseDialog(expense_id=id, parent=self)` and reload on Accepted; Delete button: show `QMessageBox.question` confirmation, on Yes apply busy cursor → `logic.expenses_logic.delete_expense(id)` → restore cursor → reload; on exception restore cursor + `QMessageBox.critical`

**Checkpoint**: Edit flow: open expense, change a field, save, verify table updates. Delete flow: confirm dialog appears, cancel keeps row, confirm removes row. All three existing CRUD operations verified end-to-end.

---

## Phase 6: User Story 4 — Search Expenses (Priority: P3)

**Goal**: A search box on the Expenses page filters the table in real time by Expense Number, Category, Description, or Notes.

**Independent Test**: Add expenses with varied categories. Type partial category name in search box — only matching rows shown. Clear search — all rows restored. Type an expense number — only that row shown.

- [x] T012 Update `ui/expenses_page.py` — add `QLineEdit` search box (placeholder "Search expenses…") above the table; connect `textChanged` signal to `_load_expenses(search=text or None)`; `_load_expenses` passes search string to `logic.expenses_logic.get_expenses(search)` which in turn calls `expenses_db.get_all_expenses(search)` — no changes needed to db layer (search param already implemented in T003)

**Checkpoint**: Typing in search box filters table live. Clearing restores all rows. Search is case-insensitive across all four fields.

---

## Phase 7: User Story 5 — Dashboard Expense KPIs (Priority: P2)

**Goal**: Three new cards appear on the Dashboard: "Today's Expenses", "This Month Expenses", "Net Profit". They update automatically when navigating back to the Dashboard after any expense change.

**Independent Test**: Record an expense. Navigate to Dashboard. Verify Today's Expenses shows the correct sum. Verify Net Profit = Total Profit − all-time Total Expenses. Verify existing Today's Profit / This Month Profit / Total Profit cards are unchanged.

- [x] T013 Update `ui/dashboard_page.py` — add three new QLabel attributes (`lbl_today_expenses`, `lbl_this_month_expenses`, `lbl_net_profit`) using the existing `_make_card()` helper; place at grid Row 2 cols 1, 2, 3 (Low Stock Count stays at Row 2 col 0); in `_refresh()` call `report_logic.get_today_expenses()`, `report_logic.get_this_month_expenses()`, `report_logic.get_net_profit()` and set label text; apply green color (`#2e7d32`) to Net Profit when positive, default bold when zero or negative — existing cards and their logic unchanged; `report_logic` already imported

**Checkpoint**: Navigate to Dashboard. Three new cards visible. Add an expense → navigate back to Dashboard → Today's Expenses and This Month Expenses reflect new amount, Net Profit decreases by same amount. Delete an expense → net values reverse. Existing profit cards unchanged throughout.

---

## Phase 8: User Story 6 — Expenses History Report (Priority: P3)

**Goal**: A dedicated "Expenses Report" page in the sidebar provides date filtering, category filtering, keyword search, a read-only Expense Detail dialog, and CSV export for all expense records.

**Independent Test**: Click Expenses Report in sidebar. Apply "This Month" date filter — correct expenses shown. Filter by category — only that category shown. Double-click a row — Expense Detail dialog opens with all fields. Export CSV — file matches visible rows.

- [x] T014 [P] Create `ui/expense_detail_dialog.py` with `ExpenseDetailDialog(QDialog)` per `contracts/expenses_report_page.md` — loads expense via `expenses_db.get_expense_by_id(expense_id)` at init; displays all fields as read-only QLabel pairs (Expense Number, Date & Time, Category, Description, Amount formatted as `{:,.2f}`, Notes, Created At); single "Close" button
- [x] T015 Create `ui/expenses_report_page.py` with `ExpensesReportPage(QWidget)` per `contracts/expenses_report_page.md` — date filter combo (Today/Yesterday/This Week/This Month/Custom Range) with From/To QDateEdit (calendar popup, enabled only for Custom Range), Apply button; category QComboBox populated from `expenses_db.get_distinct_categories()` with "All Categories" first item; search QLineEdit; Total Expenses summary label; QTableWidget 6 columns (Expense #, Date & Time, Category, Description, Amount, Notes), NoEditTriggers, SelectRows, Stretch headers; row id stored in col-0 Qt.UserRole; double-click opens `ExpenseDetailDialog`; `_apply_filter()` calls `logic.expenses_logic.get_expenses_for_report()`; Export to CSV button with busy cursor per `contracts/expenses_report_page.md`; `showEvent` reloads category combo and applies filter
- [x] T016 Update `ui/main_window.py` — add `("Expenses Report", 6)` to nav_buttons; import and instantiate `ExpensesReportPage` from `ui.expenses_report_page`; add to `self.stack` at index 6

**Checkpoint**: Expenses Report page accessible from sidebar. Date filter, category filter, and search all work independently and in combination. Double-click opens read-only detail dialog. CSV export matches visible rows.

---

## Phase 9: Polish & Validation

**Purpose**: Full end-to-end validation, regression checks, and any final adjustments.

- [x] T017 Execute all scenarios in `specs/006-expenses-management/quickstart.md` — Section 1 (CRUD), Section 2 (Smart Category), Section 3 (Search), Section 4 (Dashboard), Section 5 (Report + CSV), Section 6 (Restart Persistence), Section 7 (Regression) — document and fix any failures
- [x] T018 [P] Verify architecture compliance: confirm `expenses_db.py` has no PySide6 import; confirm `logic/expenses_logic.py` has no `sqlite3` import and no `database` import; confirm `ui/expenses_page.py` does not import `expenses_db` directly (only via `logic.expenses_logic`); confirm `ui/expenses_report_page.py` follows same rule
- [x] T019 [P] Verify Net Profit edge case: add expenses totalling more than all sales profit; confirm Net Profit card shows a negative value without crashing
- [x] T020 [P] Verify restart persistence: add 3 expenses, close the application, relaunch, confirm all 3 still appear and category suggestions include all used categories

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
  └── Phase 2 (Foundational) ← BLOCKS all UI phases
        ├── Phase 3 (US1 — Record Expense) ← MVP entry point
        │     └── Phase 4 (US2 — Smart Category) ← enhances Phase 3 dialog
        │           └── Phase 5 (US3 — Edit/Delete) ← extends Phase 3 page
        │                 └── Phase 6 (US4 — Search) ← extends Phase 3 page
        ├── Phase 7 (US5 — Dashboard KPIs) ← independent of Phase 3–6 UI
        └── Phase 8 (US6 — Expenses Report) ← independent of Phase 3–6 UI
              └── Phase 9 (Polish) ← requires all previous phases
```

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|-----------|----------------------|
| US1 — Record Expense | Phase 2 complete | US5 Dashboard, US6 Report |
| US2 — Smart Category | US1 (dialog must exist) | US5 Dashboard, US6 Report |
| US3 — Edit/Delete | US1 (page + dialog must exist) | US5 Dashboard, US6 Report |
| US4 — Search | US1 (page must exist) | US5 Dashboard, US6 Report |
| US5 — Dashboard KPIs | Phase 2 complete (report_logic.py) | US1–US4, US6 |
| US6 — Expenses Report | Phase 2 complete | US1–US5 |

### Parallel Opportunities

**Within Phase 2** (different files):
- T003 (`expenses_db.py`) and T004 (`report_logic.py` additions) can run in parallel

**After Phase 3 checkpoint**:
- Phase 7 (US5, T013 — `dashboard_page.py`) can run in parallel with Phase 4/5/6
- Phase 8 (US6, T014 + T015 — new files) can run in parallel with Phase 4/5/6

**Within Phase 8**:
- T014 (`expense_detail_dialog.py`) and T015 (`expenses_report_page.py`) can run in parallel (different files); T016 depends on T015

**Within Phase 9**:
- T018, T019, T020 are all independent checks and can run in parallel

---

## Parallel Example: After Phase 3 Checkpoint

```
# After US1 is complete, these can run in parallel:

Stream A (US2 + US3 + US4 — sequential, same files):
  T009 → T010 → T011 → T012

Stream B (US5 — dashboard):
  T013

Stream C (US6 — report):
  T014 [parallel with T015] → T016
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) — T001
2. Complete Phase 2 (Foundational) — T002–T005
3. Complete Phase 3 (US1) — T006–T008
4. **STOP and VALIDATE**: Add an expense, verify EXP-000001 in table
5. Proceed to remaining stories in priority order

### Incremental Delivery

| After Phase | Feature Delivered |
|-------------|-------------------|
| Phase 3 | Add expenses + view list |
| Phase 4 | Smart category autocomplete |
| Phase 5 | Edit + Delete expenses |
| Phase 6 | Live search |
| Phase 7 | Dashboard KPIs (Today's Expenses, This Month Expenses, Net Profit) |
| Phase 8 | Expenses History Report with CSV export |
| Phase 9 | Full validation pass + regression confirmed |

---

## Notes

- No test files generated (not requested in spec)
- [P] tasks operate on different files or are read-only checks — safe to run in parallel
- Each phase ends with a testable checkpoint that can be validated independently
- Build bottom-up within each phase: data access → logic → UI (already enforced by the phase structure above since T002–T005 precede all UI tasks)
- Avoid editing the same file in two parallel tasks — the phase structure above prevents this
- The busy/wait cursor (`QApplication.setOverrideCursor(Qt.WaitCursor)` / `restoreOverrideCursor()`) is required for all save, delete, and CSV export operations per the project constitution
