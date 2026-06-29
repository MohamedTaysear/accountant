---
description: "Task list for Phase 3 — Purchase Invoice Management"
---

# Tasks: Purchase Invoice Management

**Input**: Design documents from `specs/003-purchases/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | data-model.md ✅ | research.md ✅ | quickstart.md ✅

**Tests**: Not requested — no test tasks generated.

**Organization**: Strictly bottom-up per plan.md. Inline implementation guidance with
full code blocks provided so a smaller LLM model can complete every task without
reading any additional document.

**Project root**: `accounting_system/` (all file paths below are relative to it)

**Phase 1–2 files already exist and MUST NOT be modified** unless a task explicitly
says so:
`config.py`, `database.py`, `auth_db.py`, `auth.py`, `products_db.py`, `main.py`,
`logic/__init__.py`, `ui/__init__.py`, `ui/login_window.py`, `ui/main_window.py`,
`ui/change_password_dialog.py`, `ui/product_dialog.py`, `ui/products_page.py`,
and the four remaining placeholder pages.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no cross-task dependency)
- **[Story]**: Maps to user stories US1–US4 from spec.md
- Every task includes the exact target file path

---

## Phase 1: Setup

No new directories needed — `logic/` already exists from Phase 1 skeleton.
Verify `logic/__init__.py` exists (it should from Phase 1).

- [x] T001 Verify `accounting_system/logic/__init__.py` exists. If it does not, create it
  as an empty file. This is required before `purchase_logic.py` can be imported.

  ```
  # logic/__init__.py — empty file, exists to make logic/ a Python package
  ```

---

## Phase 2: Foundation — `purchases_db.py` (blocking prerequisite for all user stories)

**Purpose**: All parameterized SQL for the `Purchases` and `PurchaseItems` tables,
plus stock/price updates on `Products`. No business rules — only SQL.

**Checkpoint**: `python -c "import purchases_db; print('OK')"` from `accounting_system/` → prints `OK`.

- [x] T002 Create `accounting_system/purchases_db.py` with all 5 functions below.
  Every function opens its own connection via `database.get_connection()`, performs
  its operation, and closes the connection. All SQL uses `?` placeholders.

  **Imports**:
  ```python
  import sqlite3
  import database
  ```

  ---

  **`insert_purchase_with_items(supplier_name, items)`**

  `items` is a list of dicts: `[{"product_id": int, "quantity": float, "unit_price": float, "subtotal": float}, ...]`

  Returns the generated invoice_number string (e.g. `"PUR-000001"`).

  ```python
  def insert_purchase_with_items(supplier_name, items: list) -> str:
      total_amount = sum(item["subtotal"] for item in items)
      conn = database.get_connection()
      try:
          # 1. Insert the header row first (without invoice_number)
          conn.execute(
              """INSERT INTO Purchases (supplier_name, total_amount, status)
                 VALUES (?, ?, 'active')""",
              (supplier_name, total_amount)
          )
          purchase_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

          # 2. Generate invoice number from the assigned id
          invoice_number = f"PUR-{purchase_id:06d}"
          conn.execute(
              "UPDATE Purchases SET invoice_number = ? WHERE id = ?",
              (invoice_number, purchase_id)
          )

          # 3. Insert each line item and update stock + purchase_price
          for item in items:
              conn.execute(
                  """INSERT INTO PurchaseItems
                     (purchase_id, product_id, quantity, unit_price, subtotal)
                     VALUES (?, ?, ?, ?, ?)""",
                  (purchase_id, item["product_id"], item["quantity"],
                   item["unit_price"], item["subtotal"])
              )
              conn.execute(
                  """UPDATE Products
                     SET stock_quantity = stock_quantity + ?,
                         purchase_price = ?
                     WHERE id = ?""",
                  (item["quantity"], item["unit_price"], item["product_id"])
              )

          conn.commit()
          return invoice_number
      except Exception:
          conn.rollback()
          raise
      finally:
          conn.close()
  ```

  ---

  **`get_purchase_by_id(purchase_id)`**

  ```python
  def get_purchase_by_id(purchase_id: int):
      conn = database.get_connection()
      try:
          return conn.execute(
              "SELECT * FROM Purchases WHERE id = ?", (purchase_id,)
          ).fetchone()
      finally:
          conn.close()
  ```

  ---

  **`get_purchase_items(purchase_id)`**

  ```python
  def get_purchase_items(purchase_id: int):
      conn = database.get_connection()
      try:
          return conn.execute(
              """SELECT pi.*, p.name AS product_name
                 FROM PurchaseItems pi
                 JOIN Products p ON pi.product_id = p.id
                 WHERE pi.purchase_id = ?""",
              (purchase_id,)
          ).fetchall()
      finally:
          conn.close()
  ```

  ---

  **`get_all_purchases(start_date=None, end_date=None)`**

  ```python
  def get_all_purchases(start_date=None, end_date=None):
      conn = database.get_connection()
      try:
          if start_date and end_date:
              return conn.execute(
                  """SELECT * FROM Purchases
                     WHERE created_at BETWEEN ? AND ?
                     ORDER BY created_at DESC""",
                  (start_date, end_date)
              ).fetchall()
          else:
              return conn.execute(
                  "SELECT * FROM Purchases ORDER BY created_at DESC"
              ).fetchall()
      finally:
          conn.close()
  ```

  ---

  **`void_purchase(purchase_id)`**

  *(Called only from Phase 5's Invoice Detail Dialog — after
  `purchase_logic.check_void_stock()` passes. Do NOT add any stock validation
  here; that lives in the logic layer.)*

  ```python
  def void_purchase(purchase_id: int) -> None:
      conn = database.get_connection()
      try:
          # Get all line items
          items = conn.execute(
              "SELECT product_id, quantity FROM PurchaseItems WHERE purchase_id = ?",
              (purchase_id,)
          ).fetchall()

          # Reverse stock for each line
          for item in items:
              conn.execute(
                  "UPDATE Products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                  (item["quantity"], item["product_id"])
              )

          # Mark invoice as voided
          conn.execute(
              "UPDATE Purchases SET status = 'voided' WHERE id = ?",
              (purchase_id,)
          )
          conn.commit()
      except Exception:
          conn.rollback()
          raise
      finally:
          conn.close()
  ```

---

## Phase 3: Foundation — `logic/purchase_logic.py` (blocking prerequisite for UI)

**Purpose**: In-memory invoice building, validation rules, save/void orchestration.
No SQL, no PySide6.

**Checkpoint**: `python -c "import logic.purchase_logic; print('OK')"` → prints `OK`.

- [x] T003 Create `accounting_system/logic/purchase_logic.py` with all 6 functions below.

  **Imports**:
  ```python
  import purchases_db
  import products_db
  ```

  ---

  **`validate_line(quantity, unit_price)`**

  ```python
  def validate_line(quantity: float, unit_price: float) -> tuple:
      """Returns (True, '') if valid, (False, error_message) otherwise."""
      if quantity <= 0:
          return False, "Quantity must be greater than 0."
      if unit_price < 0:
          return False, "Unit price cannot be negative."
      return True, ""
  ```

  ---

  **`calculate_subtotal(quantity, unit_price)`**

  ```python
  def calculate_subtotal(quantity: float, unit_price: float) -> float:
      return round(quantity * unit_price, 2)
  ```

  ---

  **`calculate_total(items)`**

  ```python
  def calculate_total(items: list) -> float:
      """items: list of dicts with 'subtotal' key."""
      return round(sum(item["subtotal"] for item in items), 2)
  ```

  ---

  **`get_next_invoice_number()`**

  ```python
  def get_next_invoice_number() -> str:
      """Returns the preview invoice number for display on the form."""
      import database
      conn = database.get_connection()
      try:
          row = conn.execute("SELECT MAX(id) FROM Purchases").fetchone()
          max_id = row[0] if row[0] is not None else 0
          return f"PUR-{max_id + 1:06d}"
      finally:
          conn.close()
  ```

  ---

  **`save_purchase(supplier_name, items)`**

  ```python
  def save_purchase(supplier_name, items: list) -> str:
      """
      Validates, then delegates to purchases_db.
      Returns the generated invoice_number string.
      Raises ValueError for business rule violations.
      Raises Exception for database errors (caller shows QMessageBox).
      """
      if not items:
          raise ValueError("Invoice must have at least one item before saving.")
      return purchases_db.insert_purchase_with_items(supplier_name, items)
  ```

  ---

  **`check_void_stock(purchase_id)`** and **`void_purchase(purchase_id)`**

  ```python
  def check_void_stock(purchase_id: int) -> tuple:
      """
      Returns (True, '') if all lines have sufficient stock to reverse.
      Returns (False, error_message) if any line's stock has already been sold.
      """
      items = purchases_db.get_purchase_items(purchase_id)
      for item in items:
          product = products_db.get_product_by_id(item["product_id"])
          if product is None:
              continue
          if product["stock_quantity"] < item["quantity"]:
              return (
                  False,
                  f"Cannot void: insufficient stock for '{item['product_name']}'. "
                  f"Available: {product['stock_quantity']}, "
                  f"Required: {item['quantity']}. "
                  f"Some of this stock may have already been sold."
              )
      return True, ""


  def void_purchase(purchase_id: int) -> None:
      """
      Checks stock availability, then voids.
      Raises ValueError if stock check fails.
      Raises Exception for database errors.
      """
      ok, msg = check_void_stock(purchase_id)
      if not ok:
          raise ValueError(msg)
      purchases_db.void_purchase(purchase_id)
  ```

---

## Phase 4: User Story 1 — Record a Purchase Invoice (Priority: P1)

**Goal**: The Admin builds a multi-line invoice, saves it, and stock is updated.

**Independent Test** (quickstart.md Checkpoints 1–3, 6–8, 11–16):
Create a purchase invoice with Laptop (qty 5, price 850) and Sugar (qty 12.5, price 2.00).
Verify invoice number is `PUR-000001`, Laptop stock becomes 5.00, Sugar becomes 12.50,
Laptop purchase price updates to 850.00. Then save a second invoice and verify
invoice number increments to `PUR-000002`.

- [x] T004 [US1] Create `accounting_system/ui/purchases_page.py` — completely replaces
  the placeholder. Implements the full Purchases page.

  **Full implementation**:

  ```python
  import traceback

  from PySide6.QtWidgets import (
      QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
      QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
      QPushButton, QTableWidget, QTableWidgetItem,
      QHeaderView, QMessageBox, QApplication
  )
  from PySide6.QtCore import Qt

  import products_db
  from logic import purchase_logic


  class PurchasesPage(QWidget):
      def __init__(self, parent=None):
          super().__init__(parent)
          self._items = []   # in-memory line items list
          self._build_ui()
          self._refresh_invoice_number()

      def _build_ui(self):
          layout = QVBoxLayout(self)

          # ── Invoice Header ──────────────────────────────────────────
          header_form = QFormLayout()

          self.invoice_number_label = QLabel("PUR-000001")
          header_form.addRow("Invoice #:", self.invoice_number_label)

          from PySide6.QtCore import QDate
          self.date_label = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
          header_form.addRow("Date:", self.date_label)

          self.supplier_input = QLineEdit()
          self.supplier_input.setPlaceholderText("Optional supplier name")
          header_form.addRow("Supplier:", self.supplier_input)

          layout.addLayout(header_form)

          # ── Product Selection Row ───────────────────────────────────
          pick_row = QHBoxLayout()

          self.product_combo = QComboBox()
          self.product_combo.setMinimumWidth(220)
          self.product_combo.setEditable(False)

          self.qty_spin = QDoubleSpinBox()
          self.qty_spin.setRange(0.01, 999_999)
          self.qty_spin.setDecimals(2)
          self.qty_spin.setValue(1.0)

          self.price_spin = QDoubleSpinBox()
          self.price_spin.setRange(0, 9_999_999)
          self.price_spin.setDecimals(2)
          self.price_spin.setValue(0.0)

          self.add_line_btn = QPushButton("Add to Invoice")

          pick_row.addWidget(QLabel("Product:"))
          pick_row.addWidget(self.product_combo, 2)
          pick_row.addWidget(QLabel("Qty:"))
          pick_row.addWidget(self.qty_spin)
          pick_row.addWidget(QLabel("Unit Price:"))
          pick_row.addWidget(self.price_spin)
          pick_row.addWidget(self.add_line_btn)
          layout.addLayout(pick_row)

          # ── Line Items Table ────────────────────────────────────────
          self.table = QTableWidget()
          self.table.setColumnCount(5)
          self.table.setHorizontalHeaderLabels(
              ["Product", "Qty", "Unit Price", "Subtotal", ""])
          self.table.horizontalHeader().setSectionResizeMode(
              0, QHeaderView.Stretch)
          self.table.setEditTriggers(QTableWidget.NoEditTriggers)
          self.table.setSelectionBehavior(QTableWidget.SelectRows)
          layout.addWidget(self.table)

          # ── Footer ─────────────────────────────────────────────────
          footer = QHBoxLayout()
          self.total_label = QLabel("Total: 0.00")
          font = self.total_label.font()
          font.setBold(True)
          self.total_label.setFont(font)

          self.clear_btn  = QPushButton("Clear Invoice")
          self.save_btn   = QPushButton("Save Invoice")

          footer.addWidget(self.total_label)
          footer.addStretch()
          footer.addWidget(self.clear_btn)
          footer.addWidget(self.save_btn)
          layout.addLayout(footer)

          # ── Signals ────────────────────────────────────────────────
          self.product_combo.currentIndexChanged.connect(
              self._on_product_selected)
          self.add_line_btn.clicked.connect(self._on_add_line)
          self.clear_btn.clicked.connect(self._on_clear)
          self.save_btn.clicked.connect(self._on_save)

      # ── Helpers ────────────────────────────────────────────────────

      def _refresh_invoice_number(self):
          try:
              num = purchase_logic.get_next_invoice_number()
              self.invoice_number_label.setText(num)
          except Exception:
              self.invoice_number_label.setText("PUR-??????")

      def _reload_products(self):
          """Populate the product combo box with active products."""
          self.product_combo.blockSignals(True)
          self.product_combo.clear()
          try:
              rows = products_db.get_active_products()
              for row in rows:
                  # Store product_id and name as item data
                  self.product_combo.addItem(
                      f"{row['name']} ({row['unit']})",
                      userData={"id": row["id"], "name": row["name"],
                                "unit": row["unit"]}
                  )
          except Exception:
              print(traceback.format_exc())
          self.product_combo.blockSignals(False)

      def _update_total_label(self):
          total = purchase_logic.calculate_total(self._items)
          self.total_label.setText(f"Total: {total:,.2f}")

      def _rebuild_table(self):
          """Redraw the line-items table from self._items."""
          self.table.setRowCount(0)
          for idx, item in enumerate(self._items):
              r = self.table.rowCount()
              self.table.insertRow(r)
              self.table.setItem(r, 0, QTableWidgetItem(item["product_name"]))
              self.table.setItem(r, 1, QTableWidgetItem(f"{item['quantity']:.2f}"))
              self.table.setItem(r, 2, QTableWidgetItem(f"{item['unit_price']:.2f}"))
              self.table.setItem(r, 3, QTableWidgetItem(f"{item['subtotal']:.2f}"))

              remove_btn = QPushButton("Remove")
              # Capture idx by default argument to avoid closure-over-loop bug
              remove_btn.clicked.connect(
                  lambda checked=False, i=idx: self._on_remove_line(i))
              self.table.setCellWidget(r, 4, remove_btn)

      def _reset_form(self):
          """Reset the entire form to its initial empty state."""
          self._items = []
          self.supplier_input.clear()
          self.qty_spin.setValue(1.0)
          self.price_spin.setValue(0.0)
          self._rebuild_table()
          self._update_total_label()
          self._refresh_invoice_number()

      # ── Signal Handlers ────────────────────────────────────────────

      def _on_product_selected(self, index):
          """Auto-focus the Quantity field when a product is selected."""
          if index >= 0:
              self.qty_spin.setFocus()
              self.qty_spin.selectAll()

      def _on_add_line(self):
          idx = self.product_combo.currentIndex()
          if idx < 0:
              QMessageBox.warning(self, "No Product",
                                  "Please select a product first.")
              return

          product_data = self.product_combo.itemData(idx)
          quantity   = self.qty_spin.value()
          unit_price = self.price_spin.value()

          ok, msg = purchase_logic.validate_line(quantity, unit_price)
          if not ok:
              QMessageBox.warning(self, "Validation Error", msg)
              return

          subtotal = purchase_logic.calculate_subtotal(quantity, unit_price)
          self._items.append({
              "product_id":   product_data["id"],
              "product_name": product_data["name"],
              "quantity":     quantity,
              "unit_price":   unit_price,
              "subtotal":     subtotal,
          })
          self._rebuild_table()
          self._update_total_label()

          # Reset spinboxes and return focus to product picker
          self.qty_spin.setValue(1.0)
          self.price_spin.setValue(0.0)
          self.product_combo.setFocus()

      def _on_remove_line(self, index: int):
          if 0 <= index < len(self._items):
              self._items.pop(index)
              self._rebuild_table()
              self._update_total_label()

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

          supplier = self.supplier_input.text().strip() or None

          QApplication.setOverrideCursor(Qt.WaitCursor)
          try:
              invoice_number = purchase_logic.save_purchase(supplier, self._items)
              QApplication.restoreOverrideCursor()
              QMessageBox.information(
                  self, "Saved",
                  f"Purchase invoice {invoice_number} saved successfully.")
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
          """Reload the product picker each time this page becomes visible."""
          super().showEvent(event)
          self._reload_products()
  ```

  **After creating this file**, verify the placeholder is gone and the import works:
  ```
  python -c "from ui.purchases_page import PurchasesPage; print('OK')"
  ```

**Checkpoint (US1)**: Run `python main.py`, navigate to Purchases, add two products,
save — verify quickstart.md Checkpoints 1–3, 6–8, 11–16 pass.

---

## Phase 5: User Story 2 — Active-Product Picker with Auto-Focus (Priority: P1)

**Goal**: Only active products appear in the picker; keyboard focus flows
automatically from product → quantity → (add) → product picker.

*US2 is already implemented in T004 via:*
- `_reload_products()` calls `products_db.get_active_products()` (active only)
- `showEvent` reloads the picker each time the page is shown
- `_on_product_selected` moves focus to `qty_spin`
- `_on_add_line` returns focus to `product_combo` after adding

- [ ] T005 [US2] Verify US2 by running quickstart.md Checkpoints 4–5, 9–10, 17:
  - Deactivate "Mouse" in Products → open Purchases → "Mouse" not in picker.
  - Select a product → confirm focus jumps to Qty field automatically.
  - Click Add → confirm focus returns to product picker automatically.
  - If any of these fail, fix the relevant method in `ui/purchases_page.py`.

**Checkpoint (US2)**: Quickstart Checkpoints 4–5, 9–10, 17 pass.

---

## Phase 6: User Story 3 — Invoice Number Auto-Generation (Priority: P1)

**Goal**: Invoice numbers are auto-generated as `PUR-XXXXXX`, sequential, read-only.

*US3 is already implemented in T002 (`insert_purchase_with_items` uses `lastrowid`)
and T003 (`get_next_invoice_number()` previews the next number) and T004
(`_refresh_invoice_number()` populates the label, which is a `QLabel` not a
`QLineEdit` — so it is inherently read-only).*

- [ ] T006 [US3] Verify US3 by running quickstart.md Checkpoints 1, 14–16:
  - Page shows `PUR-000001` on first open (or the correct next number).
  - After saving, form resets and shows the next number.
  - Third invoice gets `PUR-000003`.
  - The number field is NOT editable (it's a QLabel).
  If any fail, check `get_next_invoice_number()` in `logic/purchase_logic.py` and
  `_refresh_invoice_number()` in `ui/purchases_page.py`.

**Checkpoint (US3)**: Quickstart Checkpoints 1, 14–16 pass.

---

## Phase 7: User Story 4 — View Purchases History (Priority: P2)

**Goal**: `get_all_purchases()` and `get_purchase_items()` return correct data for
the Phase 5 Reports page. No Phase 3 UI needed.

*US4 is already implemented in T002 via `get_all_purchases()` and `get_purchase_items()`.*

- [ ] T007 [US4] Verify US4 data functions by running this quick smoke test from
  `accounting_system/`:

  ```python
  # Run: python -c "..."  (after saving at least one purchase via the UI)
  import purchases_db
  rows = purchases_db.get_all_purchases()
  print(f"Total purchases: {len(rows)}")
  for r in rows:
      print(r["invoice_number"], r["total_amount"], r["status"])
      items = purchases_db.get_purchase_items(r["id"])
      for item in items:
          print("  →", item["product_name"], item["quantity"], item["unit_price"])
  ```

  Expected: Each invoice and its line items print correctly.
  If any fail, check the SQL in `purchases_db.get_all_purchases()` and
  `purchases_db.get_purchase_items()`.

**Checkpoint (US4)**: Data functions return correct data after saving invoices through the UI.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [x] T008 [P] Verify layering compliance for Phase 3 files:
  - `purchases_db.py` MUST NOT import PySide6 and MUST NOT contain any calculation
    logic (validate_line, total calculation, etc.) — only SQL.
  - `logic/purchase_logic.py` MUST NOT import PySide6 and MUST NOT contain any raw
    SQL (no `conn.execute(...)` calls).
  - `ui/purchases_page.py` MUST NOT import `sqlite3` directly. The only DB-layer
    import allowed is `products_db` (for `get_active_products()`) — all other DB work
    goes through `logic.purchase_logic`.
  Fix any violation before marking complete.

- [x] T009 [P] Verify error handling compliance:
  - `ui/purchases_page.py._on_save`: `ValueError` caught and shown as warning;
    unexpected `Exception` caught with traceback logged, generic message shown,
    and the in-progress invoice is preserved (form NOT reset on error).
  - `ui/purchases_page.py._on_add_line`: validation result from
    `purchase_logic.validate_line()` shown as warning if not ok; no line added.
  - `ui/purchases_page.py._reload_products`: exception caught and logged; picker
    may be empty but the app does not crash.
  Fix any missing handler before marking complete.

- [x] T010 [P] Verify wait cursor behavior:
  - `ui/purchases_page.py._on_save`: `QApplication.setOverrideCursor(Qt.WaitCursor)`
    called before the save; `QApplication.restoreOverrideCursor()` called in BOTH
    the success path AND the exception path.
  Fix if either path is missing the restore call.

- [x] T011 [P] Verify in-progress invoice retention on navigation (FR-026):
  - Run quickstart.md Checkpoint 18: add a line, navigate away, navigate back →
    line and supplier name still present.
  - If the form resets on navigation, find any `showEvent` override that calls
    `_reset_form()` and remove that call (only `_reload_products()` should be in
    `showEvent`, not `_reset_form()`).

- [ ] T012 Run the full Phase 3 manual testing checklist from `quickstart.md`
  (Checkpoints 1–20) in a single continuous session. This includes the Phase 1 and
  Phase 2 regression checks (Checkpoints 19–20). Mark each checkpoint as passed.
  Do NOT mark T012 complete until every checkpoint passes. Any failure is a bug —
  fix and re-run.

---

## Dependencies & Execution Order

### Strict Build Order

```
T001 (verify logic/__init__.py)
  → T002 (purchases_db.py)
      → T003 (logic/purchase_logic.py)
          → T004 (ui/purchases_page.py)
              → T005, T006, T007  (verification — can run in parallel)
                  → T008, T009, T010, T011  (compliance checks — can run in parallel)
                      → T012  (full regression — must be last)
```

### Parallel Opportunities

```
# After T004 is complete, these verification tasks can run in parallel:
T005  T006  T007

# After T005+T006+T007, these compliance tasks can run in parallel:
T008  T009  T010  T011

# T012 must be last — it is the full regression gate
T012
```

---

## Implementation Notes for the Implementer

1. **`_items` list**: The in-progress invoice is stored as `self._items` — a plain
   Python list of dicts on the `PurchasesPage` instance. Because PySide6's
   `QStackedWidget` keeps page widgets alive when switching pages, this list persists
   naturally across page switches. No special persistence code is needed (FR-026).

2. **`QLabel` for invoice number**: The invoice number is displayed as a `QLabel`,
   not a `QLineEdit`. This makes it inherently read-only — the user cannot click and
   type in it. Do not change it to a `QLineEdit` even with `setReadOnly(True)`.

3. **`QComboBox` with `userData`**: Each combo box item stores the product dict
   `{"id": ..., "name": ..., "unit": ...}` as its `userData`. Retrieve it with
   `self.product_combo.itemData(idx)`. This avoids a second DB call when the Admin
   selects a product.

4. **Remove button closure bug**: When creating Remove buttons in a loop, use a
   default argument to capture the current index: `lambda checked=False, i=idx: ...`
   Without this, all Remove buttons would remove the last item (classic Python
   closure-over-loop bug).

5. **`showEvent` only reloads the picker**: The `showEvent` override calls
   `self._reload_products()` only — it does NOT call `_reset_form()`. This preserves
   the in-progress invoice (FR-026) while still updating the product list (so that
   newly activated/deactivated products are reflected when returning to the page).

6. **`blockSignals` during picker reload**: `_reload_products()` wraps the combo
   population in `blockSignals(True/False)` to prevent `_on_product_selected` from
   firing (and moving focus to the Qty field) during the reload.

7. **`save_purchase` vs. DB errors**: `purchase_logic.save_purchase()` raises
   `ValueError` for business rule violations (empty invoice) and re-raises any
   `Exception` from `purchases_db` for DB errors. The UI distinguishes these:
   `ValueError` → `QMessageBox.warning`; `Exception` → `QMessageBox.critical`.
   In both cases the in-progress invoice is NOT reset.

8. **`void_purchase()` implemented but not wired to UI**: Both
   `purchases_db.void_purchase()` and `logic/purchase_logic.void_purchase()` are
   fully implemented in Phase 3 but called only from Phase 5's
   `ui/invoice_detail_dialog.py`. Do not add a Void button to the Purchases page.

9. **`get_next_invoice_number()` uses `MAX(id)`**: The preview number on the form
   is `MAX(id) + 1`. After a void (Phase 5), voided invoice IDs are not reused —
   the next purchase still uses `MAX(id) + 1`, so the sequence has no gaps from a
   user perspective (IDs always increment).

10. **`price_spin` defaults to 0.0**: A unit price of 0 is allowed (FR-007). The
    spin box minimum is 0, not 0.01. Only quantity has a minimum > 0 (0.01 via
    `setRange(0.01, 999_999)`).
