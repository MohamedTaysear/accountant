# Store Accounting System — Implementation Plan

**Purpose of this document:** a phase-by-phase build roadmap derived from the approved `BLUEPRINT.md`. This is the input you will feed into Spec-Kit to author each phase's `spec.md` / `plan.md` / `tasks.md`. It contains no source code and no Spec-Kit artifacts.

**Governing rule for every phase (to be encoded in your Constitution):** *Every phase must leave the application in a fully runnable, manually testable state. No phase may merge a partially wired or broken feature.*

---

## Phase Overview

| Phase | Name | Milestone |
|---|---|---|
| 1 | Foundation, Shell & Auth | Full app runs end-to-end: login → main shell (placeholder pages) → change password / backup → logout |
| 2 | Products | Products fully manageable (CRUD, search, archive) |
| 3 | Purchases | Real stock can be built up via actual purchase invoices |
| 4 | Sales | Sales tested against real stock produced in Phase 3 |
| 5 | Dashboard & Reports | Full reporting, invoice detail/void/print, CSV export |
| 6 | Final Polish | Cross-cutting hardening only — no new screens |

Build order within each phase is strictly bottom-up: data access → business logic → UI — consistent with the blueprint's layering rules throughout.

---

## Phase 1 — Foundation, Shell & Auth

### Goal
Establish the entire technical foundation and the full application shell — navigation, authentication, and account maintenance — so that every later phase only ever has to *add a page's real content*, never build new plumbing.

### Files to Implement (in order)

| # | File | Purpose | Depends On |
|---|---|---|---|
| 1 | `config.py` | App-wide constants (paths, sizes, app info) | — |
| 2 | `database.py` | Connection, table creation for all 6 tables, **`backup_database()`** | config.py |
| 3 | `auth_db.py` | Raw SQL: `get_user()`, `count_users()`, `insert_user()`, `update_password()` | database.py |
| 4 | `auth.py` | `hash_password()`, `verify_password()`, `seed_default_admin()`, `check_login()`, `change_password()` | auth_db.py |
| 5 | `ui/change_password_dialog.py` | Modal: current/new/confirm password fields | auth.py |
| 6 | `ui/dashboard_page.py` *(placeholder)* | Empty/"Coming soon" page — replaced in Phase 5 | — |
| 7 | `ui/products_page.py` *(placeholder)* | Empty placeholder — replaced in Phase 2 | — |
| 8 | `ui/purchases_page.py` *(placeholder)* | Empty placeholder — replaced in Phase 3 | — |
| 9 | `ui/sales_page.py` *(placeholder)* | Empty placeholder — replaced in Phase 4 | — |
| 10 | `ui/reports_page.py` *(placeholder)* | Empty placeholder — replaced in Phase 5 | — |
| 11 | `ui/main_window.py` | Sidebar (Dashboard/Products/Sales/Purchases/Reports + Change Password/Backup Now/Logout), `QStackedWidget`, resizable (min 900×600) | all placeholder pages, change_password_dialog.py, database.py |
| 12 | `ui/login_window.py` | Username/password fields (auto-focus username), Enter-to-submit, opens Main Window on success | auth.py, main_window.py |
| 13 | `main.py` | `QApplication`, `initialize_database()`, `seed_default_admin()`, show Login Window, `app.exec()` | database.py, auth.py, login_window.py |

### File Dependency Diagram (this phase)
```
main.py
  ├─> database.py ─> config.py
  ├─> auth.py ─> auth_db.py ─> database.py
  └─> login_window.py
        ├─> auth.py
        └─> main_window.py
              ├─> dashboard_page.py (placeholder)
              ├─> products_page.py (placeholder)
              ├─> sales_page.py (placeholder)
              ├─> purchases_page.py (placeholder)
              ├─> reports_page.py (placeholder)
              ├─> change_password_dialog.py ─> auth.py
              └─> database.py (Backup Now)
```

### Manual Testing Checkpoint (must pass before Phase 2 starts)
- [ ] First run: `data/store.db` is created automatically; console/log confirms tables exist.
- [ ] Exactly one row exists in `Users` after first run (no duplicate seeding on second run).
- [ ] Login with correct default credentials succeeds → Main Window opens on Dashboard.
- [ ] Login with wrong password shows an error and does **not** open Main Window.
- [ ] Username field is focused automatically when Login Window opens.
- [ ] Sidebar navigation switches between all 5 placeholder pages with no crashes.
- [ ] Main Window can be resized smaller/larger; cannot shrink below 900×600.
- [ ] Change Password: wrong current password is rejected; correct current password + matching new/confirm succeeds; can log out and log back in with the new password.
- [ ] Backup Now: creates a timestamped `.db` copy under `data/backups/`; confirmation message shown.
- [ ] Logout returns to Login Window without closing the app; closing Login Window's "X" exits the app entirely.

### Exit Criteria
The application is fully launchable, securable, and navigable end-to-end. Nothing in later phases requires touching any file built in this phase except to wire a placeholder page to its real content.

---

## Phase 2 — Products

### Goal
Replace the Products placeholder with full product management — the foundation every later invoice screen depends on.

### Files to Implement (in order)

| # | File | Purpose | Depends On |
|---|---|---|---|
| 1 | `products_db.py` | Raw SQL: `insert_product()`, `update_product()`, `delete_product()` (guarded), `set_active()`, `search_products()` (name match), `get_active_products()`, `get_low_stock_products()`, `is_product_referenced()`, `get_categories()` (distinct category values for the editable dropdown) | database.py |
| 2 | `ui/product_dialog.py` | Add/Edit modal: Name, Category (editable QComboBox populated from `get_categories()`), Purchase Price, Selling Price, Stock Quantity, Reorder Level | products_db.py |
| 3 | `ui/products_page.py` *(replaces placeholder)* | Search bar (name only), "Show Inactive" checkbox, table (Name, Category, Purchase Price, Selling Price, Stock Quantity, Reorder Level, Status), Add/Edit/Delete-or-Deactivate actions | product_dialog.py, products_db.py |

### File Dependency Diagram (new this phase)
```
ui/products_page.py
  ├─> ui/product_dialog.py ─> products_db.py ─> database.py
  └─> products_db.py
```

### Manual Testing Checkpoint (must pass before Phase 3 starts)
- [ ] Add a product with all fields (Name, Category, prices, stock, reorder level) → appears in the table immediately with the correct category shown.
- [ ] Edit a product, including changing its category → changes persist after closing and reopening the app.
- [ ] Type a brand-new category name when adding a product → saves successfully; that category now appears in the dropdown when adding the next product.
- [ ] Delete an unused product → succeeds and disappears from the table.
- [ ] Deactivate a product → disappears from the default table view; appears when "Show Inactive" is checked; can be Reactivated.
- [ ] Search by partial product name → filters correctly.
- [ ] Validation: empty name, empty category, negative price, negative stock, negative reorder level are all rejected with clear messages.
- [ ] App still launches, logs in, and navigates through all other (still-placeholder) pages with no regressions from Phase 1.

### Exit Criteria
A real, persistent product catalog exists with categories and active/inactive state — everything Phase 3 (Purchases) needs to select products from.

---

## Phase 3 — Purchases

### Goal
Replace the Purchases placeholder with full purchase-invoice creation, enabling real stock to enter the system for the first time.

### Files to Implement (in order)

| # | File | Purpose | Depends On |
|---|---|---|---|
| 1 | `purchases_db.py` | Raw SQL: `insert_purchase_with_items()` (transaction: header + lines + stock increment + `purchase_price` update, via `lastrowid`-based invoice numbering), `get_purchase_by_id()`, `get_purchase_items()`, `get_all_purchases()` (optional date range), `get_next_invoice_number()`, `void_purchase()` | database.py, products_db.py |
| 2 | `logic/purchase_logic.py` | In-memory invoice building, line/subtotal calculation, quantity validation, calls into `purchases_db.py` for save/void | purchases_db.py, products_db.py |
| 3 | `ui/purchases_page.py` *(replaces placeholder)* | Auto invoice number/date, optional Supplier Name, active-product picker (auto-focus flow), line-items table, Clear Invoice (confirm if non-empty), Save Invoice, wait cursor on save | purchase_logic.py, products_db.py |

### File Dependency Diagram (new this phase)
```
ui/purchases_page.py
  └─> logic/purchase_logic.py
        ├─> purchases_db.py ─> database.py
        └─> products_db.py
```

### Manual Testing Checkpoint (must pass before Phase 4 starts)
- [ ] Create a multi-line purchase invoice (2+ products) with an optional supplier name → saves successfully.
- [ ] Invoice number generated as `PUR-000001` (and increments correctly on subsequent saves).
- [ ] After saving: each product's `stock_quantity` increased by the correct amount; `purchase_price` updated to the entered price.
- [ ] Quantity accepts decimals (e.g. 2.5).
- [ ] Save is blocked if invoice has zero line items.
- [ ] Clear Invoice with existing lines prompts for confirmation; with no lines, clears instantly.
- [ ] Only active products appear in the product picker (deactivate one in Products page, confirm it disappears from this picker).
- [ ] Wait cursor briefly appears during Save.
- [ ] Now go back to **Products page** and confirm: a product used in this invoice can no longer be hard-deleted (Delete action is replaced by Deactivate) — this closes the loop on the Phase 2 checkpoint that couldn't be tested yet.
- [ ] App still fully functional across Phase 1 and Phase 2 features with no regressions.

### Exit Criteria
Real stock now exists in the system from genuine purchase invoices — exactly what Phase 4 (Sales) needs to sell against without faking data.

---

## Phase 4 — Sales

### Goal
Replace the Sales placeholder with full sales-invoice creation, tested against the real stock levels Phase 3 produced.

### Files to Implement (in order)

| # | File | Purpose | Depends On |
|---|---|---|---|
| 1 | `sales_db.py` | Raw SQL: `insert_sale_with_items()` (transaction: header incl. discount/customer_name + lines + stock decrement, via `lastrowid`-based invoice numbering), `get_sale_by_id()`, `get_sale_items()`, `get_all_sales()` (optional date range), `void_sale()` (restores stock) | database.py, products_db.py |
| 2 | `logic/sales_logic.py` | In-memory invoice building, subtotal/discount/grand-total calculation, stock-availability validation, calls into `sales_db.py` for save/void | sales_db.py, products_db.py |
| 3 | `ui/sales_page.py` *(replaces placeholder)* | Auto invoice number/date, optional Customer Name, active-product picker (auto-focus flow), line-items table, Discount field, Grand Total, Clear Invoice (confirm if non-empty), Save Invoice, wait cursor on save | sales_logic.py, products_db.py |

### File Dependency Diagram (new this phase)
```
ui/sales_page.py
  └─> logic/sales_logic.py
        ├─> sales_db.py ─> database.py
        └─> products_db.py
```

### Manual Testing Checkpoint (must pass before Phase 5 starts)
- [ ] Create a multi-line sales invoice against products stocked in Phase 3 → saves successfully.
- [ ] Invoice number generated as `SAL-000001`.
- [ ] After saving: each sold product's `stock_quantity` decreased correctly.
- [ ] Attempt to sell more than available stock → blocked with a clear message before save.
- [ ] Apply a discount → Grand Total recalculates correctly (Subtotal − Discount); discount exceeding subtotal is rejected.
- [ ] Optional customer name saves and is retrievable.
- [ ] Save is blocked if invoice has zero line items.
- [ ] Only active products appear in the picker.
- [ ] Wait cursor briefly appears during Save.
- [ ] Cross-check: after this sale, the products page shows reduced stock; if stock now sits at/below `reorder_level`, note it (visually confirmed properly in Phase 5's Low Stock list).
- [ ] App still fully functional across Phases 1–3 with no regressions.

### Exit Criteria
Both halves of day-to-day inventory movement (Purchases in, Sales out) are real and working together correctly — the data Phase 5's reports will summarize is now genuine, not synthetic.

---

## Phase 5 — Dashboard & Reports

### Goal
Replace the Dashboard and Reports placeholders, and add the Invoice Detail Dialog — turning the real Sales/Purchases data from Phases 3–4 into summaries, history, and corrective actions (void).

### Files to Implement (in order)

| # | File | Purpose | Depends On |
|---|---|---|---|
| 1 | `logic/report_logic.py` | Aggregation functions accepting an optional date range: total sales, total purchases, total profit (active invoices only, discount-adjusted) | sales_db.py, purchases_db.py |
| 2 | `ui/invoice_detail_dialog.py` | Read-only Sales/Purchases invoice view (header, line items, discount/grand total), Void (with confirmation + stock-sufficiency check for purchases), Print, wait cursor on void/print | sales_db.py, purchases_db.py, sales_logic.py, purchase_logic.py |
| 3 | `ui/reports_page.py` *(replaces placeholder)* | Date-range filter (All Time/Today/Week/Month/Custom), 3 summary blocks, Sales/Purchases history tables (double-click → detail dialog), CSV export, wait cursor on export | report_logic.py, invoice_detail_dialog.py |
| 4 | `ui/dashboard_page.py` *(replaces placeholder)* | 6 summary cards (incl. Today's Profit, Total Profit), Low Stock list showing Name + Category + Current Stock + Reorder Level for active products at/below reorder level | products_db.py, sales_db.py, purchases_db.py, report_logic.py |

### File Dependency Diagram (new this phase)
```
ui/reports_page.py
  ├─> logic/report_logic.py ─> sales_db.py / purchases_db.py
  └─> ui/invoice_detail_dialog.py
        ├─> sales_db.py / purchases_db.py
        └─> logic/sales_logic.py / logic/purchase_logic.py (void)

ui/dashboard_page.py
  ├─> products_db.py (incl. low-stock query)
  ├─> sales_db.py / purchases_db.py
  └─> logic/report_logic.py
```

### Manual Testing Checkpoint (must pass before Phase 6 starts)
- [ ] Dashboard shows correct Total Products, Total Stock Value, Today's Sales/Purchases/Profit, Total Profit (All Time) — cross-check at least one figure by hand against the data created in Phases 3–4.
- [ ] Low Stock list shows only active products at/below their reorder level, including the Category column; deactivating a low-stock product removes it from the list.
- [ ] Reports: switching the date filter (Today/Week/Month/Custom/All Time) changes the summary totals and both history tables correctly.
- [ ] Custom range rejects From > To.
- [ ] Double-clicking a Sales or Purchases history row opens the Invoice Detail Dialog with correct header + line items + totals.
- [ ] Void a Sale → stock restored on the relevant products; sale shows "Voided" in history; excluded from totals on refresh.
- [ ] Void a Purchase where the stock has already been sold onward → blocked with a clear message.
- [ ] Void a Purchase where stock is still available → succeeds, stock reduced, totals updated.
- [ ] An already-voided invoice cannot be voided again (button disabled).
- [ ] Print opens the OS print dialog from the Invoice Detail Dialog without error.
- [ ] CSV export produces a valid file with the currently filtered rows.
- [ ] App still fully functional across Phases 1–4 with no regressions.

### Exit Criteria
All planned business functionality is complete and end-to-end correct. Only cross-cutting polish remains.

---

## Phase 6 — Final Polish

### Goal
Apply the remaining cross-cutting refinements from the blueprint that don't belong to any single screen — no new screens or files are introduced in this phase.

### Work Items (touch existing files only)

| Area | Files Touched | What Changes |
|---|---|---|
| Wait cursor coverage audit | `sales_page.py`, `purchases_page.py`, `reports_page.py`, `invoice_detail_dialog.py`, `main_window.py` | Confirm every Save/Void/Export/Print/Backup action wraps in `QApplication.setOverrideCursor(Qt.WaitCursor)` consistently |
| Keyboard-focus audit | `login_window.py`, `sales_page.py`, `purchases_page.py` | Confirm auto-focus behaviors (username on open; quantity after product pick; picker after line add) all work as specified |
| Confirmation Dialog Policy audit | `products_page.py`, `sales_page.py`, `purchases_page.py`, `invoice_detail_dialog.py`, `main_window.py` | Confirm exactly the documented set prompts (Delete, Deactivate, Void, Clear-if-non-empty) and exactly the documented set doesn't (Logout, Backup) |
| Resizing audit | `main_window.py` | Confirm minimum size holds, layouts don't break at the minimum, Login window remains fixed |
| Error handling audit | all files with DB/file I/O | Confirm every database call, file write (backup, CSV, print), and business-rule violation surfaces a friendly `QMessageBox`, never a raw traceback |
| Full regression pass | entire app | Walk every checkpoint from Phases 1–5 once more, end-to-end, in a single continuous session |

### Manual Testing Checkpoint (final sign-off)
- [ ] Full regression: repeat every checklist item from Phases 1–5 in one sitting against the finished app.
- [ ] Deliberately trigger at least one error in each category (bad input, simulated DB issue, business rule violation) and confirm no raw traceback ever reaches the user.
- [ ] Confirm app behaves identically after a full restart (close and reopen), including persisted data, default admin only seeded once, and backups folder intact.

### Exit Criteria
The application matches the approved blueprint in full, with no known regressions — ready to be considered the final v1.0 release.

---

## Notes for Spec-Kit Authoring

- Each phase above maps to one Spec-Kit feature folder (e.g. `001-foundation-shell-and-auth`, `002-products`, …) — use the **Goal** as the basis for `spec.md`'s primary user story, and the **Files to Implement** table as the basis for `tasks.md`.
- The **Manual Testing Checkpoint** for each phase doubles as a starting point for that phase's acceptance scenarios in `spec.md`.
- Phase 6 has no new files, so its Spec-Kit feature folder will lean heavily on `tasks.md` (audit/fix tasks) rather than new functional requirements in `spec.md`.
- The "always runnable" rule referenced throughout should be written once into `constitution.md` rather than restated per-phase `plan.md`.
