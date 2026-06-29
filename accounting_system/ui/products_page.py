import traceback

def _fmt(v) -> str:
    """Format a number, dropping unnecessary trailing zeros (e.g. 50.00→'50', 6.5→'6.5')."""
    s = f"{v:.2f}"
    return s.rstrip("0").rstrip(".")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import qtawesome as qta

import products_db
from ui.product_dialog import ProductDialog
from ui import theme


class ProductsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_products()

    def _build_ui(self):
        t = theme._active
        layout = QVBoxLayout(self)
        layout.setContentsMargins(t.spacing_xl, t.spacing_xl, t.spacing_xl, t.spacing_xl)
        layout.setSpacing(t.spacing_lg)

        # ── Page header ──────────────────────────────────────────────
        header_row = QHBoxLayout()
        page_title = QLabel("Products Inventory")
        title_font = QFont(t.font_family, t.size_page_title)
        title_font.setBold(True)
        page_title.setFont(title_font)
        page_title.setStyleSheet(f"color: {t.text_primary}; background: transparent; font-weight: 700;")
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.box', color=t.primary).pixmap(24, 24))
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        
        header_row.addWidget(icon_lbl)
        header_row.addWidget(page_title)
        
        header_row.addStretch()
        
        self.add_btn = QPushButton("  Add Product")
        self.add_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        self.add_btn.setStyleSheet(
            f"QPushButton {{ background-color: {t.primary}; color: white; border: none; border-radius: 8px; padding: 8px 16px; font-weight: 600; font-size: {t.size_section}pt; }}"
            f"QPushButton:hover {{ background-color: {t.primary_hover}; }}"
        )
        self.add_btn.setMinimumHeight(44)
        self.add_btn.setMinimumWidth(160)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        header_row.addWidget(self.add_btn)
        layout.addLayout(header_row)

        # ── Control Bar (Search / Filter) ─────────────────────────────
        control_frame = QFrame()
        control_frame.setStyleSheet(
            f"QFrame {{"
            f" background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px;"
            f"}}"
        )
        control_frame.setGraphicsEffect(theme.make_card_shadow())
        
        toolbar = QHBoxLayout(control_frame)
        toolbar.setContentsMargins(t.spacing_md, t.spacing_sm, t.spacing_md, t.spacing_sm)
        toolbar.setSpacing(t.spacing_md)
        toolbar.setAlignment(Qt.AlignVCenter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search products by name or category…")
        self.search_input.setMaximumWidth(400)
        self.search_input.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px 12px; background: {t.background}; }}"
            f"QLineEdit:focus {{ border-color: {t.primary}; }}"
        )
        
        self.show_inactive_cb = QCheckBox("Show Inactive")
        self.show_inactive_cb.setCursor(Qt.PointingHandCursor)
        
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.show_inactive_cb)
        toolbar.addStretch()
        layout.addWidget(control_frame)

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
        # Fixed widths 
        for col, w in [(2, 120), (3, 140), (4, 130), (5, 120), (6, 120), (7, 100), (8, 130), (9, 100)]:
            self.table.setColumnWidth(col, w)
            
        theme.apply_table_style(self.table)
        theme.apply_actions_column(self.table, 10)

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
        t = theme._active
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)

            def _item(text):
                it = QTableWidgetItem(text)
                it.setToolTip(text)
                return it

            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            
            name_item = _item(row["name"] or "")
            name_item.setFont(QFont(t.font_family, t.size_normal, QFont.Bold))
            self.table.setItem(r, 1, name_item)
            
            self.table.setItem(r, 2, _item(row["category"] or ""))
            
            profit = row['selling_price'] - row['purchase_price']
            stock_profit = profit * row['stock_quantity']
            self.table.setItem(r, 3, _item(_fmt(row['purchase_price'])))
            self.table.setItem(r, 4, _item(_fmt(row['selling_price'])))
            
            profit_item = _item(_fmt(profit))
            profit_item.setForeground(QColor(theme.color_for_value(profit)))
            self.table.setItem(r, 5, profit_item)
            
            stock_profit_item = _item(_fmt(stock_profit))
            stock_profit_item.setForeground(QColor(theme.color_for_value(stock_profit)))
            self.table.setItem(r, 6, stock_profit_item)
            
            qty = row['stock_quantity']
            reorder = row['reorder_level']
            qty_item = _item(str(qty))
            if qty <= reorder:
                qty_item.setForeground(QColor(t.error))
                qty_item.setFont(QFont(t.font_family, t.size_normal, QFont.Bold))
            self.table.setItem(r, 7, qty_item)
            
            self.table.setItem(r, 8, _item(str(reorder)))
            
            status = "Active" if row["is_active"] else "Inactive"
            status_item = _item(status)
            status_item.setForeground(QColor(t.success if row["is_active"] else t.text_disabled))
            self.table.setItem(r, 9, status_item)

            self._add_action_buttons(r, row["id"], bool(row["is_active"]))

        has_rows = self.table.rowCount() > 0
        search_active = bool(self.search_input.text().strip())
        self.table.setVisible(has_rows)
        self._empty_lbl.setVisible(not has_rows and not search_active)
        self._empty_search_lbl.setVisible(not has_rows and search_active)

    def _add_action_buttons(self, row_index: int, product_id: int, is_active: bool):
        t = theme._active
        cell_widget = QWidget()
        btn_layout  = QHBoxLayout(cell_widget)
        btn_layout.setContentsMargins(8, 4, 8, 4)
        btn_layout.setSpacing(12)

        btn_style = (
            f"QPushButton {{ background-color: {t.surface_alt}; color: {t.text_primary};"
            f" border: 1px solid {t.border}; border-radius: 6px; padding: 6px 12px; font-weight: 500; }}"
            f"QPushButton:hover {{ background-color: {t.primary}; color: white; border: none; }}"
        )
        dest_style = (
            f"QPushButton {{ background-color: {t.surface_alt}; color: {t.error};"
            f" border: 1px solid {t.border}; border-radius: 6px; padding: 6px 12px; font-weight: 500; }}"
            f"QPushButton:hover {{ background-color: {t.error}; color: white; border: none; }}"
        )

        edit_btn = QPushButton(" Edit")
        edit_btn.setIcon(qta.icon('fa5s.edit', color=t.text_primary))
        edit_btn.setStyleSheet(btn_style)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self._on_edit(product_id))
        btn_layout.addWidget(edit_btn)

        if products_db.is_product_referenced(product_id):
            if is_active:
                action_btn = QPushButton(" Hide")
                action_btn.setIcon(qta.icon('fa5s.eye-slash', color=t.error))
                action_btn.setStyleSheet(dest_style)
                action_btn.setCursor(Qt.PointingHandCursor)
                action_btn.clicked.connect(lambda: self._on_deactivate(product_id))
            else:
                action_btn = QPushButton(" Show")
                action_btn.setIcon(qta.icon('fa5s.eye', color=t.text_primary))
                action_btn.setStyleSheet(btn_style)
                action_btn.setCursor(Qt.PointingHandCursor)
                action_btn.clicked.connect(lambda: self._on_activate(product_id))
        else:
            action_btn = QPushButton(" Delete")
            action_btn.setIcon(qta.icon('fa5s.trash-alt', color=t.error))
            action_btn.setStyleSheet(dest_style)
            action_btn.setCursor(Qt.PointingHandCursor)
            action_btn.clicked.connect(lambda: self._on_delete(product_id))

        btn_layout.addWidget(action_btn)
        
        # Update icon colors on hover for a premium feel
        edit_btn.installEventFilter(self)
        action_btn.installEventFilter(self)
        
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
