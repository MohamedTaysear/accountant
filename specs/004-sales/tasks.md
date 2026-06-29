# Tasks: Phase 4 — Sales

**Input**: Design documents from `specs/004-sales/`

**Prerequisites satisfied**: plan.md ✓ spec.md ✓ research.md ✓ data-model.md ✓ quickstart.md ✓

**Tests**: No automated tests — manual testing only per quickstart.md checkpoints.

**Stack**: Python + PySide6 + SQLite. No new dependencies. Three new files only.

**Architecture rule (NON-NEGOTIABLE)**: UI → Logic → Data Access → Foundation.
- `ui/sales_page.py` imports `logic/sales_logic.py` and `products_db.py` only. NEVER imports `sqlite3` or `database.py`.
- `logic/sales_logic.py` imports `sales_db.py` and `products_db.py` only. NEVER imports PySide6.
- `sales_db.py` imports `database` only. All SQL is parameterized. No business rules.

**Reference implementations** (study these before writing):
- `accounting_system/purchases_db.py` — identical transaction pattern for sales_db.py
- `accounting_system/logic/purchase_logic.py` — identical delegation pattern for sales_logic.py
- `accounting_system/ui/purchases_page.py` — closest structural match for sales_page.py

---

## Phase 1: Setup

**Purpose**: Verify environment and confirm existing files compile before adding new code.

- [x] T001 Verify the application still runs by executing `python accounting_system/main.py` from `C:\accountant\accounting_system\` — confirm Login window appears; close it immediately. This confirms Phases 1–3 baseline is intact before Phase 4 work begins.

- [x] T002 Confirm `accounting_system/sales_db.py` does NOT yet exist (it will be created in Phase 2). Confirm `accounting_system/ui/sales_page.py` IS a placeholder (it exists but contains only `pass` or a simple `QWidget` with a label). If it is already a full implementation, stop and report.

---

## Phase 2: Foundational — Data Access Layer

**Purpose**: Create `sales_db.py` with all raw SQL functions. This file MUST be complete before any logic or UI work.

**⚠️ CRITICAL**: No US1/US2/US3/US4 work can begin until this phase is complete.

**File to create**: `accounting_system/sales_db.py`

**Pattern to follow**: `accounting_system/purchases_db.py` — same structure, same connection handling, same transaction approach.

---

- [x] T003 Create `accounting_system/sales_db.py` with the module-level import only:
  ```python
  import database
  ```
  No other imports. Save and confirm the file is importable: `python -c "import sys; sys.path.insert(0,'accounting_system'); import sales_db; print('OK')"`.

- [x] T004 Add function `get_next_invoice_number() -> str` to `accounting_system/sales_db.py`:
  ```python
  def get_next_invoice_number() -> str:
      conn = database.get_connection()
      try:
          row = conn.execute("SELECT MAX(id) FROM Sales").fetchone()
          max_id = row[0] if row[0] is not None else 0
          return f"SAL-{max_id + 1:06d}"
      finally:
          conn.close()
  ```
  This is a preview number — shown before save. The actual number after save is derived from `lastrowid`.

- [x] T005 Add function `insert_sale_with_items(customer_name, discount_amount: float, items: list) -> str` to `accounting_system/sales_db.py`. This is the core atomic transaction. Implement it exactly as follows:
  ```python
  def insert_sale_with_items(customer_name, discount_amount: float, items: list) -> str:
      subtotal = sum(item["subtotal"] for item in items)
      total_amount = subtotal - discount_amount
      conn = database.get_connection()
      try:
          conn.execute(
              "INSERT INTO Sales (invoice_number, customer_name, discount_amount, total_amount, status) VALUES (?, ?, ?, ?, 'active')",
              ("PENDING", customer_name, discount_amount, total_amount)
          )
          sale_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
          invoice_number = f"SAL-{sale_id:06d}"
          conn.execute(
              "UPDATE Sales SET invoice_number = ? WHERE id = ?",
              (invoice_number, sale_id)
          )
          for item in items:
              purchase_price_at_sale = conn.execute(
                  "SELECT purchase_price FROM Products WHERE id = ?",
                  (item["product_id"],)
              ).fetchone()[0]
              conn.execute(
                  "INSERT INTO SaleItems (sale_id, product_id, quantity, unit_price, purchase_price_at_sale, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                  (sale_id, item["product_id"], item["quantity"], item["unit_price"], purchase_price_at_sale, item["subtotal"])
              )
              conn.execute(
                  "UPDATE Products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                  (item["quantity"], item["product_id"])
              )
          conn.commit()
          return invoice_number
      except Exception:
          conn.rollback()
          raise
      finally:
          conn.close()
  ```
  Key points:
  - `purchase_price_at_sale` is fetched inside the transaction (save-time, not line-add-time).
  - Stock is DECREMENTED (not incremented — this is Sales, not Purchases).
  - The initial `invoice_number` placeholder `"PENDING"` is immediately replaced with the real number using `last_insert_rowid()`.
  - Single `conn.commit()` at the end — all steps succeed or nothing commits.

- [x] T006 Add function `get_sale_by_id(sale_id: int)` to `accounting_system/sales_db.py`:
  ```python
  def get_sale_by_id(sale_id: int):
      conn = database.get_connection()
      try:
          return conn.execute(
              "SELECT * FROM Sales WHERE id = ?", (sale_id,)
          ).fetchone()
      finally:
          conn.close()
  ```

- [x] T007 Add function `get_sale_items(sale_id: int)` to `accounting_system/sales_db.py`:
  ```python
  def get_sale_items(sale_id: int):
      conn = database.get_connection()
      try:
          return conn.execute(
              """SELECT si.*, p.name as product_name
                 FROM SaleItems si
                 JOIN Products p ON si.product_id = p.id
                 WHERE si.sale_id = ?""",
              (sale_id,)
          ).fetchall()
      finally:
          conn.close()
  ```

- [x] T008 Add function `get_all_sales(start_date=None, end_date=None)` to `accounting_system/sales_db.py`:
  ```python
  def get_all_sales(start_date=None, end_date=None):
      conn = database.get_connection()
      try:
          if start_date and end_date:
              return conn.execute(
                  """SELECT * FROM Sales
                     WHERE DATE(created_at) BETWEEN ? AND ?
                     ORDER BY created_at DESC""",
                  (start_date, end_date)
              ).fetchall()
          return conn.execute(
              "SELECT * FROM Sales ORDER BY created_at DESC"
          ).fetchall()
      finally:
          conn.close()
  ```

- [x] T009 Add function `void_sale(sale_id: int)` to `accounting_system/sales_db.py`. This is needed by Phase 5 but must be defined now so the logic layer can reference it:
  ```python
  def void_sale(sale_id: int) -> None:
      conn = database.get_connection()
      try:
          items = conn.execute(
              "SELECT product_id, quantity FROM SaleItems WHERE sale_id = ?",
              (sale_id,)
          ).fetchall()
          conn.execute(
              "UPDATE Sales SET status = 'voided' WHERE id = ?",
              (sale_id,)
          )
          for item in items:
              conn.execute(
                  "UPDATE Products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                  (item["quantity"], item["product_id"])
              )
          conn.commit()
      except Exception:
          conn.rollback()
          raise
      finally:
          conn.close()
  ```

- [x] T010 Verify `sales_db.py` is complete and importable with all functions present:
  ```
  python -c "
  import sys; sys.path.insert(0,'accounting_system')
  import database, auth
  database.initialize_database()
  auth.seed_default_admin()
  import sales_db
  print('get_next_invoice_number:', sales_db.get_next_invoice_number())
  print('sales_db OK — all functions importable')
  "
  ```
  Expected output includes `SAL-000001` (or similar) and no ImportError or AttributeError.

---

## Phase 3: User Story 1 — Build and Save a Sales Invoice (Priority: P1) 🎯 MVP

**Goal**: The user selects products, enters quantities, optionally adds customer name and discount, and saves a multi-line invoice. Stock decrements atomically.

**Independent Test**: quickstart.md Checkpoints 1, 5, 9, 10.

### Implementation

- [x] T011 [US1] Create `accounting_system/logic/sales_logic.py`. Start with imports and two simple functions:
  ```python
  import sales_db
  import products_db

  def get_next_invoice_number() -> str:
      return sales_db.get_next_invoice_number()

  def calculate_subtotal(quantity: float, unit_price: float) -> float:
      return round(quantity * unit_price, 10)

  def calculate_total(items: list, discount: float) -> float:
      subtotal = sum(item["subtotal"] for item in items)
      return max(0.0, subtotal - discount)
  ```
  No PySide6 imports. No SQL. Save and verify import:
  ```
  python -c "import sys; sys.path.insert(0,'accounting_system'); import sales_db, products_db; import logic.sales_logic as sl; print('sales_logic OK')"
  ```

- [x] T012 [US1] Add `validate_line(quantity: float, unit_price: float) -> tuple[bool, str]` to `accounting_system/logic/sales_logic.py`:
  ```python
  def validate_line(quantity: float, unit_price: float) -> tuple:
      if quantity <= 0:
          return False, "Quantity must be greater than 0."
      if unit_price < 0:
          return False, "Unit price cannot be negative."
      return True, ""
  ```

- [x] T013 [US1] Add `validate_stock(product_id: int, quantity: float, current_items: list) -> tuple[bool, str]` to `accounting_system/logic/sales_logic.py`. This implements the "effective available stock" rule (FR-008 / research Decision 3):
  ```python
  def validate_stock(product_id: int, quantity: float, current_items: list) -> tuple:
      # Sum quantities already queued for this product in the current in-progress invoice
      already_queued = sum(
          item["quantity"] for item in current_items
          if item["product_id"] == product_id
      )
      # Fetch current DB stock
      rows = products_db.get_active_products()
      product = next((r for r in rows if r["id"] == product_id), None)
      if product is None:
          return False, "Product is not available."
      effective_available = product["stock_quantity"] - already_queued
      if quantity > effective_available:
          return False, (
              f"Insufficient stock. Available: {effective_available}, "
              f"Requested: {quantity}."
          )
      return True, ""
  ```

- [x] T014 [US1] Add `save_sale(customer_name, discount_amount: float, items: list) -> str` to `accounting_system/logic/sales_logic.py`:
  ```python
  def save_sale(customer_name, discount_amount: float, items: list) -> str:
      if not items:
          raise ValueError("Invoice must have at least one item before saving.")
      subtotal = sum(item["subtotal"] for item in items)
      if discount_amount > subtotal:
          raise ValueError(
              f"Discount ({discount_amount}) cannot exceed invoice subtotal ({subtotal})."
          )
      customer = customer_name.strip() if customer_name else None
      return sales_db.insert_sale_with_items(customer, discount_amount, items)
  ```

- [x] T015 [US1] Add `void_sale(sale_id: int) -> None` to `accounting_system/logic/sales_logic.py` (used by Phase 5 Invoice Detail Dialog):
  ```python
  def void_sale(sale_id: int) -> None:
      sale = sales_db.get_sale_by_id(sale_id)
      if sale is None:
          raise ValueError("Sale not found.")
      if sale["status"] == "voided":
          raise ValueError("This invoice has already been voided.")
      sales_db.void_sale(sale_id)
  ```

- [x] T016 [US1] Verify `logic/sales_logic.py` is complete and importable:
  ```
  python -c "
  import sys; sys.path.insert(0,'accounting_system')
  import database, auth
  database.initialize_database(); auth.seed_default_admin()
  from logic import sales_logic
  print('get_next_invoice_number:', sales_logic.get_next_invoice_number())
  print('calculate_total:', sales_logic.calculate_total([{'subtotal': 50}], 10))
  print('sales_logic OK')
  "
  ```
  Expected: `SAL-000001` (or next available), `40.0`, no errors.

- [x] T017 [US1] Replace the placeholder content of `accounting_system/ui/sales_page.py` with the full implementation. Write the complete file as follows.

  **Module-level helpers and imports** (at the very top, before class definition):
  ```python
  import traceback

  def _fmt(v) -> str:
      s = f"{v:.2f}"
      return s.rstrip("0").rstrip(".")

  def _fmt_total(v) -> str:
      s = f"{v:,.2f}"
      if "." in s:
          integer_part, frac_part = s.split(".")
          frac_part = frac_part.rstrip("0")
          return integer_part if not frac_part else f"{integer_part}.{frac_part}"
      return s

  from PySide6.QtWidgets import (
      QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
      QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
      QPushButton, QTableWidget, QTableWidgetItem,
      QHeaderView, QMessageBox, QApplication
  )
  from PySide6.QtCore import Qt, QDate
  from PySide6.QtGui import QColor

  class _SpinBox(QDoubleSpinBox):
      def textFromValue(self, value: float) -> str:
          s = f"{value:.2f}"
          return s.rstrip("0").rstrip(".")

  import products_db
  from logic import sales_logic
  ```

  **Class skeleton** — `SalesPage(QWidget)` with `__init__`:
  ```python
  class SalesPage(QWidget):
      def __init__(self, parent=None):
          super().__init__(parent)
          self._items = []          # list of dicts: product_id, product_name, quantity, unit_price, subtotal
          self._build_ui()
          self._refresh_invoice_number()
  ```

- [x] T018 [US1] Implement `_build_ui(self)` inside `SalesPage`. Build the layout in this exact order:

  **Invoice header form** (QFormLayout):
  - `self.invoice_number_label = QLabel("SAL-000001")` — row label "Invoice #:"
  - `self.date_label = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))` — row label "Date:"
  - `self.customer_input = QLineEdit()` with placeholder "Optional customer name" — row label "Customer:"

  **Product selection row** (QHBoxLayout):
  - `self.product_combo = QComboBox()`, `setMinimumWidth(220)`, `setEditable(False)`
  - `self.qty_spin = _SpinBox()`, range `(0.01, 999_999)`, decimals 2, value 1.0
  - `self.add_line_btn = QPushButton("Add to Invoice")`
  - Layout: Label "Product:", combo (stretch=2), Label "Qty:", qty_spin, add_line_btn

  **Line-items table** (QTableWidget):
  - `self.table = QTableWidget()`, `setColumnCount(5)`
  - Headers: `["Product", "Qty", "Unit Price", "Subtotal", ""]`
  - `setSectionResizeMode(0, QHeaderView.Stretch)` on horizontal header
  - `setEditTriggers(QTableWidget.NoEditTriggers)`
  - `setSelectionBehavior(QTableWidget.SelectRows)`

  **Footer** (QHBoxLayout):
  - `self.subtotal_label = QLabel("Subtotal: 0")` — bold font
  - Discount row: `QLabel("Discount:")` + `self.discount_spin = _SpinBox()` (range 0–9_999_999, decimals 2, value 0.0)
  - `self.grand_total_label = QLabel("Grand Total: 0")` — bold font
  - `self.clear_btn = QPushButton("Clear Invoice")`
  - `self.save_btn = QPushButton("Save Invoice")`
  - Layout: subtotal_label, stretch, Label "Discount:", discount_spin, grand_total_label, stretch, clear_btn, save_btn

  **Signal connections**:
  ```python
  self.product_combo.currentIndexChanged.connect(self._on_product_selected)
  self.add_line_btn.clicked.connect(self._on_add_line)
  self.discount_spin.valueChanged.connect(self._on_discount_changed)
  self.clear_btn.clicked.connect(self._on_clear)
  self.save_btn.clicked.connect(self._on_save)
  ```

- [x] T019 [US1] Implement helper methods inside `SalesPage`:

  ```python
  def _refresh_invoice_number(self):
      try:
          num = sales_logic.get_next_invoice_number()
          self.invoice_number_label.setText(num)
      except Exception:
          self.invoice_number_label.setText("SAL-??????")

  def _reload_products(self):
      self.product_combo.blockSignals(True)
      self.product_combo.clear()
      try:
          rows = products_db.get_active_products()
          for row in rows:
              self.product_combo.addItem(
                  row["name"],
                  userData={"id": row["id"], "name": row["name"],
                            "selling_price": row["selling_price"]}
              )
      except Exception:
          print(traceback.format_exc())
      self.product_combo.blockSignals(False)

  def _get_subtotal(self) -> float:
      return sum(item["subtotal"] for item in self._items)

  def _update_totals(self):
      subtotal = self._get_subtotal()
      discount = self.discount_spin.value()
      grand_total = max(0.0, subtotal - discount)
      self.subtotal_label.setText(f"Subtotal: {_fmt_total(subtotal)}")
      self.grand_total_label.setText(f"Grand Total: {_fmt_total(grand_total)}")
      # Visual error state on discount field (FR-013, FR-013a)
      if discount > subtotal:
          self.discount_spin.setStyleSheet("QDoubleSpinBox { border: 2px solid red; }")
      else:
          self.discount_spin.setStyleSheet("")

  def _rebuild_table(self):
      self.table.setRowCount(0)
      for idx, item in enumerate(self._items):
          r = self.table.rowCount()
          self.table.insertRow(r)
          self.table.setItem(r, 0, QTableWidgetItem(item["product_name"]))
          self.table.setItem(r, 1, QTableWidgetItem(_fmt(item["quantity"])))
          self.table.setItem(r, 2, QTableWidgetItem(_fmt(item["unit_price"])))
          self.table.setItem(r, 3, QTableWidgetItem(_fmt(item["subtotal"])))
          remove_btn = QPushButton("Remove")
          remove_btn.clicked.connect(
              lambda checked=False, i=idx: self._on_remove_line(i))
          self.table.setCellWidget(r, 4, remove_btn)

  def _reset_form(self):
      self._items = []
      self.customer_input.clear()
      self.discount_spin.setValue(0.0)
      self.discount_spin.setStyleSheet("")
      self._rebuild_table()
      self._update_totals()
      self._refresh_invoice_number()
  ```

- [x] T020 [US1] Implement signal handler methods inside `SalesPage`:

  ```python
  def _on_product_selected(self, index):
      if index >= 0:
          self.qty_spin.setFocus()
          self.qty_spin.selectAll()

  def _on_discount_changed(self, value: float):
      self._update_totals()

  def _on_add_line(self):
      idx = self.product_combo.currentIndex()
      if idx < 0:
          QMessageBox.warning(self, "No Product", "Please select a product first.")
          return
      product_data = self.product_combo.itemData(idx)
      quantity = self.qty_spin.value()
      unit_price = product_data["selling_price"]
      ok, msg = sales_logic.validate_line(quantity, unit_price)
      if not ok:
          QMessageBox.warning(self, "Validation Error", msg)
          return
      ok, msg = sales_logic.validate_stock(product_data["id"], quantity, self._items)
      if not ok:
          QMessageBox.warning(self, "Insufficient Stock", msg)
          return
      subtotal = sales_logic.calculate_subtotal(quantity, unit_price)
      self._items.append({
          "product_id":   product_data["id"],
          "product_name": product_data["name"],
          "quantity":     quantity,
          "unit_price":   unit_price,
          "subtotal":     subtotal,
      })
      self._rebuild_table()
      self._update_totals()
      self.qty_spin.setValue(1.0)
      self.product_combo.setFocus()

  def _on_remove_line(self, index: int):
      if 0 <= index < len(self._items):
          self._items.pop(index)
          self._rebuild_table()
          self._update_totals()

  def _on_clear(self):
      if self._items:
          answer = QMessageBox.question(
              self, "Clear Invoice",
              "Are you sure you want to clear this invoice?\n"
              "All unsaved line items will be lost.",
              QMessageBox.Yes | QMessageBox.No,
              QMessageBox.No
          )
          if answer != QMessageBox.Yes:
              return
      self._reset_form()

  def _on_save(self):
      if not self._items:
          QMessageBox.warning(self, "Empty Invoice",
              "Invoice must have at least one item before saving.")
          return
      discount = self.discount_spin.value()
      subtotal = self._get_subtotal()
      if discount > subtotal:
          QMessageBox.warning(self, "Invalid Discount",
              f"Discount ({_fmt(discount)}) cannot exceed invoice subtotal ({_fmt(subtotal)}).")
          return
      customer = self.customer_input.text().strip() or None
      QApplication.setOverrideCursor(Qt.WaitCursor)
      try:
          invoice_number = sales_logic.save_sale(customer, discount, self._items)
          QApplication.restoreOverrideCursor()
          QMessageBox.information(
              self, "Saved",
              f"Sales invoice {invoice_number} saved successfully.")
          self._reset_form()
      except ValueError as e:
          QApplication.restoreOverrideCursor()
          QMessageBox.warning(self, "Cannot Save", str(e))
      except Exception:
          QApplication.restoreOverrideCursor()
          print(traceback.format_exc())
          QMessageBox.critical(self, "Unexpected Error",
              "An unexpected error occurred while saving. Please try again.\n"
              "Your invoice data has been preserved.")

  def showEvent(self, event):
      super().showEvent(event)
      self._reload_products()   # refresh active products — do NOT call _reset_form() here
  ```

- [x] T021 [US1] Run the application and verify it imports cleanly:
  ```
  python -c "
  import sys; sys.path.insert(0,'accounting_system')
  import database, auth
  database.initialize_database(); auth.seed_default_admin()
  from PySide6.QtWidgets import QApplication
  app = QApplication(sys.argv)
  from ui.sales_page import SalesPage
  page = SalesPage()
  print('SalesPage import and instantiation: OK')
  print('Column count:', page.table.columnCount())
  "
  ```
  Expected: `SalesPage import and instantiation: OK`, column count `5`. No errors.

- [x] T022 [US1] Manual test — quickstart.md Checkpoint 1:
  - Launch `python accounting_system/main.py`, log in.
  - Navigate to Sales page.
  - Verify invoice number label shows `SAL-000001` (or next expected).
  - Add at least two products from the picker, verify subtotal updates.
  - Enter customer name and 0 discount, save — verify success message with invoice number.
  - Navigate to Products page, verify stock decremented correctly.

  Mark this task complete only after the checkpoint passes manually.

- [x] T023 [US1] Manual test — quickstart.md Checkpoints 5 (empty invoice blocked), 9 (wait cursor), 10 (invoice number sequence):
  - Attempt to save with zero lines — verify blocked.
  - Save an invoice and observe the wait cursor briefly appears.
  - Save a second invoice — verify number increments (e.g. `SAL-000002`).

  Mark complete only after all three sub-checks pass.

**Checkpoint US1**: `SalesPage` fully functional — save, stock decrement, wait cursor, invoice numbering, empty-invoice block all verified.

---

## Phase 4: User Story 2 — Stock Availability Validation (Priority: P2)

**Goal**: Block any line-add where quantity > effective available stock (DB stock − already queued for the same product). Verified end-to-end.

**Independent Test**: quickstart.md Checkpoints 2 and 3.

**Note**: The logic for US2 (`validate_stock`) was already implemented in T013 as part of the foundational logic layer, and `_on_add_line` in T020 already calls it. This phase is validation-only — verify the behaviour is correct, no new code required unless a bug is found.

- [x] T024 [US2] Manual test — quickstart.md Checkpoint 2 (single-product oversell blocked):
  - Stock Widget A to a known quantity via the Purchases page (e.g. 17 units).
  - On Sales page: attempt to add Widget A × 20 — must be blocked with an error.
  - Add Widget A × 17 — must succeed.

- [x] T025 [US2] Manual test — quickstart.md Checkpoint 3 (effective stock — same product twice):
  - Add Widget A × 10 (accepted). Attempt Widget A × 10 again — effective available = 17 − 10 = 7; must be blocked.
  - Attempt Widget A × 5 — must succeed (17 − 10 = 7; 5 ≤ 7).
  - Attempt Widget A × 5 again — effective available = 17 − 15 = 2; must be blocked.

**Checkpoint US2**: Effective stock validation works for single-product and multi-line-same-product scenarios.

---

## Phase 5: User Story 3 — Discount Validation (Priority: P3)

**Goal**: Discount > subtotal is blocked at save; Grand Total clamped to 0 in real time; discount field shows red border when invalid; clears on correction.

**Independent Test**: quickstart.md Checkpoint 4.

**Note**: All discount logic was implemented in T014 (`save_sale` raises `ValueError`), T019 (`_update_totals` clamps display and sets red border), and T020 (`_on_save` checks discount before calling logic). This phase is verification-only.

- [x] T026 [US3] Manual test — quickstart.md Checkpoint 4:
  - Add Widget A × 2 and Widget B × 2 (subtotal 80 assuming prices from setup).
  - Enter discount 100 — verify Grand Total shows 0 (not −20) and discount spin border turns red.
  - Attempt Save — must be blocked with a clear message.
  - Change discount to 20 — verify red border disappears and Grand Total shows 60.
  - Save — must succeed.

**Checkpoint US3**: Discount validation, real-time clamping, visual error state, and save-block all verified.

---

## Phase 6: User Story 4 — In-Progress Invoice Retained on Navigation (Priority: P4)

**Goal**: Navigating away from and back to the Sales page does not lose in-progress work.

**Independent Test**: quickstart.md Checkpoint 7.

**Note**: This behaviour is guaranteed by design — `showEvent` calls only `_reload_products()` and does NOT call `_reset_form()`. This was specified in T020. This phase is verification-only.

- [x] T027 [US4] Manual test — quickstart.md Checkpoint 7:
  - Add two lines to a sales invoice and enter a customer name and discount.
  - Navigate to Products (sidebar).
  - Navigate back to Sales.
  - Verify all lines, customer name, and discount are still present.
  - Verify the product combo has refreshed (add a new product via the Products page while away, then return and confirm it appears).

**Checkpoint US4**: Navigation retention confirmed; product list refreshed on return.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final verification — active-product picker, Clear Invoice confirmation, regressions.

- [x] T028 Manual test — quickstart.md Checkpoint 6 (Clear Invoice confirmation):
  - Add a line, click Clear — confirm dialog appears; click Cancel — lines remain.
  - Click Clear again — confirm Yes — invoice clears.
  - Click Clear with no lines — no dialog, instant clear.

- [x] T029 Manual test — quickstart.md Checkpoint 8 (active-products-only picker):
  - Deactivate a product on the Products page.
  - Navigate to Sales — confirm deactivated product does NOT appear in the combo.
  - Reactivate — navigate back to Sales — confirm it reappears.

- [x] T030 Manual test — quickstart.md Checkpoint 11 (no regressions from Phases 1–3):
  - Log out and back in — credentials still work.
  - Products page: add, edit, search — all functional.
  - Purchases page: create a purchase invoice — saves correctly, stock increases.
  - All sidebar pages navigate without crashes.

- [x] T031 Verify the layered-architecture constraint: open `accounting_system/ui/sales_page.py` and confirm:
  - The word `sqlite3` does NOT appear anywhere in the file.
  - `database` is NOT imported anywhere in the file.
  - Only `products_db` and `logic.sales_logic` (or `from logic import sales_logic`) are imported as project modules.

- [x] T032 Verify `accounting_system/logic/sales_logic.py` contains no PySide6 imports:
  - `python -c "import ast, open; ..."` or simply open the file and confirm no line contains `PySide6`, `QWidget`, `QMessageBox`, or any Qt import.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start here.
- **Phase 2 (Foundational / sales_db.py)**: Depends on Phase 1. Blocks all US phases.
- **Phase 3 (US1)**: Depends on Phase 2 complete. Creates logic layer AND full UI.
- **Phase 4 (US2)**: Depends on Phase 3 (validate_stock already in place — verification only).
- **Phase 5 (US3)**: Depends on Phase 3 (discount logic already in place — verification only).
- **Phase 6 (US4)**: Depends on Phase 3 (showEvent already correct — verification only).
- **Phase 7 (Polish)**: Depends on all above.

### Within-Phase Task Order

- T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 (all sequential, same file)
- T011 → T012 → T013 → T014 → T015 → T016 (sequential, building up sales_logic.py)
- T017 → T018 → T019 → T020 → T021 → T022 → T023 (sequential, building up sales_page.py)

### Parallel Opportunities

This is a single-developer, 3-file phase. No meaningful parallelism applies. All tasks are sequential within each phase to avoid conflicts on the same file.

---

## Implementation Strategy

### MVP First (complete US1, then verify US2–US4)

1. Complete Phase 1 (setup check) — 5 minutes.
2. Complete Phase 2 (sales_db.py, T003–T010) — ~20 minutes.
3. Complete Phase 3 US1 (sales_logic.py + sales_page.py, T011–T023) — ~45 minutes.
4. **STOP and VALIDATE**: Run quickstart.md Checkpoints 1, 5, 9, 10.
5. Complete Phase 4 US2 (T024–T025) — verification only, ~10 minutes.
6. Complete Phase 5 US3 (T026) — verification only, ~5 minutes.
7. Complete Phase 6 US4 (T027) — verification only, ~5 minutes.
8. Complete Phase 7 Polish (T028–T032) — ~15 minutes.
9. All 11 quickstart.md checkpoints should now pass.

---

## Notes

- `_fmt()` and `_fmt_total()` are copy-pasted from `purchases_page.py` — identical helpers, same behaviour (no trailing `.00`, thousands separator for totals only).
- `_SpinBox` subclass is copy-pasted from `purchases_page.py` — overrides `textFromValue` to strip trailing zeros.
- The `showEvent` must call `_reload_products()` but NEVER `_reset_form()`. This is the single most common mistake in this phase.
- `unit_price` for a sale line is auto-populated from `product_data["selling_price"]` — NOT entered by the user (unlike Purchases where the user types the price).
- `purchase_price_at_sale` is NOT stored in `self._items` — it is fetched inside the DB transaction in `sales_db.insert_sale_with_items`.
- The discount validation happens twice: once in real-time in `_on_discount_changed` → `_update_totals` (visual feedback only, no block) and once in `_on_save` (hard block before calling logic layer).
