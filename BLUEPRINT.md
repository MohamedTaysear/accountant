# Store Accounting System — Complete Project Blueprint (MVP v1.0 — FINAL)

**Stack:** Python + PySide6 + SQLite | **Users:** Single local Admin account | **Scope:** One Windows PC, no network/cloud
**Release plan:** Single, permanent release — no v2 planned. All core daily-use accounting features must be included now.

---

## 1. Folder and File Structure

```
accounting_system/
│
├── main.py                      # Application entry point
├── config.py                    # App-wide constants (paths, sizes, app info)
│
├── database.py                  # SQLite connection, table creation, manual backup
├── auth_db.py                    # Raw SQL queries on Users table
├── products_db.py                # Raw SQL queries on Products table
├── sales_db.py                   # Raw SQL queries on Sales + SaleItems tables
├── purchases_db.py               # Raw SQL queries on Purchases + PurchaseItems tables
│
├── auth.py                       # Password hashing, login check, admin seeding, change password
│
├── logic/
│   ├── __init__.py
│   ├── sales_logic.py             # Sale total/discount calculation, stock reduction, voiding
│   ├── purchase_logic.py          # Purchase total calculation, stock increase, voiding
│   └── report_logic.py            # Totals/profit aggregation with date-range filtering
│
├── ui/
│   ├── __init__.py
│   ├── login_window.py             # Login screen
│   ├── main_window.py              # Main shell (sidebar + page switcher + logout + backup + change password)
│   ├── dashboard_page.py           # Dashboard screen (incl. Low Stock list)
│   ├── products_page.py            # Products list + search + add/edit/delete triggers
│   ├── product_dialog.py           # Add/Edit product popup (modal dialog)
│   ├── sales_page.py               # Sales invoice creation screen (incl. discount, customer name)
│   ├── purchases_page.py           # Purchases invoice creation screen (incl. supplier name)
│   ├── reports_page.py             # Reports screen (incl. date filter, history tables, CSV export)
│   ├── invoice_detail_dialog.py    # Read-only invoice view + Void + Print (Sales & Purchases)
│   └── change_password_dialog.py   # Change the single Admin account's password
│
└── data/
    ├── store.db                    # SQLite file (auto-created at runtime, not in source control)
    └── backups/                     # Manual backup copies land here (auto-created on first backup)
```

**Total source files: 21** (excluding `__init__.py` and runtime database/backup files).

---

## 2. Database Schema

### Users
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| username | TEXT | UNIQUE NOT NULL |
| password_hash | TEXT | NOT NULL |

*Exactly one row ever exists in this table. Password can be changed in-place via the Change Password screen — username and row identity never change.*

### Products
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL |
| category | TEXT | NOT NULL — product category for grouping (e.g. "Electronics", "Food & Beverages"). Categories are not a separate table; the distinct values present in this column define the category list dynamically. |
| purchase_price | REAL | NOT NULL, DEFAULT 0 |
| selling_price | REAL | NOT NULL, DEFAULT 0 |
| stock_quantity | REAL | NOT NULL, DEFAULT 0 — REAL to allow fractional quantities (e.g. 0.5) |
| reorder_level | REAL | NOT NULL, DEFAULT 5 — REAL to match `stock_quantity`'s type; triggers the Dashboard's Low Stock list when stock_quantity falls to or below this |
| is_active | INTEGER | NOT NULL, DEFAULT 1 — 1 = active, 0 = deactivated/archived. Lets a discontinued product be hidden from daily use (search, pickers) without deleting its history. |

*All products are treated as individual items (no unit of measure). Quantities are stored as REAL to support fractional amounts where needed.*

### Sales (invoice header)
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| invoice_number | TEXT | UNIQUE NOT NULL |
| customer_name | TEXT | NULLABLE — optional, plain text, no separate customer table |
| discount_amount | REAL | NOT NULL, DEFAULT 0 |
| total_amount | REAL | NOT NULL, DEFAULT 0 — the **grand total after discount** (sum of line subtotals − discount_amount) |
| status | TEXT | NOT NULL, DEFAULT 'active' — values: 'active' or 'voided' |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

### SaleItems (invoice lines)
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| sale_id | INTEGER | NOT NULL, FOREIGN KEY → Sales(id) |
| product_id | INTEGER | NOT NULL, FOREIGN KEY → Products(id) |
| quantity | REAL | NOT NULL — REAL to support decimal quantities |
| unit_price | REAL | NOT NULL — selling price at time of sale |
| purchase_price_at_sale | REAL | NOT NULL — purchase price at time of sale (for accurate profit) |
| subtotal | REAL | NOT NULL — quantity × unit_price (before any invoice-level discount) |

### Purchases (invoice header)
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| invoice_number | TEXT | UNIQUE NOT NULL |
| supplier_name | TEXT | NULLABLE — optional, plain text, no separate supplier table |
| total_amount | REAL | NOT NULL, DEFAULT 0 |
| status | TEXT | NOT NULL, DEFAULT 'active' — values: 'active' or 'voided' |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

### PurchaseItems (invoice lines)
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| purchase_id | INTEGER | NOT NULL, FOREIGN KEY → Purchases(id) |
| product_id | INTEGER | NOT NULL, FOREIGN KEY → Products(id) |
| quantity | REAL | NOT NULL — REAL to support decimal quantities |
| unit_price | REAL | NOT NULL — purchase price at time of purchase |
| subtotal | REAL | NOT NULL — quantity × unit_price |

**Relationships:**
- `Sales (1) → (many) SaleItems`, `SaleItems.product_id → Products.id`
- `Purchases (1) → (many) PurchaseItems`, `PurchaseItems.product_id → Products.id`
- `Users` has no relationships (standalone, single row)

**Note on Sales discount math:** line-item `subtotal` values are stored pre-discount (so per-line history is accurate); the invoice-level `discount_amount` is subtracted once at the header level to produce `total_amount`. The Invoice Detail Dialog displays: Subtotal (sum of lines) → Discount → Grand Total, so the breakdown is always visible without needing extra stored columns.

---

## 3. Screen Descriptions & Layout

### 3.1 Login Window
- Small fixed-size window (per `config.py`: 400×250).
- Centered layout: app title/logo label, username field, password field (masked), Login button, status/error label (hidden until needed).
- Enter key in password field triggers login, same as clicking the button.

### 3.2 Main Window (Shell)
- Fixed-size main window (1100×700).
- Left sidebar: navigation buttons — Dashboard, Products, Sales, Purchases, Reports — plus, separated near the bottom: **Change Password**, **Backup Now**, and **Logout**.
- Right side: a `QStackedWidget` holding all 5 page widgets; sidebar buttons switch the visible page.
- **Backup Now** does not navigate anywhere — it immediately copies the database file (see Section 6) and shows a confirmation `QMessageBox` with the backup's file path.
- **Change Password** opens `change_password_dialog.py` as a modal popup.

### 3.3 Dashboard Page
- Summary cards/labels: Total Products, Total Stock Value, Today's Sales Total, Today's Purchases Total, **Today's Profit**, Total Profit (All Time).
- Today's Profit reuses the same `report_logic.py` profit function as Total Profit, just called with today's date as both the start and end of the range — no new logic, just one more call with a different parameter.
- **Low Stock list**: a read-only list/table below the cards showing every product where `stock_quantity <= reorder_level` (Name, Category, Current Stock, Reorder Level). Only considers active products. Empty/hidden if nothing is low.
- All values reuse existing `*_db.py` and `report_logic.py` functions — no duplicate logic.
- Read-only, refreshes each time the page is shown.

### 3.4 Products Page
- Top bar: search box (filters by **name** as you type or on Enter) + "Add Product" button + a "Show Inactive" checkbox (off by default — deactivated products are hidden from daily use unless explicitly shown).
- Center: table view listing products — Name, Category, Purchase Price, Selling Price, **Profit/Unit** (read-only, calculated as Selling Price − Purchase Price, never stored in the database), **Stock Profit** (read-only, calculated as Profit/Unit × Stock Quantity, never stored in the database), Stock Quantity, Reorder Level, Status (Active/Inactive).
- Row actions: Edit, and either **Delete** (only enabled for products never used in any invoice) or **Deactivate/Activate** (for products that already have invoice history — replaces Delete for those rows, since their data can't be removed without breaking past invoices).
- Add/Edit opens `product_dialog.py` as a modal popup.

### 3.5 Product Dialog (Add/Edit popup)
- Modal dialog with fields: Name, Category, Purchase Price, Selling Price, Stock Quantity (accepts decimals), Reorder Level.
- **Category** is an editable `QComboBox`: it lists all existing categories (fetched from the distinct values already in the `Products` table via `products_db.get_categories()`) so the user can select one quickly. The user may also type a new category name directly — no separate management screen or extra dialog is needed. The new category is immediately available in future dropdowns once the product is saved.
- Save and Cancel buttons.
- Same dialog reused for both Add (fields empty/defaulted) and Edit (fields pre-filled).

### 3.6 Sales Page
- Top: invoice number (auto-generated, read-only display), date (auto, read-only), and an optional Customer Name text field.
- Product selection row: dropdown/search to pick a product, quantity input (accepts decimals), "Add to Invoice" button. The picker shows **active products only** (see Section 6) — a discontinued product can't be sold until it's reactivated on the Products page.
- Middle: invoice line-items table (Product, Quantity, Unit Price, Subtotal) with ability to remove a line.
- Bottom: Subtotal (auto-calculated, read-only), Discount input field, Grand Total (auto-recalculated as Subtotal − Discount), a **"Clear Invoice"** button (confirms first if any lines exist), and "Save Invoice" button.

### 3.7 Purchases Page
- Top: invoice number (auto-generated, read-only), date (auto, read-only), and an optional Supplier Name text field.
- Product selection row, line-items table, auto-calculated total, a **"Clear Invoice"** button (confirms first if any lines exist), and Save Invoice button — same pattern as Sales (no discount field here; purchase pricing is entered directly per line).
- The product picker shows **active products only** — same rule as Sales (see Section 6). To restock a discontinued item, the user must first reactivate it on the Products page.
- Functionally increases stock and updates each product's `purchase_price` instead of decreasing stock.

### 3.8 Reports Page
- **Date filter** at the top: a dropdown — All Time / Today / This Week / This Month / Custom Range — with two date pickers that only enable when "Custom Range" is selected, plus an "Apply" button.
- Three summary blocks below the filter: Total Sales, Total Purchases, Total Profit — all computed over the selected range, **active invoices only**.
- Below the summaries: two read-only tables —
  - **Sales History**: Invoice Number, Date, Customer, Total Amount, Status (filtered by the same date range, newest first, voided ones marked "Voided").
  - **Purchases History**: Invoice Number, Date, Supplier, Total Amount, Status (same pattern).
- Double-clicking a row opens that invoice in the **Invoice Detail Dialog** (Section 3.9).
- An **"Export to CSV"** button exports the currently filtered history table (whichever is selected/visible) to a `.csv` file via a standard Save File dialog — using Python's built-in `csv` module, no new dependency.

### 3.9 Invoice Detail Dialog
- Modal, read-only dialog. One reusable dialog works for both Sales and Purchases invoices (driven by an invoice type + id passed in).
- Displays: Invoice Number, Date, Status, Customer/Supplier Name (if set), a line-items table (Product, Quantity, Unit Price, Subtotal), and for Sales additionally Subtotal → Discount → Grand Total (for Purchases, just Grand Total, since there is no discount concept there).
- Contains a **"Void Invoice"** button (enabled only if active; confirmation required) and a **"Print"** button that opens Qt's standard print dialog (`QPrinter`/`QPrintDialog`) to print or "print to PDF" the currently displayed details — no custom invoice template engine, just printing what's already on screen.
- Once voided, the Void button is disabled — an invoice can only be voided once.
- Closing the dialog returns to the Reports page, refreshing the history tables and summary totals to reflect any change.

### 3.10 Change Password Dialog
- Modal dialog with three fields: Current Password, New Password, Confirm New Password.
- Save and Cancel buttons.
- On Save: verifies Current Password against the stored hash, checks New Password and Confirm New Password match and meet the minimum length rule, then updates the stored hash. Shows a success or error message and closes on success.

---

## 4. Navigation Flow

```
[App Start]
     │
     ▼
[Login Window] ──(invalid credentials)──► stay on Login, show error
     │ (valid credentials)
     ▼
[Main Window opens] ──► Login Window closes
     │
     ▼
[Dashboard Page]  (default page shown after login)
     │
     ├──► Products Page ──► Product Dialog (Add/Edit) ──► back to Products Page
     ├──► Sales Page
     ├──► Purchases Page
     ├──► Reports Page ──► Invoice Detail Dialog (view + optional Void + Print) ──► back to Reports Page
     │
     ├──► Change Password Dialog (from sidebar, any page) ──► closes back to whatever page was active
     ├──► Backup Now (from sidebar, any page) ──► confirmation popup only, no navigation
     │
     ▼ (Logout button clicked, any page)
[Main Window closes] ──► [Login Window reopens]
```

- Navigation between Dashboard/Products/Sales/Purchases/Reports is via the sidebar — all are siblings, no nesting.
- Change Password and Backup Now are accessible from any page without leaving it (Backup Now doesn't even open a new window).
- Logout always returns to the Login Window, never closes the whole application.
- Closing the Login Window's "X" button (without logging in) exits the application entirely.

---

## 5. Features Per Screen

| Screen | Features |
|---|---|
| Login | Enter username/password, validate against DB, show error on failure, open Main Window on success |
| Dashboard | View read-only summary metrics (incl. Total Profit); view Low Stock list |
| Products | List all, search/filter by name, add, edit, delete (with confirmation); track category, reorder level; archive/restore inactive products |
| Sales | Build multi-line invoice, optional customer name, auto subtotal, apply discount, auto grand total, auto stock reduction, save with auto-generated invoice number |
| Purchases | Build multi-line invoice, optional supplier name, auto total, auto stock increase, auto-update product cost, save with auto-generated invoice number |
| Reports | Filter by date range; view total sales, total purchases, total profit; browse Sales/Purchases history tables; export history to CSV; open any invoice's full details |
| Invoice Detail Dialog | View read-only invoice breakdown (header, line items, discount/grand total); Void Invoice (with confirmation); Print |
| Change Password | Change the single Admin account's password (current password required) |
| Backup Now (sidebar action) | One-click copy of the live database file to a timestamped backup file |

---

## 6. Business Logic

### Authentication
- On startup, if `Users` table is empty, silently create one Admin row with a securely hashed (salted SHA-256) password.
- Login: fetch the single user row by username, verify password hash. No lockouts/throttling needed for a single local user.
- **Change Password**: verify the entered current password against the stored hash; if correct, hash the new password and overwrite `password_hash` on the same row. The username and row id never change — there is still and will only ever be one user row.

### Products
- Add: insert new row — Name (required), Category (required), prices ≥ 0, stock ≥ 0 (decimal allowed), reorder level ≥ 0 (decimal allowed), `is_active = 1` by default.
- Edit: update existing row by id.
- Delete: only allowed if the product has never been used in any `SaleItems`/`PurchaseItems` row — otherwise the row's Delete action is replaced with **Deactivate** (sets `is_active = 0`) instead, hiding it from search/pickers without touching invoice history. A deactivated product can be **Reactivated** at any time (sets `is_active = 1` again).
- Search: filter the products list by **name** (case-insensitive partial match). Inactive products are excluded from results unless "Show Inactive" is checked.
- **Category autocomplete**: `products_db.get_categories()` returns the list of distinct category values currently in the Products table, used to populate the editable `QComboBox` in the Product Dialog. No separate category table exists — the live set of categories emerges from the data itself.
- **Low Stock detection**: an *active* product qualifies whenever `stock_quantity <= reorder_level`; used by the Dashboard's Low Stock list (simple `SELECT` with a `WHERE` clause, no extra table).
- **Active-only picker rule**: `is_active` is treated as one global rule, not a per-screen one — a single `products_db.py` function (`get_active_products()`) returns only active products, and is reused identically by both the Sales and Purchases product pickers. An inactive product cannot be sold *or* purchased; it must be reactivated on the Products page first. This keeps the meaning of "inactive" consistent everywhere in the app rather than having different exceptions per screen.

### Sales
- User builds an invoice in memory (list of line items) before saving.
- When adding a line: validate requested quantity (can be decimal) ≤ current `stock_quantity` of that product.
- Subtotal = quantity × product's current `selling_price` (captured at add-time).
- Invoice Subtotal = sum of all line subtotals. Discount is entered once at the invoice level. Grand Total = Subtotal − Discount.
- **Invoice numbering**: generated as `SAL-000001`, `SAL-000002`, etc. — prefix + zero-padded sequence, based on `MAX(id) + 1` from the `Sales` table.
- A "Clear Invoice" button resets the in-progress line-items list back to empty (confirmation required only if at least one line exists) — purely a UI-state reset, no database interaction.
- On Save: generate a unique invoice number, insert one `Sales` row (storing `total_amount` = Grand Total, `discount_amount`, and optional `customer_name`) + one `SaleItems` row per line, and **decrement** `Products.stock_quantity` for each line by the sold quantity. Single transaction.
- `purchase_price_at_sale` is captured from the product's current purchase price at save-time, for historical profit accuracy.

**Voiding a Sale:**
- Only allowed if the sale's current `status` is `'active'`.
- Sets `Sales.status = 'voided'`.
- For every related `SaleItems` row, **adds the quantity back** to `Products.stock_quantity` (reversing the original reduction).
- Wrapped in a single transaction (status update + all stock restorations succeed together, or none do).
- Voided sales are excluded from Reports/Dashboard totals but remain visible in the Sales History table for audit purposes.
- No stock-sufficiency check is needed here — restoring stock can never make a quantity invalid.

### Purchases
- Same in-memory invoice-building pattern as Sales, with an optional `supplier_name` instead of a discount.
- Subtotal = quantity (can be decimal) × purchase price entered for that line.
- **Invoice numbering**: generated as `PUR-000001`, `PUR-000002`, etc. — same pattern as Sales, distinct prefix.
- A "Clear Invoice" button works the same way as on the Sales page.
- On Save: generate a unique invoice number, insert one `Purchases` row + one `PurchaseItems` row per line, **increment** `Products.stock_quantity` for each line by the purchased quantity, **and automatically update `Products.purchase_price`** to the price entered on this invoice line. All of this happens in a single transaction.
- This auto-update keeps product cost data current with zero extra steps for the user, and does not affect historical accuracy: `SaleItems.purchase_price_at_sale` already freezes the cost at the time of each past sale, fully decoupled from the live `Products.purchase_price`.

**Voiding a Purchase:**
- Only allowed if the purchase's current `status` is `'active'`.
- For every related `PurchaseItems` row, validates that `Products.stock_quantity >= quantity` (i.e. that stock from this purchase hasn't already been sold onward). If any line fails this check, the void is **blocked entirely** with a clear message (e.g. "Cannot void: some of this stock has already been sold").
- If validation passes for all lines: sets `Purchases.status = 'voided'` and **subtracts the quantity** from `Products.stock_quantity` for each line — all in a single transaction.
- Voided purchases are excluded from Reports/Dashboard totals but remain visible in the Purchases History table for audit purposes.
- Note: voiding does **not** revert `Products.purchase_price` to a prior value (tracking price history is out of scope — see Section 12).

### Reports
- All totals accept an optional date range (`start_date`, `end_date`); "All Time" simply omits the `WHERE` date clause.
- Total Sales = `SUM(Sales.total_amount) WHERE status = 'active' [AND created_at BETWEEN ...]`.
- Total Purchases = `SUM(Purchases.total_amount) WHERE status = 'active' [AND created_at BETWEEN ...]`.
- Total Profit = `SUM(SaleItems.subtotal) − SUM(SaleItems.quantity × SaleItems.purchase_price_at_sale) − SUM(Sales.discount_amount)`, computed only over `SaleItems`/`Sales` rows with `status = 'active'`, within the selected range. (Discount is subtracted at the aggregate level since it's stored per-invoice, not per-line.)
- All calculated live via SQL aggregate queries — no separate profit table needed.
- History tables list **all** invoices regardless of status within the selected range (so voided ones remain visible for audit purposes), with a Status column distinguishing them.
- CSV export simply writes whichever history table is currently on screen (already filtered) to a file — no separate export logic or formatting engine.

### Database Maintenance
- **Backup Now**: copies the live `data/store.db` file to `data/backups/store_backup_YYYYMMDD_HHMMSS.db` using `shutil.copy2` (preserves timestamps). Creates the `backups` folder if it doesn't exist. Purely additive and safe — never touches or deletes the live database. Restoring is a manual, outside-the-app step (copy a backup file over `store.db` via Windows Explorer while the app is closed) — no in-app restore flow in v1. No pre-confirmation needed (nothing destructive to protect against) — a success/failure `QMessageBox` after the fact is sufficient.

### UI Responsiveness (Wait Cursor)
- For operations that touch the disk or take a noticeable moment — Save Invoice, Void Invoice, CSV Export, Print, and Backup Now — the application switches to a busy/wait cursor (`QApplication.setOverrideCursor(Qt.WaitCursor)`) for the duration of the call, then restores the normal cursor. This is a few lines wrapped around each action, not a separate progress-tracking system — a full progress bar/modal dialog would be unnecessary complexity for operations that complete in a fraction of a second on local hardware.

---

## 7. Validation Rules

### Login Form
- Username and password both required (non-empty, trimmed).

### Change Password Dialog
- Current Password: required, must match the stored hash.
- New Password: required, minimum length (e.g. 4 characters — kept low since this is a single local user, not a public-facing system).
- Confirm New Password: must exactly match New Password.

### Product Dialog
- Name: required, non-empty, max reasonable length (e.g. 100 chars).
- Category: required, non-empty. The user may select an existing category from the dropdown or type a new one. No additional uniqueness or format constraints — any non-empty string is valid.
- Purchase Price: required, numeric, ≥ 0.
- Selling Price: required, numeric, ≥ 0. (Warn, but don't block, if selling price < purchase price.)
- Profit/Unit: not a user-entered field — calculated dynamically in the UI as Selling Price − Purchase Price and displayed read-only in the Products table. Never stored in the database.
- Stock Profit: not a user-entered field — calculated dynamically in the UI as Profit/Unit × Stock Quantity and displayed read-only in the Products table immediately after Profit/Unit. Never stored in the database.
- Stock Quantity: required, numeric (decimals allowed), ≥ 0.
- Reorder Level: required, numeric (decimals allowed), ≥ 0.

### Sales Page (per line before adding)
- A product must be selected (only active products are selectable — see Section 6).
- Quantity: required, numeric (decimals allowed), > 0.
- Quantity must not exceed the product's current available stock.
- Invoice must have at least one line item before "Save Invoice" is enabled/allowed.
- Customer Name: optional, no format restriction.
- Discount: numeric, ≥ 0, and must not exceed the invoice Subtotal (Grand Total can never go negative).

### Purchases Page (per line before adding)
- A product must be selected (only active products are selectable — same rule as Sales, see Section 6).
- Quantity: required, numeric (decimals allowed), > 0.
- Unit price: required, numeric, ≥ 0.
- Invoice must have at least one line item before saving.
- Supplier Name: optional, no format restriction.

### Reports Date Filter
- When "Custom Range" is selected: From date must be ≤ To date.

### Invoice Detail Dialog / Void Action
- Void button is only enabled when the invoice's status is `'active'` (already-voided invoices cannot be voided again).
- Voiding always requires an explicit confirmation prompt ("Are you sure you want to void invoice #...?") before any database change happens.
- Voiding a Purchase additionally validates that enough stock remains for every line item before allowing the void; if not, the action is blocked with a specific error message rather than partially applied.

### Confirmation Dialog Policy (consolidated)
A confirmation prompt is shown **only** where an action is destructive or could silently discard real work:
| Action | Confirmation? | Reasoning |
|---|---|---|
| Delete Product | **Yes** | Irreversible. |
| Deactivate Product | **Yes** (lightweight) | Removes it from daily pickers; easily reversible (Reactivate), but still worth a quick check. |
| Void Invoice | **Yes** | Changes financial history and stock; already specified above. |
| Clear/Reset Invoice (Sales or Purchases) | **Yes, only if at least one line item exists** | Could silently discard unsaved work. |
| Logout | **No** | All data is already saved; logging out loses nothing. Confirming a frequent, harmless action is just friction. |
| Backup Now | **No** (pre-action) | Purely additive — nothing is at risk. A success/failure message afterward is enough. |

---

## 8. User Workflow (Login to Logout)

1. User launches the app → Login Window appears.
2. User enters username/password → clicks Login (or presses Enter).
3. Credentials validated against the single `Users` row.
4. On success: Main Window opens on the Dashboard page; Login Window closes.
5. User navigates freely between Dashboard / Products / Sales / Purchases / Reports via the sidebar; checks Low Stock list; may change their password or trigger a backup at any time.
6. User performs daily tasks: adds products (assigning each to a category), records sales (optionally with a discount/customer name) and purchases (optionally with a supplier name), checks reports for a chosen date range, exports a report to CSV if needed, opens/prints/voids a past invoice if a mistake needs correcting.
7. User clicks Logout → Main Window closes, Login Window reappears (session ends, no data is lost — everything is already saved in SQLite per action).
8. User may log back in or close the Login Window to exit the application entirely.

---

## 9. Application Startup & Shutdown Flow

**Startup (`main.py`):**
1. Create the `QApplication` instance.
2. Call `database.initialize_database()` → ensures all tables exist.
3. Call `auth.seed_default_admin()` → ensures the one Admin row exists.
4. Show the Login Window.
5. Start the Qt event loop (`app.exec()`).

**Shutdown:**
- Normal exit: user closes the Main Window or Login Window → Qt event loop ends → `sys.exit()`.
- No special cleanup is required: every database action opens, commits, and closes its own short-lived connection immediately, so there is never an open connection or unsaved in-memory state to flush on exit.

---

## 10. Error Handling Strategy

- **Database errors** (e.g. SQLite `IntegrityError`, locked file): caught at the point of the query call, surfaced to the calling logic/UI layer as a clear message, shown via a `QMessageBox` — the app never crashes silently.
- **Validation errors** (bad input): caught before any database call is made, shown inline or via `QMessageBox`, database is never touched with invalid data.
- **Business rule violations** (e.g. selling more than available stock, deleting a referenced product, voiding a purchase whose stock is already sold): caught in the `logic/` layer, surfaced as a friendly `QMessageBox` warning — never a raw Python traceback shown to the user.
- **Backup errors** (e.g. disk full, permissions issue): caught around the `shutil.copy2` call, shown as a friendly error rather than crashing.
- **Unexpected errors:** a top-level `try/except` around critical actions (login, save invoice, void invoice, backup) to prevent any unhandled exception from crashing the whole app; logs the technical detail to the console for the developer, shows a generic friendly message to the user.
- General principle: **fail safely and visibly to the user, never silently and never with a raw stack trace.**

---

## 11. Database Interaction Flow

```
UI Page (e.g. sales_page.py)
   │  collects user input, calls logic layer
   ▼
Logic File (e.g. sales_logic.py)
   │  validates, calculates totals/discount, decides stock changes
   ▼
DB File (e.g. sales_db.py, products_db.py)
   │  executes raw SQL (INSERT/UPDATE/SELECT)
   ▼
database.py
   │  provides the actual SQLite connection (and manual backup)
   ▼
data/store.db
```

- UI files **never** import `sqlite3` or call `database.py` directly — they always go through a `logic/` or `*_db.py` file (the one exception: `main_window.py` calls `database.backup_database()` directly for the Backup Now action, since that's a connection-level/file-level operation, not a business-logic one).
- `*_db.py` files **never** contain business rules — only parameterized SQL queries (preventing SQL injection by construction).
- Multi-step operations (e.g. saving a sales invoice = insert header + insert lines + update stock) are wrapped in a single transaction (commit only after all steps succeed; rollback on any failure) to keep the database consistent.

---

## 12. Future Extension Points (not implemented now)

- Multiple user accounts with roles/permissions (cashier vs admin).
- Tax/VAT calculation on invoices (explicitly excluded from this release by decision).
- Exporting invoices/reports to PDF directly (Print-to-PDF via the OS print dialog already covers this informally).
- Editing a saved invoice's contents (Voiding is implemented; in-place editing is not — to correct a mistake, void and create a new correct invoice).
- Partial returns (returning some, not all, items from a sale) — the Void-and-recreate workflow covers corrections adequately for a single-user app.
- Search/filter/sort on the Reports invoice history tables beyond the date range filter.
- Tracking purchase price *history* over time (currently only the single latest `purchase_price` is kept; voiding a purchase does not restore a prior price).
- A dedicated Customer/Supplier database with contact details, balances, or credit tracking (current scope is a plain optional text field only).
- A dedicated Category management screen (the current design derives categories dynamically from product data — a future management screen could allow renaming or merging categories).
- In-app restore-from-backup flow (manual file copy is sufficient for v1).
- Barcode scanner integration, multi-branch/warehouse tracking, cloud sync/backup, or any multi-user/networked feature.
- **Status bar** (logged-in user / DB connection status / current date / app version) — considered and explicitly rejected for v1: at single-user, single-local-database scale, "logged-in user" never changes, "DB connected" has no realistic failure mode worth surfacing, and "current date" already appears on the Sales/Purchases pages. Would add a permanent UI element of mostly decorative value.

---

## 13. File Dependency Diagram

```
main.py
  ├──> config.py
  ├──> database.py
  ├──> auth.py
  └──> ui/login_window.py

ui/login_window.py
  ├──> auth.py
  └──> ui/main_window.py   (opened on successful login)

ui/main_window.py
  ├──> ui/dashboard_page.py
  ├──> ui/products_page.py
  ├──> ui/sales_page.py
  ├──> ui/purchases_page.py
  ├──> ui/reports_page.py
  ├──> ui/change_password_dialog.py
  └──> database.py            (Backup Now action)

ui/products_page.py
  ├──> ui/product_dialog.py
  └──> products_db.py

ui/product_dialog.py
  └──> products_db.py   (get_categories() to populate the category dropdown)

ui/sales_page.py
  ├──> logic/sales_logic.py
  └──> products_db.py   (get_active_products(), to populate product picker)

ui/purchases_page.py
  ├──> logic/purchase_logic.py
  └──> products_db.py   (get_active_products(), same function as Sales — see Section 6)

ui/reports_page.py
  ├──> logic/report_logic.py
  └──> ui/invoice_detail_dialog.py   (opened when a history row is selected)

ui/invoice_detail_dialog.py
  ├──> sales_db.py        (fetch sale + line items, when type = sale)
  ├──> purchases_db.py    (fetch purchase + line items, when type = purchase)
  ├──> logic/sales_logic.py      (void_sale, when type = sale)
  └──> logic/purchase_logic.py   (void_purchase, when type = purchase)

ui/change_password_dialog.py
  └──> auth.py

ui/dashboard_page.py
  ├──> products_db.py    (incl. low-stock query)
  ├──> sales_db.py
  ├──> purchases_db.py
  └──> logic/report_logic.py   (Total Profit card)

logic/sales_logic.py
  ├──> sales_db.py
  └──> products_db.py

logic/purchase_logic.py
  ├──> purchases_db.py
  └──> products_db.py

logic/report_logic.py
  ├──> sales_db.py
  └──> purchases_db.py

auth.py
  └──> auth_db.py

auth_db.py        ──> database.py
products_db.py    ──> database.py
sales_db.py        ──> database.py
purchases_db.py    ──> database.py
database.py         ──> config.py
```

**Rule of thumb:** dependencies only ever point downward/inward (UI → Logic → DB-specific → database.py → config.py). Nothing at the bottom ever imports something above it — this is what keeps the architecture free of circular imports and easy to reason about.

---

## 14. Overall Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                          UI LAYER                            │
│   login_window | main_window | dashboard_page                 │
│   products_page | product_dialog | sales_page                  │
│   purchases_page | reports_page | invoice_detail_dialog          │
│   change_password_dialog                                        │
│   (PySide6 widgets — display + user input only)                  │
└───────────────────────┬────────────────────────────────────────┘
                         │  calls
┌───────────────────────▼────────────────────────────────────────┐
│                       LOGIC LAYER                              │
│   auth.py | logic/sales_logic.py | logic/purchase_logic.py       │
│   logic/report_logic.py                                          │
│   (validation, calculations, stock rules, voiding — no SQL, no UI) │
└───────────────────────┬────────────────────────────────────────┘
                         │  calls
┌───────────────────────▼────────────────────────────────────────┐
│                   DATA ACCESS LAYER                            │
│   auth_db.py | products_db.py | sales_db.py | purchases_db.py    │
│   (raw parameterized SQL only — no business rules, no UI)         │
└───────────────────────┬────────────────────────────────────────┘
                         │  uses
┌───────────────────────▼────────────────────────────────────────┐
│                    FOUNDATION LAYER                             │
│         database.py (connection + schema + backup)               │
│         config.py (constants)                                     │
└───────────────────────┬────────────────────────────────────────┘
                         │  reads/writes
┌───────────────────────▼────────────────────────────────────────┐
│         data/store.db (SQLite file) + data/backups/ (copies)     │
└──────────────────────────────────────────────────────────────────┘
```

This is a classic **3-tier layered architecture** (Presentation → Business Logic → Data Access), simplified for an MVP by skipping formal interfaces/DI/ORM — but the separation of concerns (and therefore the ability to test, modify, or replace any one layer independently) is fully preserved.

---

## 15. Development Roadmap (Build Order)

| # | File | Depends On | Status |
|---|---|---|---|
| 1 | `config.py` | — | ✅ Done |
| 2 | `database.py` | config.py | ✅ Done |
| 3 | `auth_db.py` | database.py | ✅ Done |
| 4 | `products_db.py` | database.py | ✅ Done |
| 5 | `sales_db.py` | database.py | Pending |
| 6 | `purchases_db.py` | database.py | ✅ Done |
| 7 | `auth.py` | auth_db.py | ✅ Done |
| 8 | `logic/sales_logic.py` | sales_db.py, products_db.py | Pending |
| 9 | `logic/purchase_logic.py` | purchases_db.py, products_db.py | ✅ Done |
| 10 | `logic/report_logic.py` | sales_db.py, purchases_db.py | Pending |
| 11 | `ui/product_dialog.py` | products_db.py | ✅ Done |
| 12 | `ui/products_page.py` | product_dialog.py, products_db.py | ✅ Done |
| 13 | `ui/sales_page.py` | sales_logic.py, products_db.py | Pending |
| 14 | `ui/purchases_page.py` | purchase_logic.py, products_db.py | ✅ Done |
| 15 | `ui/dashboard_page.py` | products_db.py, sales_db.py, purchases_db.py, report_logic.py | Pending |
| 16 | `ui/invoice_detail_dialog.py` | sales_db.py, purchases_db.py, sales_logic.py, purchase_logic.py | Pending |
| 17 | `ui/reports_page.py` | report_logic.py, invoice_detail_dialog.py | Pending |
| 18 | `ui/change_password_dialog.py` | auth.py | ✅ Done |
| 19 | `ui/main_window.py` | all `ui/*_page.py` files, change_password_dialog.py, database.py | ✅ Done |
| 20 | `ui/login_window.py` | auth.py, main_window.py | ✅ Done |
| 21 | `main.py` | database.py, auth.py, login_window.py | ✅ Done |

Build order is strictly bottom-up: foundation → data access → business logic → individual UI pages → shell window → entry point — so every file only ever depends on something that already exists by the time it's written.

---

## Final Consistency Review

A full pass was made to confirm the document is internally consistent and implementation-ready after the SKU removal, Unit removal, and Category addition:

✅ **SKU removed everywhere:** No remaining references to `sku` in schema (Section 2), screen descriptions (Sections 3.4, 3.5), business logic (Section 6), validation rules (Section 7), or file dependency notes (Section 13). Search is now name-only.
✅ **Unit removed everywhere:** No remaining references to `unit` in schema (Section 2), dialog fields (Section 3.5), or business logic (Section 6). The schema note clarifies all products are individual items; REAL quantities still support fractional amounts.
✅ **Category added consistently:** `category` column in schema (Section 2), Products page table columns (Section 3.4), Product Dialog fields (Section 3.5, with editable QComboBox UX fully specified), business logic (`get_categories()` function, Section 6), validation rules (Section 7), file dependency note for `product_dialog.py` (Section 13), and user workflow (Section 8).
✅ **`get_categories()` scoped correctly:** Listed as a `products_db.py` function, called only by `ui/product_dialog.py` — no layering violation. Categories are derived dynamically from the data; no separate table or management screen needed.
✅ **Dashboard Low Stock list updated:** Section 3.3 now shows Category in the Low Stock list columns (Name, Category, Current Stock, Reorder Level) — consistent with the Products page table layout.
✅ **Type consistency:** `stock_quantity` and `reorder_level` are both `REAL` — Low Stock comparison still compares like with like. REAL quantities still make sense without a unit label.
✅ **Roadmap status updated:** Section 15 reflects which files are already implemented (Phases 1–3 done) vs pending (Phases 4–5).
✅ **Future extensions note added:** Category management screen (rename/merge) added to Section 12 as a deferred future extension, making the deliberate "no separate category table" decision a recorded choice rather than a gap.
✅ **Profit/Unit and Stock Profit added as display-only columns:** Products table (Section 3.4) now lists Profit/Unit (Selling Price − Purchase Price) and Stock Profit (Profit/Unit × Stock Quantity) between Selling Price and Stock Quantity. Validation rules (Section 7) note both are computed in the UI, never stored. No schema change — the Products table is unchanged. `products_page.py` computes both values when populating each row.
✅ **All other previously reviewed items unchanged:** Archive flow, inactive-product consistency, Today's Profit, invoice numbering format, Confirmation Dialog Policy, wait cursor scope, error handling strategy, layering rules — all still hold as previously reviewed.

**Everything else in the previously approved blueprint (architecture, layering, transaction handling, error handling philosophy, void/audit-trail design) is unchanged and still holds.**
