import traceback

def _fmt(v) -> str:
    """Format a number, dropping unnecessary trailing zeros (e.g. 50.00→'50', 6.5→'6.5')."""
    s = f"{v:.2f}"
    return s.rstrip("0").rstrip(".")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLabel, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import products_db
from ui.product_dialog import ProductDialog
from ui import theme


class ProductsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_products()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_xl,
            theme._active.spacing_xl, theme._active.spacing_xl)
        layout.setSpacing(theme._active.spacing_lg)

        # ── Page header ──────────────────────────────────────────────
        header_row = QHBoxLayout()
        page_title = QLabel("Products")
        title_font = QFont(theme._active.font_family, theme._active.size_page_title)
        title_font.setBold(True)
        page_title.setFont(title_font)
        page_title.setStyleSheet(
            f"color: {theme._active.text_primary}; background: transparent;")
        header_row.addWidget(page_title)
        header_row.addStretch()
        self.add_btn = QPushButton("  + Add Product")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.setMinimumWidth(130)
        header_row.addWidget(self.add_btn)
        layout.addLayout(header_row)

        # ── Search / filter toolbar ──────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setSpacing(theme._active.spacing_md)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products by name or category…")
        self.search_input.setMaximumWidth(400)
        self.show_inactive_cb = QCheckBox("Show Inactive")
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.show_inactive_cb)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ── Products table ───────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Category",
            "Purchase Price", "Selling Price", "Profit/Unit", "Stock Profit",
            "Stock Qty", "Reorder Level", "Status",
            "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnHidden(0, True)
        # Fixed widths — sized to fit uppercase header text at the theme font
        for col, w in [(2, 100), (3, 132), (4, 122), (5, 100), (6, 112), (7, 95), (8, 128), (9, 72), (10, 152)]:
            self.table.setColumnWidth(col, w)
        self.table.setStyleSheet(
            f"QTableWidget {{ border-radius: {theme._active.card_border_radius}px;"
            f" border: 1px solid {theme._active.border}; }}")
        theme.apply_table_style(self.table)

        self._empty_lbl = theme.make_empty_label("No products added yet. Click '+ Add Product' to get started.")
        self._empty_search_lbl = theme.make_empty_label("No products match your search.")
        layout.addWidget(self.table)
        layout.addWidget(self._empty_lbl)
        layout.addWidget(self._empty_search_lbl)
        self._empty_lbl.hide()
        self._empty_search_lbl.hide()

        layout.addStretch()

        self.search_input.textChanged.connect(self._load_products)
        self.show_inactive_cb.stateChanged.connect(self._load_products)
        self.add_btn.clicked.connect(self._on_add)

    def _load_products(self):
        search_text      = self.search_input.text().strip()
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

            def _item(text):
                it = QTableWidgetItem(text)
                it.setToolTip(text)
                return it

            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, _item(row["name"] or ""))
            self.table.setItem(r, 2, _item(row["category"] or ""))
            profit = row['selling_price'] - row['purchase_price']
            stock_profit = profit * row['stock_quantity']
            self.table.setItem(r, 3, _item(_fmt(row['purchase_price'])))
            self.table.setItem(r, 4, _item(_fmt(row['selling_price'])))
            self.table.setItem(r, 5, _item(_fmt(profit)))
            self.table.setItem(r, 6, _item(_fmt(stock_profit)))
            self.table.setItem(r, 7, _item(_fmt(row['stock_quantity'])))
            self.table.setItem(r, 8, _item(_fmt(row['reorder_level'])))
            status = "Active" if row["is_active"] else "Inactive"
            self.table.setItem(r, 9, _item(status))

            self._add_action_buttons(r, row["id"], bool(row["is_active"]))

        has_rows = self.table.rowCount() > 0
        search_active = bool(self.search_input.text().strip())
        self.table.setVisible(has_rows)
        self._empty_lbl.setVisible(not has_rows and not search_active)
        self._empty_search_lbl.setVisible(not has_rows and search_active)

    def _add_action_buttons(self, row_index: int, product_id: int, is_active: bool):
        cell_widget = QWidget()
        btn_layout  = QHBoxLayout(cell_widget)
        btn_layout.setContentsMargins(2, 2, 2, 2)
        btn_layout.setSpacing(4)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedWidth(50)
        edit_btn.clicked.connect(lambda: self._on_edit(product_id))
        btn_layout.addWidget(edit_btn)

        if products_db.is_product_referenced(product_id):
            if is_active:
                action_btn = QPushButton("Deactivate")
                action_btn.setProperty("class", "destructive")
                action_btn.clicked.connect(
                    lambda: self._on_deactivate(product_id))
            else:
                action_btn = QPushButton("Activate")
                action_btn.clicked.connect(
                    lambda: self._on_activate(product_id))
        else:
            action_btn = QPushButton("Delete")
            action_btn.setProperty("class", "destructive")
            action_btn.clicked.connect(lambda: self._on_delete(product_id))

        btn_layout.addWidget(action_btn)
        self.table.setCellWidget(row_index, 10, cell_widget)

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

    def highlight_product(self, product_id: int):
        product = products_db.get_product_by_id(product_id)
        if product is None:
            return
        self.search_input.setText(product["name"])
        self._load_products()
        for r in range(self.table.rowCount()):
            id_item = self.table.item(r, 0)
            if id_item and id_item.text() == str(product_id):
                self.table.selectRow(r)
                break

    def showEvent(self, event):
        super().showEvent(event)
        self._load_products()
