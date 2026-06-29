# Tasks: Dashboard & Reports

**Input**: Design documents from `specs/005-dashboard-reports/`

**References**:
- `specs/005-dashboard-reports/spec.md`
- `specs/005-dashboard-reports/plan.md`
- `specs/005-dashboard-reports/data-model.md`
- `specs/005-dashboard-reports/contracts/`
- `specs/005-dashboard-reports/research.md`
- `specs/005-dashboard-reports/quickstart.md`

**Architecture rules (NON-NEGOTIABLE)**:
- UI files (`ui/`) MUST NOT import `sqlite3` or contain SQL
- Logic files (`logic/`) MUST NOT contain raw SQL and MUST NOT import PySide6
- DB files (`*_db.py`) MUST NOT contain business rules — only parameterized SQL
- `Products.purchase_price` MUST NEVER be used in profit calculations — always use `SaleItems.purchase_price_at_sale`

---

## Phase 2: Foundational — New DB Query Functions and Report Logic

- [X] T001 [P] Add `get_product_counts()` to `accounting_system/products_db.py`
- [X] T002 [P] Add `get_inventory_value()` to `accounting_system/products_db.py`
- [X] T003 [P] Add `get_potential_stock_profit()` to `accounting_system/products_db.py`
- [X] T004 [P] Add `get_low_stock_count()` to `accounting_system/products_db.py`
- [X] T005 [P] Add `get_total_sales_amount()` to `accounting_system/sales_db.py`
- [X] T006 [P] Add `get_profit_components()` to `accounting_system/sales_db.py`
- [X] T007 [P] Add `get_recent_activity()` to `accounting_system/sales_db.py`
- [X] T008 [P] Add `get_top_selling_products()` to `accounting_system/sales_db.py`
- [X] T009 [P] Add `get_total_purchases_amount()` to `accounting_system/purchases_db.py`
- [X] T010 [P] Add `get_top_purchased_products()` to `accounting_system/purchases_db.py`
- [X] T011 Create `accounting_system/logic/report_logic.py` with all 9 functions

---

## Phase 3: US4 — Reports Page

- [X] T012 [US4] Create `accounting_system/ui/reports_page.py` with date filter bar and summary labels
- [X] T013 [US4] Implement `_apply_filter()` calling report_logic and updating summary labels
- [X] T014 [US4] Implement `_get_date_range()` with all 5 presets and custom validation

---

## Phase 4: US5, US7, US8 — Invoice Detail Dialog and History Tables

- [X] T015 [US5] Create `accounting_system/ui/invoice_detail_dialog.py` constructor
- [X] T016 [US5] Implement Sales invoice layout (6 columns including Cost Price and Profit/Line)
- [X] T017 [US5] Implement Purchases invoice layout (4 columns)
- [X] T018 [US7] Implement `_on_void()` for both sale and purchase types
- [X] T019 [US8] Implement `_on_print()` with QPrinter/QPrintDialog
- [X] T020 [US5] Add Sales History table and Purchases History table to reports_page.py
- [X] T021 [US5] Implement `_populate_history_tables()` storing invoice id in UserRole
- [X] T022 [US5] Implement double-click handlers opening InvoiceDetailDialog

---

## Phase 5: US1 — Dashboard

- [X] T023 [US1] Create `accounting_system/ui/dashboard_page.py` with Signal and `_build_ui()`
- [X] T024 [US1] Implement 10-card grid layout with all value labels
- [X] T025 [US1] Implement `_refresh()` calling all report_logic and products_db functions
- [X] T026 [US1] Implement `_refresh_low_stock()` with amber row color
- [X] T027 [US3] Implement `_refresh_recent_activity()` populating recent_table

---

## Phase 6: US2 — Low Stock Navigation

- [X] T028 [US2] Add `highlight_product(product_id)` to `accounting_system/ui/products_page.py`
- [X] T029 [US2] Wire `navigate_to_product` signal in `accounting_system/ui/main_window.py`

---

## Phase 8: US6 — Top Products (included in Phase 3)

- [X] T030 [US6] Top Selling Products panel added to reports_page.py layout
- [X] T031 [US6] Implement `_populate_top_products()` in reports_page.py

---

## Phase 9: US9 — CSV Export (included in Phase 3)

- [X] T032 [US9] Implement `_on_export_csv()` in reports_page.py with active-table tracking

---

## Phase 10: Polish

- [X] T033 Green styling for Today's Profit and Total Profit cards in dashboard_page.py
- [X] T034 Amber styling for Low Stock Count card and Low Stock list rows in dashboard_page.py
- [X] T035 Wait cursor coverage verified in invoice_detail_dialog.py void and print handlers
- [ ] T036 Run quickstart.md S1–S14 manual validation (requires running application)
