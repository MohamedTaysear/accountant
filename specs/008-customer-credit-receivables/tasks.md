# Tasks: Customer Credit & Receivables Management

**Input**: Design documents from `specs/008-customer-credit-receivables/`

**Stack**: Python, PySide6, SQLite — no ORM, no new dependencies

**Key references** (read before implementing):
- `specs/008-customer-credit-receivables/data-model.md` — table schemas and derivation formulas
- `specs/008-customer-credit-receivables/contracts/customers_db.md` — DB-layer function signatures
- `specs/008-customer-credit-receivables/contracts/customers_logic.md` — logic-layer function signatures
- `specs/008-customer-credit-receivables/contracts/customers_page.md` — UI contracts and layouts
- `specs/008-customer-credit-receivables/contracts/dashboard_update.md` — nav order and dashboard changes
- `specs/008-customer-credit-receivables/quickstart.md` — manual test scenarios

**Architectural decisions in effect**:
- Payments link to both `customer_id` AND `sale_id` (not customer-only)
- `remaining_balance` is NEVER stored on Sales — always derived
- Payment status uses four explicit states: Paid / Partially Paid / Unpaid / Voided
- Sales page uses a payment-status QComboBox (not a checkbox)
- Receive Payment dialog shows outstanding invoices for the customer; user selects which to pay

**Format**: `- [x] [TaskID] [P?] [Story?] Description — file path`
- **[P]**: task operates on a different file from its siblings and can be done simultaneously
- **[USn]**: which user story this task belongs to

---

## Phase 1: Foundational — Database Schema

**Purpose**: Extend SQLite schema. MUST be complete before any other phase. App must still launch normally after every task.

- [x] T001 Add `Customers` table to `initialize_database()` in `accounting_system/database.py`.
  Inside the existing `executescript` string, after the `Expenses` table block, add:
  ```sql
  CREATE TABLE IF NOT EXISTS Customers (
      id         INTEGER PRIMARY KEY AUTOINCREMENT,
      name       TEXT    NOT NULL,
      phone      TEXT    NOT NULL DEFAULT '',
      created_at TEXT    NOT NULL
  );
  ```

- [x] T002 Add `Payments` table to `initialize_database()` in `accounting_system/database.py`.
  Inside the same `executescript` string (alongside the Customers table added in T001), add:
  ```sql
  CREATE TABLE IF NOT EXISTS Payments (
      id              INTEGER PRIMARY KEY AUTOINCREMENT,
      customer_id     INTEGER NOT NULL,
      sale_id         INTEGER NOT NULL,
      amount          REAL    NOT NULL,
      notes           TEXT    NOT NULL DEFAULT '',
      remaining_after REAL    NOT NULL DEFAULT 0,
      payment_date    TEXT    NOT NULL,
      created_at      TEXT    NOT NULL,
      FOREIGN KEY (customer_id) REFERENCES Customers(id),
      FOREIGN KEY (sale_id)     REFERENCES Sales(id)
  );
  ```

- [x] T003 Add two `ALTER TABLE` statements for the `Sales` table in `accounting_system/database.py`.
  Place them **after** the `executescript` call (after `conn.commit()`), each in a `try/except` that silently ignores errors (SQLite raises `OperationalError` when a column already exists):
  ```python
  for ddl in [
      "ALTER TABLE Sales ADD COLUMN customer_id INTEGER REFERENCES Customers(id)",
      "ALTER TABLE Sales ADD COLUMN amount_paid REAL NOT NULL DEFAULT 0",
  ]:
      try:
          conn.execute(ddl)
      except Exception:
          pass
  conn.commit()
  ```
  **Important**: Do NOT add a `remaining_balance` column — it is always derived, never stored.

- [x] T004 Verify the app launches cleanly after T001–T003. Confirm `initialize_database()` succeeds without errors and the three SQL objects (`Customers` table, `Payments` table, `Sales.customer_id`, `Sales.amount_paid`) exist.

**Checkpoint**: Schema extended. App still runs. Three new DB objects present.

---

## Phase 2: Data-Access Layer — New Modules

**Purpose**: Create `customers_db.py` and `payments_db.py`. No business rules. All SQL parameterized.

- [x] T005 [P] Create `accounting_system/customers_db.py` with the following complete implementation:

  ```python
  import database

  def create_customer(name: str, phone: str) -> int:
      conn = database.get_connection()
      try:
          conn.execute(
              "INSERT INTO Customers (name, phone, created_at) VALUES (?, ?, ?)",
              (name, phone, database.now_cairo())
          )
          row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
          conn.commit()
          return row_id
      except Exception:
          conn.rollback()
          raise
      finally:
          conn.close()

  def get_all_customers() -> list:
      conn = database.get_connection()
      try:
          return conn.execute(
              "SELECT id, name, phone FROM Customers ORDER BY name COLLATE NOCASE ASC"
          ).fetchall()
      finally:
          conn.close()

  def get_customer_by_id(customer_id: int):
      conn = database.get_connection()
      try:
          return conn.execute(
              "SELECT id, name, phone FROM Customers WHERE id = ?", (customer_id,)
          ).fetchone()
      finally:
          conn.close()

  def get_customers_with_balance_summary() -> list:
      conn = database.get_connection()
      try:
          return conn.execute("""
              SELECT
                  c.id,
                  c.name,
                  c.phone,
                  COUNT(s.id)                                       AS invoice_count,
                  COALESCE(SUM(s.total_amount), 0)                  AS total_purchases,
                  COALESCE(SUM(s.amount_paid), 0)                   AS total_paid_at_invoice,
                  COALESCE((
                      SELECT SUM(p.amount)
                      FROM Payments p
                      WHERE p.customer_id = c.id
                  ), 0)                                             AS total_post_payments,
                  COALESCE(SUM(s.total_amount - s.amount_paid), 0) -
                  COALESCE((
                      SELECT SUM(p.amount)
                      FROM Payments p
                      WHERE p.customer_id = c.id
                  ), 0)                                             AS outstanding_balance
              FROM Customers c
              LEFT JOIN Sales s ON s.customer_id = c.id AND s.status = 'active'
              GROUP BY c.id
              ORDER BY c.name COLLATE NOCASE ASC
          """).fetchall()
      finally:
          conn.close()

  def get_customer_invoices(customer_id: int) -> list:
      conn = database.get_connection()
      try:
          return conn.execute(
              """SELECT id, invoice_number, created_at, total_amount, amount_paid, status
                 FROM Sales
                 WHERE customer_id = ?
                 ORDER BY created_at ASC""",
              (customer_id,)
          ).fetchall()
      finally:
          conn.close()

  def get_invoice_outstanding(sale_id: int) -> float:
      conn = database.get_connection()
      try:
          inv = conn.execute(
              "SELECT total_amount, amount_paid, status FROM Sales WHERE id = ?", (sale_id,)
          ).fetchone()
          if not inv or inv["status"] == "voided":
              return 0.0
          paid = conn.execute(
              "SELECT COALESCE(SUM(amount), 0) FROM Payments WHERE sale_id = ?", (sale_id,)
          ).fetchone()[0]
          return max(0.0, round(float(inv["total_amount"]) - float(inv["amount_paid"]) - float(paid), 2))
      finally:
          conn.close()

  def get_outstanding_receivables_total() -> float:
      conn = database.get_connection()
      try:
          inv_remaining = conn.execute(
              "SELECT COALESCE(SUM(total_amount - amount_paid), 0) FROM Sales WHERE status = 'active' AND customer_id IS NOT NULL"
          ).fetchone()[0]
          pay_total = conn.execute(
              "SELECT COALESCE(SUM(p.amount), 0) FROM Payments p JOIN Sales s ON p.sale_id = s.id WHERE s.status = 'active'"
          ).fetchone()[0]
          return max(0.0, round(float(inv_remaining) - float(pay_total), 2))
      finally:
          conn.close()

  def get_customers_with_outstanding_balance() -> list:
      rows = get_customers_with_balance_summary()
      return [r for r in rows if float(r["outstanding_balance"]) > 0]
  ```

- [x] T006 [P] Create `accounting_system/payments_db.py` with the following complete implementation:

  ```python
  import database

  def insert_payment(customer_id: int, sale_id: int, amount: float,
                     remaining_after: float, notes: str, conn) -> int:
      """Insert a payment using the provided connection (caller manages transaction)."""
      conn.execute(
          """INSERT INTO Payments
             (customer_id, sale_id, amount, remaining_after, notes, payment_date, created_at)
             VALUES (?, ?, ?, ?, ?, ?, ?)""",
          (customer_id, sale_id, amount, remaining_after, notes,
           database.now_cairo(), database.now_cairo())
      )
      return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

  def get_payments_for_customer(customer_id: int) -> list:
      conn = database.get_connection()
      try:
          return conn.execute(
              """SELECT p.id, p.customer_id, p.sale_id, p.amount, p.notes,
                        p.remaining_after, p.payment_date, p.created_at,
                        s.invoice_number
                 FROM Payments p
                 JOIN Sales s ON p.sale_id = s.id
                 WHERE p.customer_id = ?
                 ORDER BY p.payment_date ASC""",
              (customer_id,)
          ).fetchall()
      finally:
          conn.close()

  def get_payments_for_invoice(sale_id: int) -> list:
      conn = database.get_connection()
      try:
          return conn.execute(
              """SELECT id, customer_id, sale_id, amount, notes, remaining_after,
                        payment_date, created_at
                 FROM Payments WHERE sale_id = ? ORDER BY payment_date ASC""",
              (sale_id,)
          ).fetchall()
      finally:
          conn.close()

  def get_total_payments_for_invoice(sale_id: int) -> float:
      conn = database.get_connection()
      try:
          row = conn.execute(
              "SELECT COALESCE(SUM(amount), 0) FROM Payments WHERE sale_id = ?", (sale_id,)
          ).fetchone()
          return float(row[0])
      finally:
          conn.close()

  def get_total_payments_for_customer(customer_id: int) -> float:
      conn = database.get_connection()
      try:
          row = conn.execute(
              "SELECT COALESCE(SUM(amount), 0) FROM Payments WHERE customer_id = ?", (customer_id,)
          ).fetchone()
          return float(row[0])
      finally:
          conn.close()
  ```

**Checkpoint**: `import customers_db` and `import payments_db` succeed without error.

---

## Phase 3: Business-Logic Layer

**Purpose**: Create `logic/customers_logic.py`. No SQL. No PySide6.

- [x] T007 Create `accounting_system/logic/customers_logic.py` with the following complete implementation:

  ```python
  import database
  import customers_db
  import payments_db


  # ── Customer management ────────────────────────────────────────────────────

  def validate_customer_name(name: str) -> str:
      name = name.strip()
      if not name:
          raise ValueError("Customer name cannot be empty.")
      return name

  def create_customer(name: str, phone: str) -> int:
      name = validate_customer_name(name)
      return customers_db.create_customer(name, (phone or "").strip())

  def get_all_customers_for_selector() -> list:
      rows = customers_db.get_all_customers()
      return [{"id": r["id"], "name": r["name"], "phone": r["phone"]} for r in rows]

  def get_customers_list() -> list:
      return [dict(r) for r in customers_db.get_customers_with_balance_summary()]


  # ── Partial-payment validation ────────────────────────────────────────────

  def validate_partial_payment(invoice_total: float, amount_paid: float) -> None:
      if amount_paid < 0:
          raise ValueError("Amount paid cannot be negative.")
      if amount_paid > invoice_total + 0.001:
          raise ValueError("Amount paid cannot exceed the invoice total.")

  def compute_invoice_outstanding(sale_id: int) -> float:
      return customers_db.get_invoice_outstanding(sale_id)


  # ── Payment collection ────────────────────────────────────────────────────

  def validate_payment_amount(amount: float, invoice_outstanding: float) -> None:
      if amount <= 0:
          raise ValueError("Payment amount must be greater than zero.")
      if amount > invoice_outstanding + 0.001:
          raise ValueError("Payment cannot exceed the invoice outstanding balance.")

  def record_payment(customer_id: int, sale_id: int, amount: float, notes: str = "") -> int:
      invoice_outstanding = compute_invoice_outstanding(sale_id)
      validate_payment_amount(amount, invoice_outstanding)
      remaining_after = round(invoice_outstanding - amount, 2)
      conn = database.get_connection()
      try:
          payment_id = payments_db.insert_payment(
              customer_id, sale_id, amount, remaining_after, notes, conn
          )
          conn.commit()
          return payment_id
      except Exception:
          conn.rollback()
          raise
      finally:
          conn.close()


  # ── Customer profile ──────────────────────────────────────────────────────

  def _derive_payment_status(total_amount: float, total_paid: float, inv_status: str) -> str:
      if inv_status == "voided":
          return "Voided"
      remaining = round(total_amount - total_paid, 2)
      if remaining <= 0:
          return "Paid"
      if total_paid <= 0:
          return "Unpaid"
      return "Partially Paid"

  def get_customer_profile(customer_id: int) -> dict:
      customer = customers_db.get_customer_by_id(customer_id)
      if not customer:
          raise ValueError(f"Customer {customer_id} not found.")

      invoices_raw = customers_db.get_customer_invoices(customer_id)
      all_payments = payments_db.get_payments_for_customer(customer_id)

      total_purchases = 0.0
      total_paid_sum  = 0.0
      outstanding_sum = 0.0
      invoices = []

      for inv in invoices_raw:
          inv_total      = float(inv["total_amount"])
          paid_at_create = float(inv["amount_paid"])
          post_payments  = payments_db.get_total_payments_for_invoice(inv["id"])
          total_paid_inv = round(paid_at_create + post_payments, 2)
          remaining      = max(0.0, round(inv_total - total_paid_inv, 2))
          status         = _derive_payment_status(inv_total, total_paid_inv, inv["status"])

          total_purchases += inv_total
          total_paid_sum  += total_paid_inv
          if inv["status"] == "active":
              outstanding_sum += remaining

          invoices.append({
              "id": inv["id"],
              "invoice_number": inv["invoice_number"],
              "created_at": inv["created_at"],
              "total_amount": inv_total,
              "amount_paid_at_creation": paid_at_create,
              "post_sale_payments": post_payments,
              "total_paid": total_paid_inv,
              "remaining": remaining,
              "payment_status": status,
          })

      return {
          "customer": dict(customer),
          "outstanding_balance": round(outstanding_sum, 2),
          "total_purchases": round(total_purchases, 2),
          "total_paid": round(total_paid_sum, 2),
          "invoice_count": len(invoices_raw),
          "invoices": invoices,
          "payments": [dict(p) for p in all_payments],
      }

  def get_outstanding_invoices_for_customer(customer_id: int) -> list:
      """Returns only invoices with remaining > 0, for the Receive Payment dialog."""
      invoices_raw = customers_db.get_customer_invoices(customer_id)
      result = []
      for inv in invoices_raw:
          if inv["status"] != "active":
              continue
          outstanding = customers_db.get_invoice_outstanding(inv["id"])
          if outstanding > 0:
              result.append({
                  "id": inv["id"],
                  "invoice_number": inv["invoice_number"],
                  "created_at": inv["created_at"],
                  "total_amount": float(inv["total_amount"]),
                  "remaining": outstanding,
              })
      return result


  # ── Dashboard / report aggregates ────────────────────────────────────────

  def get_outstanding_receivables_total() -> float:
      return customers_db.get_outstanding_receivables_total()

  def get_customers_with_outstanding_count() -> int:
      return len(customers_db.get_customers_with_outstanding_balance())

  def get_customers_with_outstanding_list() -> list:
      rows = customers_db.get_customers_with_outstanding_balance()
      return [{"id": r["id"], "name": r["name"],
               "outstanding_balance": float(r["outstanding_balance"])} for r in rows]

  def get_receivables_report(start_date=None, end_date=None, search=None) -> list:
      conn = database.get_connection()
      try:
          conditions = ["s.status = 'active'"]
          params = []
          if start_date and end_date:
              conditions.append("DATE(s.created_at) BETWEEN ? AND ?")
              params.extend([start_date, end_date])
          where = " AND ".join(conditions)
          rows = conn.execute(f"""
              SELECT
                  c.id,
                  c.name,
                  COALESCE(SUM(s.total_amount), 0)             AS total_sales,
                  COALESCE(SUM(s.amount_paid), 0)              AS paid_at_invoice,
                  COALESCE(SUM(s.total_amount - s.amount_paid), 0) AS inv_remaining
              FROM Customers c
              LEFT JOIN Sales s ON s.customer_id = c.id AND {where}
              GROUP BY c.id
              ORDER BY c.name COLLATE NOCASE ASC
          """, params).fetchall()
      finally:
          conn.close()

      results = []
      for r in rows:
          if search and search.lower() not in r["name"].lower():
              continue
          post = payments_db.get_total_payments_for_customer(r["id"])
          outstanding = max(0.0, round(float(r["inv_remaining"]) - post, 2))
          total_paid  = round(float(r["paid_at_invoice"]) + post, 2)
          results.append({
              "name": r["name"],
              "total_sales": round(float(r["total_sales"]), 2),
              "total_paid": total_paid,
              "outstanding_balance": outstanding,
          })
      return results
  ```

**Checkpoint**: `from logic import customers_logic` succeeds. All functions callable without error.

---

## Phase 4: Sales Integration — Payment Status Selector + Customer Selector

**Goal (US1)**: Accountant can record Paid in Full / Partial Payment / Unpaid on a new invoice and link it to a customer.

**Independent Test**: Quickstart Scenario 1 (full payment) and Scenario 2 (partial payment). Invoice saves with correct `amount_paid` in DB.

- [x] T008 [US1] Update `insert_sale_with_items` in `accounting_system/sales_db.py` to accept `customer_id` and `amount_paid`.

  Change the function signature from:
  ```python
  def insert_sale_with_items(customer_name, discount_amount: float, items: list) -> str:
  ```
  to:
  ```python
  def insert_sale_with_items(customer_name, discount_amount: float, items: list,
                             customer_id=None, amount_paid=None) -> str:
  ```

  Inside the function, update the `INSERT INTO Sales` statement:
  ```python
  # Before the INSERT, compute amount_paid default:
  ap = amount_paid if amount_paid is not None else total_amount

  conn.execute(
      "INSERT INTO Sales (invoice_number, customer_name, discount_amount, total_amount,"
      " status, created_at, customer_id, amount_paid)"
      " VALUES (?, ?, ?, ?, 'active', ?, ?, ?)",
      ("PENDING", customer_name, discount_amount, total_amount,
       database.now_cairo(), customer_id, ap)
  )
  ```
  Note: **no** `remaining_balance` column is inserted — it does not exist in the schema.

- [x] T009 [US1] Update `accounting_system/logic/sales_logic.py` to add payment validation helpers.
  Add import at the top:
  ```python
  from logic.customers_logic import validate_partial_payment
  ```
  Add new function:
  ```python
  def compute_amount_paid(invoice_total: float, payment_status: str, partial_amount: float) -> float:
      """Returns amount_paid based on the payment status selection.
      payment_status is one of: 'paid_in_full', 'partial', 'unpaid'
      Raises ValueError for invalid partial amounts.
      """
      if payment_status == "paid_in_full":
          return invoice_total
      elif payment_status == "unpaid":
          return 0.0
      else:  # partial
          validate_partial_payment(invoice_total, partial_amount)
          return round(partial_amount, 2)
  ```

- [x] T010 [US1] Update `accounting_system/ui/sales_page.py` — add customer selector and payment status selector.

  **Step 1** — Add imports at the top of the file (after existing imports):
  ```python
  from logic.customers_logic import get_all_customers_for_selector, create_customer
  from logic.sales_logic import compute_amount_paid
  ```

  **Step 2** — In `_build_ui`, replace the `customer_input` QLineEdit block:
  ```python
  self.customer_input = QLineEdit()
  self.customer_input.setPlaceholderText("Optional customer name")
  self.customer_input.setMaximumWidth(280)
  header_form.addRow("Customer:", self.customer_input)
  ```
  With:
  ```python
  from PySide6.QtWidgets import QCheckBox  # already imported if needed
  self.customer_combo = QComboBox()
  self.customer_combo.setEditable(True)
  self.customer_combo.setMaximumWidth(320)
  self.customer_combo.setInsertPolicy(QComboBox.NoInsert)
  self._selected_customer_id = None
  self._customer_data = []
  self._refresh_customer_combo()
  self.customer_combo.currentIndexChanged.connect(self._on_customer_selected)
  header_form.addRow("Customer:", self.customer_combo)

  # Payment status selector
  self.payment_status_combo = QComboBox()
  self.payment_status_combo.addItem("Paid in Full",     "paid_in_full")
  self.payment_status_combo.addItem("Partial Payment",  "partial")
  self.payment_status_combo.addItem("Unpaid",           "unpaid")
  self.payment_status_combo.currentIndexChanged.connect(self._on_payment_status_changed)
  header_form.addRow("Payment:", self.payment_status_combo)

  # Partial payment fields (shown only for "Partial Payment")
  self._partial_widget = QWidget()
  pp_form = QFormLayout(self._partial_widget)
  pp_form.setContentsMargins(0, 0, 0, 0)

  self.invoice_total_lbl = QLabel("0.00")
  self.invoice_total_lbl.setStyleSheet("background: transparent;")
  pp_form.addRow("Invoice Total:", self.invoice_total_lbl)

  self.amount_paid_spin = QDoubleSpinBox()
  self.amount_paid_spin.setDecimals(2)
  self.amount_paid_spin.setRange(0, 0)
  self.amount_paid_spin.setFixedWidth(140)
  self.amount_paid_spin.valueChanged.connect(self._on_amount_paid_changed)
  pp_form.addRow("Amount Paid:", self.amount_paid_spin)

  self.remaining_lbl = QLabel("0.00")
  self.remaining_lbl.setStyleSheet("background: transparent;")
  pp_form.addRow("Remaining Balance:", self.remaining_lbl)

  header_form.addRow("", self._partial_widget)
  self._partial_widget.hide()
  ```

  **Step 3** — Add these helper methods to `SalesPage`:
  ```python
  def _refresh_customer_combo(self):
      self.customer_combo.blockSignals(True)
      self.customer_combo.clear()
      self._customer_data = get_all_customers_for_selector()
      self.customer_combo.addItem("(Select or add customer)", userData=None)
      for c in self._customer_data:
          label = c["name"] + (f"  [{c['phone']}]" if c["phone"] else "")
          self.customer_combo.addItem(label, userData=c["id"])
      self.customer_combo.addItem("＋ Add New Customer…", userData="ADD_NEW")
      self.customer_combo.blockSignals(False)
      self._selected_customer_id = None

  def _on_customer_selected(self, index):
      data = self.customer_combo.itemData(index)
      if data == "ADD_NEW":
          self._add_new_customer()
      else:
          self._selected_customer_id = data

  def _add_new_customer(self):
      from PySide6.QtWidgets import QDialog, QDialogButtonBox
      dlg = QDialog(self)
      dlg.setWindowTitle("Add New Customer")
      lay = QFormLayout(dlg)
      name_edit  = QLineEdit()
      phone_edit = QLineEdit()
      phone_edit.setPlaceholderText("Optional")
      lay.addRow("Name:", name_edit)
      lay.addRow("Phone:", phone_edit)
      btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
      btns.accepted.connect(dlg.accept)
      btns.rejected.connect(dlg.reject)
      lay.addRow(btns)
      if dlg.exec() != QDialog.Accepted:
          self.customer_combo.setCurrentIndex(0)
          self._selected_customer_id = None
          return
      try:
          new_id = create_customer(name_edit.text(), phone_edit.text())
          self._refresh_customer_combo()
          for i in range(self.customer_combo.count()):
              if self.customer_combo.itemData(i) == new_id:
                  self.customer_combo.setCurrentIndex(i)
                  break
      except ValueError as e:
          QMessageBox.warning(self, "Validation Error", str(e))
          self.customer_combo.setCurrentIndex(0)
          self._selected_customer_id = None

  def _on_payment_status_changed(self, _index):
      status = self.payment_status_combo.currentData()
      if status == "partial":
          self._partial_widget.show()
          self._sync_partial_total()
      else:
          self._partial_widget.hide()

  def _sync_partial_total(self):
      total = self._compute_invoice_total()
      self.invoice_total_lbl.setText(f"{total:,.2f}")
      self.amount_paid_spin.setRange(0, total)
      self._on_amount_paid_changed(self.amount_paid_spin.value())

  def _on_amount_paid_changed(self, value):
      total     = self._compute_invoice_total()
      remaining = max(0.0, round(total - value, 2))
      self.remaining_lbl.setText(f"{remaining:,.2f}")

  def _compute_invoice_total(self) -> float:
      subtotal  = sum(item["subtotal"] for item in self._items)
      disc_type = self.discount_type_combo.currentText()
      disc_val  = self.discount_spin.value()
      discount  = round(subtotal * disc_val / 100, 2) if disc_type == "%" else disc_val
      return max(0.0, round(subtotal - discount, 2))
  ```

  **Step 4** — In `_update_totals` (or wherever the footer total is recalculated after items change), add a call to `self._sync_partial_total()` if partial payment is selected:
  ```python
  # at the end of _update_totals:
  if self.payment_status_combo.currentData() == "partial":
      self._sync_partial_total()
  ```

  **Step 5** — In the existing save method (wherever `insert_sale_with_items` is called), replace the call with:
  ```python
  # 1. Validate customer
  if self._selected_customer_id is None:
      QMessageBox.warning(self, "Missing Customer", "Please select or add a customer before saving.")
      return

  # 2. Compute amount_paid
  invoice_total  = self._compute_invoice_total()
  payment_status = self.payment_status_combo.currentData()
  partial_amount = self.amount_paid_spin.value() if payment_status == "partial" else 0.0
  try:
      amount_paid = compute_amount_paid(invoice_total, payment_status, partial_amount)
  except ValueError as e:
      QMessageBox.warning(self, "Validation Error", str(e))
      return

  # 3. Get customer name
  customer_name = ""
  for c in self._customer_data:
      if c["id"] == self._selected_customer_id:
          customer_name = c["name"]
          break

  # 4. Call insert (pass customer_id and amount_paid; no remaining_balance arg)
  invoice_number = sales_db.insert_sale_with_items(
      customer_name, discount_amount, items,
      customer_id=self._selected_customer_id,
      amount_paid=amount_paid
  )
  ```

  **Step 6** — After a successful save, reset the form:
  ```python
  self._refresh_customer_combo()
  self.payment_status_combo.setCurrentIndex(0)  # reset to "Paid in Full"
  ```

  **Step 7** — Add `showEvent` to refresh customer combo when page is shown:
  ```python
  def showEvent(self, event):
      super().showEvent(event)
      self._refresh_customer_combo()
  ```

**Checkpoint (US1)**: Create invoice with "Partial Payment", 400 paid on a 1000 invoice. Confirm `SELECT amount_paid, customer_id FROM Sales ORDER BY id DESC LIMIT 1` shows `400` and a valid customer_id. No `remaining_balance` column exists.

---

## Phase 5: Customers Page

**Goal (US2)**: New "Customers" navigation page listing all customers.

**Independent Test**: Navigate to Customers. See list with outstanding balance. Search and filter work. Double-click opens detail. Quickstart Scenario 1 & 2 prerequisites.

- [x] T011 [US2] Update `accounting_system/ui/main_window.py` — insert Customers at nav index 5, shift Reports to index 6.

  Change `nav_buttons`:
  ```python
  nav_buttons = [
      ("Dashboard",  0, "dashboard.svg"),
      ("Products",   1, "products.svg"),
      ("Sales",      2, "sales.svg"),
      ("Purchases",  3, "purchases.svg"),
      ("Expenses",   4, "expenses.svg"),
      ("Customers",  5, "customers.svg"),   # NEW
      ("Reports",    6, "reports.svg"),     # was 5
  ]
  ```

  Add import:
  ```python
  from ui.customers_page import CustomersPage
  ```

  In `_build_ui`, update the stack:
  ```python
  self.customers_page = CustomersPage()
  self.stack.addWidget(self.dashboard_page)   # 0
  self.stack.addWidget(self.products_page)    # 1
  self.stack.addWidget(SalesPage())           # 2
  self.stack.addWidget(PurchasesPage())       # 3
  self.stack.addWidget(ExpensesPage())        # 4
  self.stack.addWidget(self.customers_page)   # 5 NEW
  self.stack.addWidget(ReportsPage())         # 6
  ```

  Connect signal:
  ```python
  self.customers_page.open_customer_detail.connect(self._on_open_customer_detail)
  ```

  Add handler method:
  ```python
  def _on_open_customer_detail(self, customer_id: int):
      if not hasattr(self, '_customer_detail_page'):
          from ui.customer_detail_page import CustomerDetailPage
          self._customer_detail_page = CustomerDetailPage()
          self.stack.addWidget(self._customer_detail_page)   # index 7
          self._customer_detail_page.back_requested.connect(
              lambda: self._switch_page(5)
          )
      self._customer_detail_page.load_customer(customer_id)
      self._switch_page(self.stack.indexOf(self._customer_detail_page))
  ```

  In `_refresh_all_pages`, add:
  ```python
  if hasattr(self, 'customers_page'):
      self.customers_page._refresh()
  ```

- [x] T012 [US2] Create `accounting_system/ui/customers_page.py` — complete implementation:

  ```python
  import traceback
  from PySide6.QtWidgets import (
      QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
      QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
      QMessageBox,
  )
  from PySide6.QtCore import Qt, Signal
  from PySide6.QtGui import QFont, QColor

  from logic import customers_logic
  from ui import theme


  class CustomersPage(QWidget):
      open_customer_detail = Signal(int)

      def __init__(self, parent=None):
          super().__init__(parent)
          self._all_data = []
          self._show_balance_only = False
          self._build_ui()
          self._refresh()

      def _build_ui(self):
          layout = QVBoxLayout(self)
          layout.setContentsMargins(
              theme._active.spacing_xl, theme._active.spacing_xl,
              theme._active.spacing_xl, theme._active.spacing_xl)
          layout.setSpacing(theme._active.spacing_lg)

          title = QLabel("Customers")
          font = QFont(theme._active.font_family, theme._active.size_page_title)
          font.setBold(True)
          title.setFont(font)
          title.setStyleSheet(f"color: {theme._active.text_primary}; background: transparent;")
          layout.addWidget(title)

          controls = QHBoxLayout()
          self.search_input = QLineEdit()
          self.search_input.setPlaceholderText("Search by customer name…")
          self.search_input.textChanged.connect(self._apply_filter)
          controls.addWidget(self.search_input, 1)
          self.balance_btn = QPushButton("Show With Balance Only")
          self.balance_btn.setCheckable(True)
          self.balance_btn.toggled.connect(self._on_balance_toggled)
          controls.addWidget(self.balance_btn)
          layout.addLayout(controls)

          self.table = QTableWidget()
          self.table.setColumnCount(5)
          self.table.setHorizontalHeaderLabels(
              ["Customer Name", "Phone", "Invoices", "Total Purchases", "Outstanding Balance"])
          self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
          for col in [1, 2]:
              self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
          for col in [3, 4]:
              self.table.setColumnWidth(col, 150)
          self.table.setEditTriggers(QTableWidget.NoEditTriggers)
          self.table.setSelectionBehavior(QTableWidget.SelectRows)
          self.table.setSortingEnabled(True)
          self.table.setStyleSheet(
              f"QTableWidget {{ border-radius: {theme._active.card_border_radius}px;"
              f" border: 1px solid {theme._active.border}; }}")
          theme.apply_table_style(self.table)
          self.table.doubleClicked.connect(self._on_row_double_clicked)
          layout.addWidget(self.table)

      def _refresh(self):
          try:
              self._all_data = customers_logic.get_customers_list()
              self._apply_filter()
          except Exception:
              traceback.print_exc()
              QMessageBox.critical(self, "Error", "Failed to load customers.")

      def _on_balance_toggled(self, checked):
          self._show_balance_only = checked
          self._apply_filter()

      def _apply_filter(self):
          query = self.search_input.text().lower().strip()
          data  = self._all_data
          if query:
              data = [r for r in data if query in r["name"].lower()]
          if self._show_balance_only:
              data = [r for r in data if float(r["outstanding_balance"]) > 0]

          highlight = QColor("#e67e22")
          self.table.setSortingEnabled(False)
          self.table.setRowCount(len(data))
          for row, r in enumerate(data):
              has_bal = float(r["outstanding_balance"]) > 0
              values  = [
                  r["name"],
                  r["phone"] or "",
                  str(r["invoice_count"]),
                  f"{float(r['total_purchases']):,.2f}",
                  f"{float(r['outstanding_balance']):,.2f}",
              ]
              for col, text in enumerate(values):
                  item = QTableWidgetItem(text)
                  item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                  if has_bal:
                      item.setForeground(highlight)
                  self.table.setItem(row, col, item)
              self.table.item(row, 0).setData(Qt.UserRole, r["id"])
          self.table.setSortingEnabled(True)

      def _on_row_double_clicked(self, index):
          customer_id = self.table.item(index.row(), 0).data(Qt.UserRole)
          if customer_id is not None:
              self.open_customer_detail.emit(customer_id)
  ```

**Checkpoint (US2)**: Launch app, click Customers. List loads. Search and filter work. Double-click row does not crash.

---

## Phase 6: Customer Detail Page

**Goal (US3)**: Customer profile with summary cards, invoice table (derived status), and payment history tab.

**Independent Test**: Quickstart Scenario 3. Open a customer with a partial-payment invoice. Verify summary cards and invoice status are correct. Payment history tab shows post-sale payments with invoice number.

- [x] T013 [US3] Create `accounting_system/ui/customer_detail_page.py` — complete implementation:

  ```python
  import traceback
  from PySide6.QtWidgets import (
      QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
      QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
      QTabWidget, QMessageBox, QApplication, QSizePolicy,
  )
  from PySide6.QtCore import Qt, Signal
  from PySide6.QtGui import QFont, QColor

  from logic import customers_logic
  from ui import theme


  def _make_card(title: str, value_lbl: QLabel) -> QFrame:
      frame = QFrame()
      frame.setStyleSheet(
          f"QFrame {{ background-color: {theme._active.surface};"
          f" border: 1px solid {theme._active.border};"
          f" border-radius: {theme._active.card_border_radius}px; }}")
      frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
      lay = QVBoxLayout(frame)
      lay.setContentsMargins(
          theme._active.spacing_lg, theme._active.spacing_md,
          theme._active.spacing_lg, theme._active.spacing_md)
      lay.setSpacing(4)
      t = QLabel(title)
      t.setAlignment(Qt.AlignCenter)
      t.setStyleSheet(
          f"background: transparent; border: none;"
          f" font-size: {theme._active.size_kpi_label}pt;"
          f" color: {theme._active.text_secondary}; font-weight: bold;")
      value_lbl.setAlignment(Qt.AlignCenter)
      value_lbl.setStyleSheet(
          f"background: transparent; border: none;"
          f" font-size: {theme._active.size_kpi_value}pt;"
          f" font-weight: bold; color: {theme._active.text_primary};")
      lay.addWidget(t)
      lay.addWidget(value_lbl)
      return frame


  STATUS_COLORS = {
      "Paid":           "#27ae60",
      "Partially Paid": "#e67e22",
      "Unpaid":         "#e74c3c",
      "Voided":         "#95a5a6",
  }


  class CustomerDetailPage(QWidget):
      back_requested = Signal()

      def __init__(self, parent=None):
          super().__init__(parent)
          self._customer_id = None
          self._build_ui()

      def _build_ui(self):
          layout = QVBoxLayout(self)
          layout.setContentsMargins(
              theme._active.spacing_xl, theme._active.spacing_xl,
              theme._active.spacing_xl, theme._active.spacing_xl)
          layout.setSpacing(theme._active.spacing_lg)

          top = QHBoxLayout()
          back_btn = QPushButton("← Back to Customers")
          back_btn.setStyleSheet(
              f"QPushButton {{ background: transparent; border: none;"
              f" color: {theme._active.primary}; font-size: {theme._active.size_normal}pt; }}"
              f"QPushButton:hover {{ text-decoration: underline; }}")
          back_btn.clicked.connect(self.back_requested.emit)
          top.addWidget(back_btn)
          top.addStretch()
          self.receive_btn = QPushButton("Receive Payment")
          self.receive_btn.setProperty("class", "primary")
          self.receive_btn.clicked.connect(self._on_receive_payment)
          self.receive_btn.hide()
          top.addWidget(self.receive_btn)
          layout.addLayout(top)

          self.name_lbl = QLabel("")
          fn = QFont(theme._active.font_family, theme._active.size_page_title)
          fn.setBold(True)
          self.name_lbl.setFont(fn)
          self.name_lbl.setStyleSheet(f"color: {theme._active.text_primary}; background: transparent;")
          layout.addWidget(self.name_lbl)

          self.phone_lbl = QLabel("")
          self.phone_lbl.setStyleSheet(f"color: {theme._active.text_secondary}; background: transparent;")
          layout.addWidget(self.phone_lbl)

          cards = QHBoxLayout()
          self.balance_lbl   = QLabel("0.00")
          self.purchases_lbl = QLabel("0.00")
          self.paid_lbl      = QLabel("0.00")
          self.count_lbl     = QLabel("0")
          cards.addWidget(_make_card("Outstanding Balance", self.balance_lbl))
          cards.addWidget(_make_card("Total Purchases",     self.purchases_lbl))
          cards.addWidget(_make_card("Total Paid",          self.paid_lbl))
          cards.addWidget(_make_card("Invoices",            self.count_lbl))
          layout.addLayout(cards)

          tabs = QTabWidget()

          # Invoices tab
          self.inv_table = QTableWidget()
          self.inv_table.setColumnCount(6)
          self.inv_table.setHorizontalHeaderLabels(
              ["Invoice #", "Date", "Total", "Paid", "Remaining", "Status"])
          self.inv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
          self.inv_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
          self.inv_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
          for col in [2, 3, 4]:
              self.inv_table.setColumnWidth(col, 110)
          self.inv_table.setEditTriggers(QTableWidget.NoEditTriggers)
          self.inv_table.setSelectionBehavior(QTableWidget.SelectRows)
          theme.apply_table_style(self.inv_table)
          tabs.addTab(self.inv_table, "Invoices")

          # Payment History tab
          # Columns: Date | Invoice # | Amount | Remaining After | Notes
          self.pay_table = QTableWidget()
          self.pay_table.setColumnCount(5)
          self.pay_table.setHorizontalHeaderLabels(
              ["Date", "Invoice #", "Amount", "Remaining After", "Notes"])
          self.pay_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
          self.pay_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
          self.pay_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
          for col in [2, 3]:
              self.pay_table.setColumnWidth(col, 120)
          self.pay_table.setEditTriggers(QTableWidget.NoEditTriggers)
          theme.apply_table_style(self.pay_table)
          tabs.addTab(self.pay_table, "Payment History")

          layout.addWidget(tabs)

      def load_customer(self, customer_id: int):
          self._customer_id = customer_id
          self._refresh()

      def _refresh(self):
          if self._customer_id is None:
              return
          try:
              profile = customers_logic.get_customer_profile(self._customer_id)
          except Exception:
              traceback.print_exc()
              QMessageBox.critical(self, "Error", "Failed to load customer profile.")
              return

          c = profile["customer"]
          self.name_lbl.setText(c["name"])
          self.phone_lbl.setText(c.get("phone") or "")
          self.balance_lbl.setText(f"{profile['outstanding_balance']:,.2f}")
          self.purchases_lbl.setText(f"{profile['total_purchases']:,.2f}")
          self.paid_lbl.setText(f"{profile['total_paid']:,.2f}")
          self.count_lbl.setText(str(profile["invoice_count"]))

          self.receive_btn.setVisible(profile["outstanding_balance"] > 0)

          # Invoices tab
          self.inv_table.setRowCount(len(profile["invoices"]))
          for row, inv in enumerate(profile["invoices"]):
              status = inv["payment_status"]
              color  = STATUS_COLORS.get(status, theme._active.text_primary)
              for col, text in enumerate([
                  inv["invoice_number"],
                  inv["created_at"][:10],
                  f"{inv['total_amount']:,.2f}",
                  f"{inv['total_paid']:,.2f}",
                  f"{inv['remaining']:,.2f}",
                  status,
              ]):
                  item = QTableWidgetItem(text)
                  item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                  if col == 5:
                      item.setForeground(QColor(color))
                  self.inv_table.setItem(row, col, item)

          # Payment History tab — Date | Invoice # | Amount | Remaining After | Notes
          self.pay_table.setRowCount(len(profile["payments"]))
          for row, pay in enumerate(profile["payments"]):
              for col, text in enumerate([
                  pay["payment_date"][:10],
                  pay.get("invoice_number", ""),
                  f"{pay['amount']:,.2f}",
                  f"{pay['remaining_after']:,.2f}",
                  pay.get("notes") or "",
              ]):
                  item = QTableWidgetItem(text)
                  item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                  self.pay_table.setItem(row, col, item)

      def _on_receive_payment(self):
          if self._customer_id is None:
              return
          try:
              profile = customers_logic.get_customer_profile(self._customer_id)
          except Exception:
              traceback.print_exc()
              return
          from ui.receive_payment_dialog import ReceivePaymentDialog
          dlg = ReceivePaymentDialog(
              self._customer_id,
              profile["customer"]["name"],
              parent=self
          )
          if dlg.exec():
              self._refresh()
  ```

**Checkpoint (US3)**: Customer profile opens with correct summary cards and invoice statuses. Payment History tab has correct columns including Invoice #.

---

## Phase 7: Receive Payment Dialog

**Goal (US4)**: Modal dialog to collect payment against a specific invoice.

**Independent Test**: Quickstart Scenarios 4 & 5. Select an invoice in the dialog, enter amount, confirm. Balance decreases. History updated.

- [x] T014 [US4] Create `accounting_system/ui/receive_payment_dialog.py` — complete implementation:

  ```python
  import traceback
  from PySide6.QtWidgets import (
      QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
      QLabel, QComboBox, QDoubleSpinBox, QLineEdit,
      QDialogButtonBox, QMessageBox, QApplication,
  )
  from PySide6.QtCore import Qt

  from logic import customers_logic
  from ui import theme


  class ReceivePaymentDialog(QDialog):
      def __init__(self, customer_id: int, customer_name: str, parent=None):
          super().__init__(parent)
          self._customer_id = customer_id
          self._outstanding_invoices = []
          self.setWindowTitle(f"Receive Payment — {customer_name}")
          self.setMinimumWidth(420)
          self._load_invoices()
          self._build_ui()

      def _load_invoices(self):
          try:
              self._outstanding_invoices = customers_logic.get_outstanding_invoices_for_customer(
                  self._customer_id
              )
          except Exception:
              traceback.print_exc()
              self._outstanding_invoices = []

      def _build_ui(self):
          layout = QVBoxLayout(self)
          layout.setContentsMargins(24, 20, 24, 20)
          layout.setSpacing(12)

          if not self._outstanding_invoices:
              layout.addWidget(QLabel("No outstanding invoices for this customer."))
              btns = QDialogButtonBox(QDialogButtonBox.Close)
              btns.rejected.connect(self.reject)
              layout.addWidget(btns)
              return

          form = QFormLayout()
          form.setSpacing(10)

          # Invoice selector
          self.invoice_combo = QComboBox()
          for inv in self._outstanding_invoices:
              label = f"{inv['invoice_number']} | {inv['created_at'][:10]} | Outstanding: {inv['remaining']:,.2f}"
              self.invoice_combo.addItem(label, userData=inv)
          self.invoice_combo.currentIndexChanged.connect(self._on_invoice_changed)
          form.addRow("Invoice:", self.invoice_combo)

          # Outstanding for selected invoice
          self.outstanding_lbl = QLabel("0.00")
          self.outstanding_lbl.setStyleSheet(
              f"font-weight: bold; font-size: {theme._active.size_heading}pt;"
              f" background: transparent;")
          form.addRow("Invoice Outstanding:", self.outstanding_lbl)

          # Amount received
          self.amount_spin = QDoubleSpinBox()
          self.amount_spin.setDecimals(2)
          self.amount_spin.setFixedWidth(160)
          self.amount_spin.valueChanged.connect(self._on_amount_changed)
          form.addRow("Amount Received:", self.amount_spin)

          # Remaining after
          self.remaining_lbl = QLabel("0.00")
          self.remaining_lbl.setStyleSheet("background: transparent;")
          form.addRow("Remaining After Payment:", self.remaining_lbl)

          # Notes
          self.notes_edit = QLineEdit()
          self.notes_edit.setPlaceholderText("Optional note")
          form.addRow("Notes:", self.notes_edit)

          layout.addLayout(form)

          btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
          btns.button(QDialogButtonBox.Ok).setText("Confirm Payment")
          btns.accepted.connect(self._on_confirm)
          btns.rejected.connect(self.reject)
          layout.addWidget(btns)

          # Trigger initial population
          self._on_invoice_changed(0)

      def _current_invoice(self):
          return self.invoice_combo.currentData()

      def _on_invoice_changed(self, _index):
          inv = self._current_invoice()
          if not inv:
              return
          outstanding = inv["remaining"]
          self.outstanding_lbl.setText(f"{outstanding:,.2f}")
          self.amount_spin.setRange(0.01, outstanding)
          self.amount_spin.setValue(outstanding)
          self._on_amount_changed(outstanding)

      def _on_amount_changed(self, value):
          inv = self._current_invoice()
          if not inv:
              return
          remaining = max(0.0, round(inv["remaining"] - value, 2))
          self.remaining_lbl.setText(f"{remaining:,.2f}")

      def _on_confirm(self):
          inv    = self._current_invoice()
          amount = self.amount_spin.value()
          notes  = self.notes_edit.text().strip()
          if not inv:
              return
          QApplication.setOverrideCursor(Qt.WaitCursor)
          try:
              customers_logic.record_payment(
                  self._customer_id, inv["id"], amount, notes
              )
              QApplication.restoreOverrideCursor()
              QMessageBox.information(
                  self, "Payment Recorded",
                  f"Payment of {amount:,.2f} recorded against {inv['invoice_number']}."
              )
              self.accept()
          except ValueError as e:
              QApplication.restoreOverrideCursor()
              QMessageBox.warning(self, "Validation Error", str(e))
          except Exception:
              QApplication.restoreOverrideCursor()
              traceback.print_exc()
              QMessageBox.critical(self, "Error",
                  "An unexpected error occurred. Payment was not recorded.")
  ```

**Checkpoint (US4)**: Dialog shows invoice list. Selecting an invoice updates outstanding and amount range. Confirming records the payment and shows the invoice number in payment history.

---

## Phase 8: Dashboard KPI Cards

**Goal (US5)**: Two new KPI cards on Dashboard. Quickstart Scenario 6.

- [x] T015 [US5] Update `accounting_system/ui/dashboard_page.py` — add two new KPI cards and a receivables dialog.

  **Step 1** — Add import at the top:
  ```python
  from logic import customers_logic
  ```

  **Step 2** — Add signal to `DashboardPage` class:
  ```python
  navigate_to_customer = Signal(int)
  ```

  **Step 3** — In `_build_ui`, after building the existing KPI cards, create the two new ones:
  ```python
  self._receivables_value_lbl = QLabel("0.00")
  self._receivables_card = _make_card("Outstanding Receivables", self._receivables_value_lbl)
  self._receivables_card.setCursor(Qt.PointingHandCursor)
  self._receivables_card.mousePressEvent = lambda e: self._on_receivables_clicked()

  self._customers_balance_lbl = QLabel("0")
  self._customers_balance_card = _make_card("Customers With Balance", self._customers_balance_lbl)
  ```
  Add both to the KPI grid (same grid as existing cards, new row or extended row).

  **Step 4** — In the existing KPI refresh method (where `Total Sales` etc. are updated), add:
  ```python
  try:
      self._receivables_value_lbl.setText(
          f"{customers_logic.get_outstanding_receivables_total():,.2f}")
      self._customers_balance_lbl.setText(
          str(customers_logic.get_customers_with_outstanding_count()))
  except Exception:
      pass
  ```

  **Step 5** — Add the click handler:
  ```python
  def _on_receivables_clicked(self):
      from PySide6.QtWidgets import (
          QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
          QHeaderView, QLabel,
      )
      try:
          rows = customers_logic.get_customers_with_outstanding_list()
      except Exception:
          traceback.print_exc()
          return
      dlg = QDialog(self)
      dlg.setWindowTitle("Outstanding Receivables")
      dlg.setMinimumSize(400, 300)
      lay = QVBoxLayout(dlg)
      if not rows:
          lay.addWidget(QLabel("No outstanding receivables."))
      else:
          tbl = QTableWidget(len(rows), 2)
          tbl.setHorizontalHeaderLabels(["Customer", "Outstanding Balance"])
          tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
          tbl.setColumnWidth(1, 160)
          tbl.setEditTriggers(QTableWidget.NoEditTriggers)
          tbl.setSelectionBehavior(QTableWidget.SelectRows)
          for r, row in enumerate(rows):
              name_item = QTableWidgetItem(row["name"])
              name_item.setData(Qt.UserRole, row["id"])
              tbl.setItem(r, 0, name_item)
              tbl.setItem(r, 1, QTableWidgetItem(f"{row['outstanding_balance']:,.2f}"))
          def _on_double_click(idx):
              cid = tbl.item(idx.row(), 0).data(Qt.UserRole)
              self.navigate_to_customer.emit(cid)
              dlg.accept()
          tbl.doubleClicked.connect(_on_double_click)
          lay.addWidget(tbl)
          lay.addWidget(QLabel("Double-click to open customer profile."))
      dlg.exec()
  ```

  **Step 6** — In `main_window.py`, connect the new signal:
  ```python
  self.dashboard_page.navigate_to_customer.connect(self._on_open_customer_detail)
  ```

**Checkpoint (US5)**: Dashboard shows two new cards with correct values. Clicking Outstanding Receivables opens list dialog. Double-clicking a customer navigates to their profile.

---

## Phase 9: Customer Receivables Report

**Goal (US6)**: New "Customer Receivables" tab in Reports. Quickstart Scenario 7.

- [x] T016 [US6] Update `accounting_system/ui/reports_page.py` — add Customer Receivables tab.

  **Step 1** — Add import:
  ```python
  from logic import customers_logic
  ```

  **Step 2** — Add a `_build_receivables_tab` method:
  ```python
  def _build_receivables_tab(self) -> QWidget:
      from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
      widget = QWidget()
      layout = QVBoxLayout(widget)
      layout.setContentsMargins(
          theme._active.spacing_lg, theme._active.spacing_lg,
          theme._active.spacing_lg, theme._active.spacing_lg)
      layout.setSpacing(theme._active.spacing_md)

      controls = QHBoxLayout()
      self._recv_search = QLineEdit()
      self._recv_search.setPlaceholderText("Search customer name…")
      self._recv_search.textChanged.connect(self._refresh_receivables)
      controls.addWidget(self._recv_search, 1)
      layout.addLayout(controls)

      self._recv_table = QTableWidget()
      self._recv_table.setColumnCount(4)
      self._recv_table.setHorizontalHeaderLabels(
          ["Customer", "Total Sales", "Total Paid", "Outstanding Balance"])
      self._recv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
      for col in [1, 2, 3]:
          self._recv_table.setColumnWidth(col, 150)
      self._recv_table.setEditTriggers(QTableWidget.NoEditTriggers)
      self._recv_table.setSelectionBehavior(QTableWidget.SelectRows)
      self._recv_table.setSortingEnabled(True)
      theme.apply_table_style(self._recv_table)
      layout.addWidget(self._recv_table)

      return widget
  ```

  **Step 3** — In the method that builds the QTabWidget (where existing tabs are added), append:
  ```python
  self.tab_widget.addTab(self._build_receivables_tab(), "Customer Receivables")
  ```
  (Replace `self.tab_widget` with whatever the existing tab widget variable name is in `reports_page.py`.)

  **Step 4** — Add the refresh method:
  ```python
  def _refresh_receivables(self):
      if not hasattr(self, '_recv_table'):
          return
      search = self._recv_search.text().strip() if hasattr(self, '_recv_search') else ""
      try:
          data = customers_logic.get_receivables_report(search=search or None)
      except Exception:
          import traceback; traceback.print_exc()
          return
      self._recv_table.setSortingEnabled(False)
      self._recv_table.setRowCount(len(data))
      for row, r in enumerate(data):
          for col, text in enumerate([
              r["name"],
              f"{r['total_sales']:,.2f}",
              f"{r['total_paid']:,.2f}",
              f"{r['outstanding_balance']:,.2f}",
          ]):
              item = QTableWidgetItem(text)
              item.setFlags(item.flags() & ~Qt.ItemIsEditable)
              self._recv_table.setItem(row, col, item)
      self._recv_table.setSortingEnabled(True)
  ```

  **Step 5** — Call `self._refresh_receivables()` inside the existing `_refresh` or `_apply_filter` method so the tab stays up to date.

**Checkpoint (US6)**: Reports page shows Customer Receivables tab. Data matches customer profile totals.

---

## Phase 10: Polish & Validation

- [x] T017 Add a `customers.svg` icon to `accounting_system/ui/icons/`. If creating SVG is not feasible, copy any existing icon (e.g., `products.svg`) and rename it `customers.svg`. The `if os.path.exists` guard in `main_window.py` means a missing icon silently degrades — no crash.

- [x] T018 Verify `showEvent` on `SalesPage` refreshes the customer combo. The implementation in T010 Step 7 adds `showEvent` — confirm it is present and works after navigating away and back.

- [x] T019 Verify Dashboard KPI cards refresh after a payment is recorded. Open Dashboard → open a customer → receive payment → navigate back to Dashboard. Cards should show updated totals. If not, ensure `_refresh_all_pages` in `main_window.py` also calls `_refresh` on `DashboardPage` (check the existing `_refresh_all_pages` method).

- [x] T020 Run through all 8 manual scenarios in `specs/008-customer-credit-receivables/quickstart.md` and verify each expected outcome. Fix any discrepancy found during testing.

- [x] T021 Verify that voiding an existing invoice excludes it from all balance calculations. The balance formula filters `status = 'active'` — confirm that voiding an invoice with payments attached: (a) excludes it from customer outstanding balance, (b) retains payment records in history (no deletion), (c) does not crash.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Schema)**: No dependencies — start here
- **Phase 2 (DB modules)**: Depends on Phase 1
- **Phase 3 (Logic)**: Depends on Phase 2
- **Phase 4 (Sales UI)**: Depends on Phase 3
- **Phase 5 (Customers Page)**: Depends on Phase 3; can start alongside Phase 4
- **Phase 6 (Customer Detail)**: Depends on Phase 5 (nav wired in T011)
- **Phase 7 (Receive Payment)**: Depends on Phase 6
- **Phase 8 (Dashboard)**: Depends on Phase 3; can start alongside Phase 5
- **Phase 9 (Reports)**: Depends on Phase 3; can start alongside Phase 5
- **Phase 10 (Polish)**: Depends on all prior phases

### Parallel Opportunities

- T005 and T006 (Phase 2) — different files, run simultaneously
- Phases 5, 8, 9 — all depend only on Phase 3, can be worked in parallel

---

## Implementation Strategy

### MVP (Phases 1–4 only)

Complete Phases 1–4. The app can record partial invoices with customer linkage. Test with `quickstart.md` Scenarios 1 & 2.

### Full Feature

Complete all phases in order. Each phase adds a testable increment that does not break previous phases.

---

## Notes

- **No `remaining_balance` column on Sales** — this column does NOT exist. Always derive it.
- **Payments link to `sale_id`** — do not implement customer-only payment records.
- **Payment status is derived** — never store "Paid"/"Unpaid" on the Sales row.
- All SQL is parameterized. Multi-table operations use transactions with commit/rollback.
- No PySide6 in logic files. No `*_db.py` imports in UI files.
- `_refresh()` methods must handle empty data gracefully (COALESCE in SQL, `or ""` in Python).
- `customer_name` column on Sales is retained for backward-compatibility — both `customer_name` (text copy) and `customer_id` (FK) are written on new invoices.
