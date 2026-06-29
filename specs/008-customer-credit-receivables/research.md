# Research: Customer Credit & Receivables Management

**Feature**: 008-customer-credit-receivables | **Date**: 2026-06-29

## Decision 1: Schema Migration Strategy (Adding Columns to Sales)

**Decision**: Use `ALTER TABLE Sales ADD COLUMN` for the three new columns (`customer_id`, `amount_paid`, `remaining_balance`) inside `initialize_database()` using `IF NOT EXISTS` guard via `CREATE TABLE IF NOT EXISTS` pattern already used in the project.

**Rationale**: SQLite supports `ALTER TABLE … ADD COLUMN` non-destructively. Wrapping the new DDL in an `executescript` alongside the existing table definitions (which use `CREATE TABLE IF NOT EXISTS`) means the migration runs safely on first launch after upgrade: existing rows get NULL for `customer_id` and 0 for the numeric columns (via DEFAULT). No separate migration runner is needed, consistent with the project's current approach.

**Alternatives considered**:
- Separate migration versioning table: rejected — over-engineering for a single-user desktop app with no concurrent users.
- Drop-and-recreate Sales table: rejected — destroys existing invoice history, violates Constitution principle IV.

## Decision 2: Outstanding Balance Derivation Formula

**Decision**: `outstanding_balance = SUM(s.remaining_balance FOR active Sales WHERE customer_id = X) - SUM(p.amount FOR Payments WHERE customer_id = X)`

Where `s.remaining_balance` is the balance stored at invoice-creation time (captures initial partial payment) and `p.amount` is every post-creation payment collected via the Receive Payment dialog.

**Rationale**: This satisfies FR-036 (balance derived from source records, never a stored aggregate) and FR-039 (invoice records not mutated by post-save payments). The formula is cheap to compute in SQLite with a LEFT JOIN or two subqueries. Voided invoices are excluded via `status = 'active'` filter.

**Alternatives considered**:
- Storing a live `outstanding_balance` column on Customers: rejected — would require update triggers and risk divergence from source records.
- Per-invoice payment tracking (Payments linked to sale_id): rejected per clarification Q2 — customer-level payments keep the model simpler and match the UX (one payment clears multiple invoices).

## Decision 3: FIFO Payment Attribution for Per-Invoice Display

**Decision**: When the customer detail page displays per-invoice Paid / Remaining columns, compute them by sorting the customer's active invoices by `created_at ASC` and distributing the total post-sale payments greedily (oldest invoice first) until exhausted.

**Rationale**: FIFO is the stated assumption in the spec and is standard bookkeeping practice. It is a pure read-time computation — no data is stored differently. If total post-sale payments ≥ sum of all invoice remaining balances, all invoices show "Paid".

**Alternatives considered**:
- LIFO: non-standard, confuses audit trail.
- Specific invoice linkage per payment: rejected per clarification Q2.

## Decision 4: Customer Selector Widget on Sales Page

**Decision**: Use a `QComboBox` set to editable (`setEditable(True)`) with a completer that filters from the `Customers` table as the user types. A synthetic first item "＋ Add New Customer…" triggers a minimal inline `QDialog` (name + phone fields) that inserts the record and selects it.

**Rationale**: PySide6's `QCompleter` with a `QStringListModel` provides real-time filtering without a custom widget. The `+ Add New` pattern is established in the existing product combo. Keeps the invoice flow uninterrupted.

**Alternatives considered**:
- Separate customer management prerequisite: rejected per clarification Q3 (Option A).
- Popup `QListWidget` search: more complex, not needed at the scale of 1,000 customers.

## Decision 5: Dashboard KPI Card Interactivity

**Decision**: Make the "Outstanding Receivables" KPI card clickable by wrapping it in a `QFrame` with `mousePressEvent` override (same pattern used for `navigate_to_product` signal in the existing `DashboardPage`). Clicking emits a signal that opens a `QDialog` listing customers with balance > 0. Clicking a customer row in that dialog emits a signal that switches the main window to the Customers page and highlights that customer.

**Rationale**: Consistent with existing navigation pattern (`navigate_to_product` Signal). No new navigation mechanism needed.

**Alternatives considered**:
- Making the card a `QPushButton`: changes visual style; existing cards are `QFrame`.
- Separate window for the receivables list: violates UI consistency (dialogs used for contextual detail, not navigation).

## Decision 6: New Files vs. Expanding Existing Files

**Decision**:
- `customers_db.py` — new file (Customers table queries)
- `payments_db.py` — new file (Payments table queries)
- `logic/customers_logic.py` — new file (customer validation, balance derivation, payment validation)
- Modify `sales_db.py`, `sales_logic.py`, `database.py`, `main_window.py`, `sales_page.py`, `dashboard_page.py`, `reports_page.py` in place

**Rationale**: Per-table `*_db.py` files is the established pattern. Customers and Payments are separate entities with distinct query sets. Expanding existing files where the feature is an extension (Sales, Dashboard, Reports) avoids fragmentation.
