---
description: "Task list for Phase 2 — Product Catalog Management"
---

# Tasks: Product Catalog Management

**Input**: Design documents from `specs/002-products/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | data-model.md ✅ | research.md ✅ | quickstart.md ✅

**Tests**: Not requested — no test tasks generated.

**Organization**: Strictly bottom-up per plan.md. Inline implementation guidance is
provided so a smaller LLM model can complete each task without reading extra documents.

**Project root**: `accounting_system/` (all file paths below are relative to it)

**Phase 1 files already exist**: `config.py`, `database.py`, `auth_db.py`, `auth.py`,
`main.py`, `ui/__init__.py`, `ui/login_window.py`, `ui/main_window.py`,
`ui/change_password_dialog.py`, and five placeholder pages. Do NOT modify any Phase 1
file unless a task explicitly says to.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (touches different files, no cross-task dependency)
- **[Story]**: Which user story this task belongs to (US1–US4 from spec.md)
- Every task includes the exact target file path

---

## Phase 1: Setup

**Purpose**: No new directories needed. Phase 1 already created all folders.
Only one file is needed in this phase.

- [x] T001 Create `products_db.py` in `accounting_system/` with the full data access
  layer for the Products table. Implement all 8 functions listed below. Every function
  opens its own connection via `database.get_connection()`, performs its operation,
  and closes the connection. All SQL uses `?` placeholders — never string formatting.

  **Imports**:
  ```python
  import sqlite3
  import database
  ```

  **`insert_product(name, sku, unit, purchase_price, selling_price, stock_quantity, reorder_level)`**:
  ```python
  def insert_product(name: str, sku, unit: str, purchase_price: float,
                     selling_price: float, stock_quantity: float,
                     reorder_level: float) -> None:
      conn = database.get_connection()
      try:
          conn.execute(
              """INSERT INTO Products
                 (name, sku, unit, purchase_price, selling_price,
                  stock_quantity, reorder_level)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (name, sku, unit, purchase_price, selling_price,
               stock_quantity, reorder_level)
          )
          conn.commit()
      finally:
          conn.close()
  ```
  *(Raises `sqlite3.IntegrityError` if sku is non-null and duplicates an existing one.
  Caller catches this.)*

  **`update_product(product_id, name, sku, unit, purchase_price, selling_price, stock_quantity, reorder_level)`**:
  ```python
  def update_product(product_id: int, name: str, sku, unit: str,
                     purchase_price: float, selling_price: float,
                     stock_quantity: float, reorder_level: float) -> None:
      conn = database.get_connection()
      try:
          conn.execute(
              """UPDATE Products SET name=?, sku=?, unit=?, purchase_price=?,
                 selling_price=?, stock_quantity=?, reorder_level=?
                 WHERE id=?""",
              (name, sku, unit, purchase_price, selling_price,
               stock_quantity, reorder_level, product_id)
          )
          conn.commit()
      finally:
          conn.close()
  ```

  **`delete_product(product_id)`**:
  ```python
  def delete_product(product_id: int) -> None:
      conn = database.get_connection()
      try:
          conn.execute("DELETE FROM Products WHERE id = ?", (product_id,))
          conn.commit()
      finally:
          conn.close()
  ```

  **`set_active(product_id, is_active)`**:
  ```python
  def set_active(product_id: int, is_active: int) -> None:
      conn = database.get_connection()
      try:
          conn.execute(
              "UPDATE Products SET is_active = ? WHERE id = ?",
              (is_active, product_id)
          )
          conn.commit()
      finally:
          conn.close()
  ```

  **`search_products(search_text, include_inactive)`**:
  ```python
  def search_products(search_text: str, include_inactive: bool):
      conn = database.get_connection()
      try:
          pattern = f"%{search_text}%"
          if include_inactive:
              rows = conn.execute(
                  """SELECT * FROM Products
                     WHERE (name LIKE ? OR sku LIKE ?)
                     ORDER BY name""",
                  (pattern, pattern)
              ).fetchall()
          else:
              rows = conn.execute(
                  """SELECT * FROM Products
                     WHERE (name LIKE ? OR sku LIKE ?) AND is_active = 1
                     ORDER BY name""",
                  (pattern, pattern)
              ).fetchall()
          return rows
      finally:
          conn.close()
  ```

  **`get_active_products()`** *(THE single shared picker function — used by Sales and
  Purchases pages in later phases; never add a per-screen alternative)*:
  ```python
  def get_active_products():
      conn = database.get_connection()
      try:
          return conn.execute(
              """SELECT id, name, unit, selling_price, stock_quantity
                 FROM Products WHERE is_active = 1 ORDER BY name"""
          ).fetchall()
      finally:
          conn.close()
  ```

  **`get_low_stock_products()`** *(used by Dashboard in Phase 5; implement now)*:
  ```python
  def get_low_stock_products():
      conn = database.get_connection()
      try:
          return conn.execute(
              """SELECT id, name, stock_quantity, reorder_level
                 FROM Products
                 WHERE is_active = 1 AND stock_quantity <= reorder_level
                 ORDER BY name"""
          ).fetchall()
      finally:
          conn.close()
  ```

  **`is_product_referenced(product_id)`**:
  ```python
  def is_product_referenced(product_id: int) -> bool:
      conn = database.get_connection()
      try:
          row = conn.execute(
              """SELECT 1 FROM SaleItems WHERE product_id = ?
                 UNION
                 SELECT 1 FROM PurchaseItems WHERE product_id = ?
                 LIMIT 1""",
              (product_id, product_id)
          ).fetchone()
          return row is not None
      finally:
          conn.close()
  ```

  **`get_product_by_id(product_id)`**:
  ```python
  def get_product_by_id(product_id: int):
      conn = database.get_connection()
      try:
          return conn.execute(
              "SELECT * FROM Products WHERE id = ?", (product_id,)
          ).fetchone()
      finally:
          conn.close()
  ```

**Checkpoint (T001)**: Run `python -c "import products_db; print('OK')"` from
`accounting_system/` — must print `OK` with no errors.

---

## Phase 2: Foundation (Blocking Prerequisite)

T001 is the only foundation for this phase. Once it passes the import check above,
proceed to the user story phases.

---

## Phase 3: User Story 1 — Add a New Product (Priority: P1)

**Goal**: The Admin opens Add Product dialog, fills fields, saves — product appears
in the table immediately.

**Independent Test** (quickstart.md Checkpoints 1–7):
Add products with full fields, minimal fields, decimal quantities. Confirm duplicate
SKU is rejected. Confirm validation blocks empty name and negative price. Confirm the
selling-price-below-purchase-price warning appears and both Yes/No paths work.

- [x] T002 [US1] Create `ui/product_dialog.py` — the Add/Edit modal dialog. This one
  file handles both Add (called with `product_id=None`) and Edit (called with an
  integer `product_id`).

  **Full implementation**:
  ```python
  import sqlite3
  import traceback

  from PySide6.QtWidgets import (
      QDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
      QLineEdit, QDoubleSpinBox, QPushButton, QMessageBox
  )
  from PySide6.QtCore import Qt

  import products_db


  class ProductDialog(QDialog):
      def __init__(self, product_id=None, parent=None):
          super().__init__(parent)
          self.product_id = product_id
          self.setWindowTitle("Edit Product" if product_id else "Add Product")
          self.setFixedWidth(420)
          self._build_ui()
          if product_id:
              self._prefill(product_id)

      def _build_ui(self):
          # Text fields
          self.name_input = QLineEdit()
          self.sku_input  = QLineEdit()
          self.unit_input = QLineEdit()
          self.unit_input.setPlaceholderText("pcs")

          # Numeric spinboxes (decimals, range 0–9,999,999)
          def spinbox():
              sb = QDoubleSpinBox()
              sb.setRange(0, 9_999_999)
              sb.setDecimals(2)
              return sb

          self.purchase_price_input  = spinbox()
          self.selling_price_input   = spinbox()
          self.stock_quantity_input  = spinbox()
          self.reorder_level_input   = spinbox()
          self.reorder_level_input.setValue(5)  # default

          form = QFormLayout()
          form.addRow("Name *:",           self.name_input)
          form.addRow("SKU (optional):",   self.sku_input)
          form.addRow("Unit:",             self.unit_input)
          form.addRow("Purchase Price:",   self.purchase_price_input)
          form.addRow("Selling Price:",    self.selling_price_input)
          form.addRow("Stock Quantity:",   self.stock_quantity_input)
          form.addRow("Reorder Level:",    self.reorder_level_input)

          self.save_btn   = QPushButton("Save")
          self.cancel_btn = QPushButton("Cancel")
          btn_row = QHBoxLayout()
          btn_row.addStretch()
          btn_row.addWidget(self.cancel_btn)
          btn_row.addWidget(self.save_btn)

          outer = QVBoxLayout(self)
          outer.addLayout(form)
          outer.addLayout(btn_row)

          self.save_btn.clicked.connect(self._on_save)
          self.cancel_btn.clicked.connect(self.reject)

      def _prefill(self, product_id: int):
          row = products_db.get_product_by_id(product_id)
          if row is None:
              return
          self.name_input.setText(row["name"] or "")
          self.sku_input.setText(row["sku"] or "")
          self.unit_input.setText(row["unit"] or "")
          self.purchase_price_input.setValue(row["purchase_price"] or 0)
          self.selling_price_input.setValue(row["selling_price"] or 0)
          self.stock_quantity_input.setValue(row["stock_quantity"] or 0)
          self.reorder_level_input.setValue(row["reorder_level"] or 0)

      def _on_save(self):
          # --- Validation ---
          name = self.name_input.text().strip()
          if not name:
              QMessageBox.warning(self, "Validation Error", "Product name is required.")
              return
          if len(name) > 100:
              QMessageBox.warning(self, "Validation Error",
                                  "Product name must be 100 characters or fewer.")
              return

          sku  = self.sku_input.text().strip() or None   # blank → None
          unit = self.unit_input.text().strip() or "pcs"

          purchase_price  = self.purchase_price_input.value()
          selling_price   = self.selling_price_input.value()
          stock_quantity  = self.stock_quantity_input.value()
          reorder_level   = self.reorder_level_input.value()

          if purchase_price < 0:
              QMessageBox.warning(self, "Validation Error",
                                  "Purchase price must be 0 or greater.")
              return
          if selling_price < 0:
              QMessageBox.warning(self, "Validation Error",
                                  "Selling price must be 0 or greater.")
              return
          if stock_quantity < 0:
              QMessageBox.warning(self, "Validation Error",
                                  "Stock quantity must be 0 or greater.")
              return
          if reorder_level < 0:
              QMessageBox.warning(self, "Validation Error",
                                  "Reorder level must be 0 or greater.")
              return

          # Selling price below purchase price warning
          if selling_price < purchase_price:
              answer = QMessageBox.question(
                  self, "Price Warning",
                  "Selling price is less than purchase price. Save anyway?",
                  QMessageBox.Yes | QMessageBox.No,
                  QMessageBox.No
              )
              if answer != QMessageBox.Yes:
                  return

          # --- Save ---
          try:
              if self.product_id is None:
                  products_db.insert_product(
                      name, sku, unit, purchase_price, selling_price,
                      stock_quantity, reorder_level
                  )
              else:
                  products_db.update_product(
                      self.product_id, name, sku, unit, purchase_price,
                      selling_price, stock_quantity, reorder_level
                  )
              self.accept()
          except sqlite3.IntegrityError:
              QMessageBox.warning(self, "Duplicate SKU",
                  "SKU already in use. Please enter a unique SKU or leave it blank.")
          except Exception:
              print(traceback.format_exc())
              QMessageBox.critical(self, "Unexpected Error",
                  "An unexpected error occurred. Please try again.")
  ```

- [x] T003 [US1] Create `ui/products_page.py` — completely replaces the placeholder.
  This file implements the full Products page with table, search, Show Inactive
  checkbox, and Add/Edit/Delete/Deactivate/Activate row actions.

  **Full implementation**:
  ```python
  import traceback

  from PySide6.QtWidgets import (
      QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
      QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
      QMessageBox, QApplication
  )
  from PySide6.QtCore import Qt

  import products_db
  from ui.product_dialog import ProductDialog


  class ProductsPage(QWidget):
      def __init__(self, parent=None):
          super().__init__(parent)
          self._build_ui()
          self._load_products()

      def _build_ui(self):
          layout = QVBoxLayout(self)

          # Top bar: search + show inactive + add button
          top = QHBoxLayout()
          self.search_input = QLineEdit()
          self.search_input.setPlaceholderText("Search by name or SKU…")
          self.show_inactive_cb = QCheckBox("Show Inactive")
          self.add_btn = QPushButton("Add Product")

          top.addWidget(self.search_input, 1)
          top.addWidget(self.show_inactive_cb)
          top.addWidget(self.add_btn)
          layout.addLayout(top)

          # Table
          self.table = QTableWidget()
          self.table.setColumnCount(10)
          self.table.setHorizontalHeaderLabels([
              "ID", "Name", "SKU", "Unit",
              "Purchase Price", "Selling Price",
              "Stock Qty", "Reorder Level", "Status",
              "Actions"
          ])
          self.table.horizontalHeader().setSectionResizeMode(
              1, QHeaderView.Stretch  # Name column stretches
          )
          self.table.setColumnHidden(0, True)   # hide internal ID column
          self.table.setEditTriggers(QTableWidget.NoEditTriggers)
          self.table.setSelectionBehavior(QTableWidget.SelectRows)
          layout.addWidget(self.table)

          # Signals
          self.search_input.textChanged.connect(self._load_products)
          self.show_inactive_cb.stateChanged.connect(self._load_products)
          self.add_btn.clicked.connect(self._on_add)

      def _load_products(self):
          """Reload the table from the database using current search/filter state."""
          search_text    = self.search_input.text().strip()
          include_inactive = self.show_inactive_cb.isChecked()
          try:
              rows = products_db.search_products(search_text, include_inactive)
          except Exception:
              print(traceback.format_exc())
              QMessageBox.critical(self, "Error", "Failed to load products.")
              return

          self.table.setRowCount(0)
          for row in rows:
              r = self.table.rowCount()
              self.table.insertRow(r)

              self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
              self.table.setItem(r, 1, QTableWidgetItem(row["name"] or ""))
              self.table.setItem(r, 2, QTableWidgetItem(row["sku"] or ""))
              self.table.setItem(r, 3, QTableWidgetItem(row["unit"] or ""))
              self.table.setItem(r, 4, QTableWidgetItem(
                  f"{row['purchase_price']:.2f}"))
              self.table.setItem(r, 5, QTableWidgetItem(
                  f"{row['selling_price']:.2f}"))
              self.table.setItem(r, 6, QTableWidgetItem(
                  f"{row['stock_quantity']:.2f}"))
              self.table.setItem(r, 7, QTableWidgetItem(
                  f"{row['reorder_level']:.2f}"))
              status = "Active" if row["is_active"] else "Inactive"
              self.table.setItem(r, 8, QTableWidgetItem(status))

              # Action buttons cell
              self._add_action_buttons(r, row["id"], bool(row["is_active"]))

          if self.table.rowCount() == 0:
              self.table.setRowCount(1)
              no_results = QTableWidgetItem("No products found.")
              no_results.setTextAlignment(Qt.AlignCenter)
              self.table.setSpan(0, 1, 1, 8)
              self.table.setItem(0, 1, no_results)

      def _add_action_buttons(self, row_index: int, product_id: int, is_active: bool):
          """Add Edit + (Delete or Deactivate/Activate) buttons to a table row."""
          cell_widget = QWidget()
          btn_layout  = QHBoxLayout(cell_widget)
          btn_layout.setContentsMargins(2, 2, 2, 2)
          btn_layout.setSpacing(4)

          edit_btn = QPushButton("Edit")
          edit_btn.setFixedWidth(50)
          edit_btn.clicked.connect(lambda: self._on_edit(product_id))
          btn_layout.addWidget(edit_btn)

          if products_db.is_product_referenced(product_id):
              # Has invoice history — show Deactivate or Activate
              if is_active:
                  action_btn = QPushButton("Deactivate")
                  action_btn.clicked.connect(
                      lambda: self._on_deactivate(product_id))
              else:
                  action_btn = QPushButton("Activate")
                  action_btn.clicked.connect(
                      lambda: self._on_activate(product_id))
          else:
              # Never used in any invoice — show Delete
              action_btn = QPushButton("Delete")
              action_btn.clicked.connect(lambda: self._on_delete(product_id))

          btn_layout.addWidget(action_btn)
          self.table.setCellWidget(row_index, 9, cell_widget)

      # --- Action handlers ---

      def _on_add(self):
          dlg = ProductDialog(parent=self)
          if dlg.exec() == ProductDialog.Accepted:
              self._load_products()

      def _on_edit(self, product_id: int):
          dlg = ProductDialog(product_id=product_id, parent=self)
          if dlg.exec() == ProductDialog.Accepted:
              self._load_products()

      def _on_delete(self, product_id: int):
          answer = QMessageBox.question(
              self, "Confirm Delete",
              "Are you sure you want to permanently delete this product?\n"
              "This action cannot be undone.",
              QMessageBox.Yes | QMessageBox.No,
              QMessageBox.No
          )
          if answer != QMessageBox.Yes:
              return
          try:
              products_db.delete_product(product_id)
              self._load_products()
          except Exception:
              print(traceback.format_exc())
              QMessageBox.critical(self, "Error",
                  "An unexpected error occurred while deleting the product.")

      def _on_deactivate(self, product_id: int):
          answer = QMessageBox.question(
              self, "Confirm Deactivate",
              "Deactivate this product? It will be hidden from pickers and "
              "the default product list. You can reactivate it at any time.",
              QMessageBox.Yes | QMessageBox.No,
              QMessageBox.No
          )
          if answer != QMessageBox.Yes:
              return
          try:
              products_db.set_active(product_id, 0)
              self._load_products()
          except Exception:
              print(traceback.format_exc())
              QMessageBox.critical(self, "Error",
                  "An unexpected error occurred while deactivating the product.")

      def _on_activate(self, product_id: int):
          try:
              products_db.set_active(product_id, 1)
              self._load_products()
          except Exception:
              print(traceback.format_exc())
              QMessageBox.critical(self, "Error",
                  "An unexpected error occurred while activating the product.")

      def showEvent(self, event):
          """Refresh the table each time this page becomes visible."""
          super().showEvent(event)
          self._load_products()
  ```

  **After creating this file**, update `ui/main_window.py` to import the real
  `ProductsPage` instead of the placeholder. In `main_window.py`, the import line
  at the top currently reads:
  ```python
  from ui.products_page import ProductsPage
  ```
  This import already uses the correct class name — the new file uses the same class
  name `ProductsPage`, so no change to `main_window.py` is needed. The placeholder
  is simply replaced by the new file at the same path.

**Checkpoint (US1)**: Run `python main.py`, navigate to Products, click Add Product,
add at least two products. Verify quickstart.md Checkpoints 1–7 all pass.

---

## Phase 4: User Story 2 — Edit an Existing Product (Priority: P1)

**Goal**: Click Edit on a product row → pre-filled dialog opens → save updates the
table immediately.

**Independent Test** (quickstart.md Checkpoints 8–9):
Click Edit on a product, change the selling price, save → updated value in table.
Click Edit, change a value, click Cancel → original values unchanged.

*T002 and T003 already implement US2 — `ProductDialog` with a non-None `product_id`
pre-fills via `_prefill()`, and `_on_edit` in `ProductsPage` triggers it.*

- [ ] T004 [US2] Verify Edit functionality by running quickstart.md Checkpoints 8 and
  9 manually. Confirm:
  - Edit button on any product row opens the dialog with all fields pre-filled.
  - Changing selling price and saving: table shows new value immediately.
  - Opening Edit, changing a value, clicking Cancel: original values unchanged.
  - If any of these fail, fix the relevant code in `ui/product_dialog.py` (the
    `_prefill` method) or `ui/products_page.py` (the `_on_edit` method).

**Checkpoint (US2)**: Quickstart Checkpoints 8–9 pass.

---

## Phase 5: User Story 3 — Delete or Deactivate a Product (Priority: P1)

**Goal**: Products never used in invoices can be permanently deleted (with
confirmation). Products with invoice history show Deactivate instead. Deactivated
products can be reactivated.

**Independent Test** (quickstart.md Checkpoints 10–11, 15):
Delete an unused product → gone from table. Cancel delete → product remains.
Show Inactive toggle → button mechanic works. (Deactivate/Activate with real invoice
data is verified in Phase 3 of the overall project — the first Purchases invoice.)

*T003 already implements US3 via `_on_delete`, `_on_deactivate`, `_on_activate`,
and the `is_product_referenced()` check in `_add_action_buttons`.*

- [ ] T005 [US3] Verify Delete/Deactivate/Activate functionality by running
  quickstart.md Checkpoints 10, 11, and 15 manually. Confirm:
  - Clicking Delete on an unused product shows a confirmation dialog.
  - Confirming deletion removes the product from the table permanently.
  - Cancelling deletion leaves the product unchanged.
  - The "Show Inactive" checkbox causes the table to reload including/excluding
    inactive products.
  - If any of these fail, fix the relevant code in `ui/products_page.py`
    (`_on_delete`, `_on_deactivate`, `_on_activate`, `_add_action_buttons`).

**Checkpoint (US3)**: Quickstart Checkpoints 10, 11, 15 pass.

---

## Phase 6: User Story 4 — Search the Product Catalog (Priority: P2)

**Goal**: Typing in the search box filters by name or SKU in real time; clearing
restores the full list; inactive products are excluded unless "Show Inactive" is
checked.

**Independent Test** (quickstart.md Checkpoints 12–14):
Add several products. Type a partial name → only matching products visible.
Type a partial SKU → matching products visible. Clear search → full list restores.

*T003 already implements US4 — `search_input.textChanged` connects to `_load_products`,
which calls `products_db.search_products(search_text, include_inactive)`.*

- [ ] T006 [US4] Verify search functionality by running quickstart.md Checkpoints
  12–14 manually. Confirm:
  - Typing "lap" (with "Laptop" in the catalog) shows only Laptop.
  - Typing "LAP" in the search box filters by SKU correctly (case-insensitive).
  - Clearing the search box restores all active products.
  - With "Show Inactive" unchecked: inactive products excluded from results.
  - With "Show Inactive" checked: inactive products included in results.
  - If any of these fail, fix `products_db.search_products()` in `products_db.py`
    or the signal connection in `ui/products_page.py`.

**Checkpoint (US4)**: Quickstart Checkpoints 12–14 pass.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final checks before Phase 3 (Purchases) begins.

- [x] T007 [P] Verify layering compliance for Phase 2 files:
  - `products_db.py` MUST NOT import PySide6 and MUST NOT contain business rule logic
    beyond SQL queries and the `is_product_referenced` guard query.
  - `ui/product_dialog.py` MUST NOT import `sqlite3` directly (it catches
    `sqlite3.IntegrityError` — this is acceptable since `sqlite3` is a stdlib type).
  - `ui/products_page.py` MUST NOT import `sqlite3` directly.
  - `get_active_products()` in `products_db.py` MUST be the only function returning
    active products for pickers — no duplicate function with a different name.
  Fix any violation before marking complete.

- [x] T008 [P] Verify error handling compliance for Phase 2 files:
  - `ui/product_dialog.py._on_save`: `sqlite3.IntegrityError` caught and shown as
    friendly message; unexpected `Exception` caught with traceback logged and generic
    message shown.
  - `ui/products_page.py._load_products`: exception caught, logged, friendly message.
  - `ui/products_page.py._on_delete` / `_on_deactivate` / `_on_activate`: each has
    its own `try/except Exception` block.
  Fix any missing handler before marking complete.

- [ ] T009 [P] Verify the table refreshes correctly in all cases:
  - After Add Product → table reloads showing the new product.
  - After Edit Product → table reloads showing updated values.
  - After Delete → table reloads without the deleted product.
  - After Deactivate (when "Show Inactive" is unchecked) → product disappears from
    table immediately.
  - After Activate (when "Show Inactive" is checked) → product status changes to
    "Active".
  - Navigating away from Products page and back → table reloads fresh (the `showEvent`
    override in `ProductsPage` ensures this).
  Fix any case where the table does not reload correctly.

- [ ] T010 Run the full Phase 2 manual testing checklist from `quickstart.md`
  (Checkpoints 1–17) in a single continuous session. This includes the Phase 1
  regression check (Checkpoint 17). Mark each checkpoint as passed. Do NOT mark T010
  complete until every checkpoint passes. Any failure is a bug — fix and re-run.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundation (Phase 1 — T001)**: No dependencies beyond Phase 1 being complete.
  Start immediately.
- **US1 (Phase 3 — T002→T003)**: Depends on T001. T002 before T003 (dialog before
  page).
- **US2 (Phase 4 — T004)**: Depends on T002 and T003 already complete (they implement
  US2). T004 is verification only.
- **US3 (Phase 5 — T005)**: Depends on T003 (implements US3). T005 is verification.
- **US4 (Phase 6 — T006)**: Depends on T001 and T003. T006 is verification.
- **Polish (Phase 7 — T007–T010)**: Depends on all prior phases complete.

### Strict Build Order

```
T001 (products_db.py)
  → T002 (product_dialog.py)
      → T003 (products_page.py)
          → T004, T005, T006  (verification — can run in parallel)
              → T007, T008, T009  (compliance checks — can run in parallel)
                  → T010  (full regression run — must be last)
```

### Parallel Opportunities

```
# After T003 is complete, these three verification tasks can run in parallel:
T004  T005  T006

# After T004+T005+T006, these compliance tasks can run in parallel:
T007  T008  T009

# T010 must be last — it is the full regression gate
T010
```

---

## Implementation Notes for the Implementer

1. **`QDoubleSpinBox` for numeric fields**: Using `QDoubleSpinBox` (not `QLineEdit`)
   for all numeric fields means the user can never type a non-numeric value — no
   extra numeric-format validation needed. The `>= 0` lower bound is enforced by
   `setRange(0, 9_999_999)`.

2. **SKU blank → `None`**: When the SKU field is empty, pass `None` (Python None)
   to `products_db`, NOT an empty string `""`. SQLite's UNIQUE constraint treats
   multiple NULLs as allowed; multiple empty strings would conflict.

3. **`is_product_referenced` in every table load**: The `_add_action_buttons` method
   calls `is_product_referenced(product_id)` for each row. For a catalog of typical
   size (up to ~thousands of rows) this is acceptable — each call is a cheap indexed
   query. If performance becomes a concern in later phases, this can be batched, but
   do not optimize prematurely.

4. **`showEvent` for page refresh**: `ProductsPage.showEvent` overrides the Qt widget
   method and calls `_load_products()`. This ensures the table refreshes every time
   the user switches to the Products page from another page. No extra signal wiring in
   `main_window.py` is needed.

5. **Table "no results" display**: When `search_products()` returns zero rows, a
   single row with "No products found." is shown spanning columns 1–8. The `setSpan`
   call must happen after `setRowCount(1)` and before `setItem`. Clear the span before
   the next normal load by setting `setRowCount(0)` first (which also clears all
   spans).

6. **No changes to `main_window.py`**: The new `ui/products_page.py` uses the same
   class name (`ProductsPage`) as the placeholder it replaces. `main_window.py`
   already imports `from ui.products_page import ProductsPage` — no edit needed.

7. **IntegrityError import in dialog**: `product_dialog.py` imports `sqlite3` at the
   top to reference `sqlite3.IntegrityError` in the except clause. This is a stdlib
   type reference, not a direct database call — it does not violate the layering rule
   (which prohibits UI files from calling `sqlite3.connect()` or writing SQL).
