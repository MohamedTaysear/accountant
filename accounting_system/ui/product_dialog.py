import traceback

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout, QFrame,
    QLineEdit, QComboBox, QDoubleSpinBox, QPushButton, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui import theme


class _SpinBox(QDoubleSpinBox):
    """QDoubleSpinBox that drops unnecessary trailing zeros in its display."""
    def textFromValue(self, value: float) -> str:
        s = f"{value:.2f}"
        return s.rstrip("0").rstrip(".")

import products_db


class ProductDialog(QDialog):
    def __init__(self, product_id=None, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("Edit Product" if product_id else "Add Product")
        self.setMinimumWidth(420)
        self._build_ui()
        if product_id:
            self._prefill(product_id)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_xl,
            theme._active.spacing_xl, theme._active.spacing_xl)
        outer.setSpacing(theme._active.spacing_lg)

        # Dialog title
        title_text = "Edit Product" if self.product_id else "Add Product"
        title_lbl = QLabel(title_text)
        title_font = QFont(theme._active.font_family, theme._active.size_heading)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(
            f"color: {theme._active.text_primary}; background: transparent;")
        outer.addWidget(title_lbl)

        # Form card
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: {theme._active.surface};"
            f" border: 1px solid {theme._active.border};"
            f" border-radius: {theme._active.card_border_radius}px; }}")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_lg,
            theme._active.spacing_xl, theme._active.spacing_lg)
        card_layout.setSpacing(theme._active.spacing_sm)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.setInsertPolicy(QComboBox.NoInsert)
        self.category_input.lineEdit().setPlaceholderText("Select or type a category…")
        try:
            for cat in products_db.get_categories():
                self.category_input.addItem(cat)
        except Exception:
            pass
        self.category_input.setCurrentIndex(-1)

        def spinbox():
            sb = _SpinBox()
            sb.setRange(0, 9_999_999)
            sb.setDecimals(2)
            return sb

        self.purchase_price_input = spinbox()
        self.selling_price_input  = spinbox()
        self.stock_quantity_input = spinbox()
        self.reorder_level_input  = spinbox()
        self.reorder_level_input.setValue(5)

        form = QFormLayout()
        form.setSpacing(theme._active.spacing_md)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.addRow("Name *:",         self.name_input)
        form.addRow("Category *:",     self.category_input)
        form.addRow("Purchase Price:", self.purchase_price_input)
        form.addRow("Selling Price:",  self.selling_price_input)
        form.addRow("Stock Quantity:", self.stock_quantity_input)
        form.addRow("Reorder Level:",  self.reorder_level_input)
        card_layout.addLayout(form)
        outer.addWidget(card)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(theme._active.spacing_md)
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn   = QPushButton("Save Product")
        self.save_btn.setProperty("class", "primary")
        btn_row.addStretch()
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.save_btn)
        outer.addLayout(btn_row)

        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.reject)

    def _prefill(self, product_id: int):
        row = products_db.get_product_by_id(product_id)
        if row is None:
            return
        self.name_input.setText(row["name"] or "")
        # Set category: if it already exists in the list select it, else add+select it
        cat = row["category"] or ""
        idx = self.category_input.findText(cat, Qt.MatchFixedString)
        if idx >= 0:
            self.category_input.setCurrentIndex(idx)
        else:
            self.category_input.setCurrentText(cat)
        self.purchase_price_input.setValue(row["purchase_price"] or 0)
        self.selling_price_input.setValue(row["selling_price"] or 0)
        self.stock_quantity_input.setValue(row["stock_quantity"] or 0)
        self.reorder_level_input.setValue(row["reorder_level"] or 0)

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Product name is required.")
            return
        if len(name) > 100:
            QMessageBox.warning(self, "Validation Error",
                                "Product name must be 100 characters or fewer.")
            return

        category = self.category_input.currentText().strip()
        if not category:
            QMessageBox.warning(self, "Validation Error", "Category is required.")
            return

        purchase_price = self.purchase_price_input.value()
        selling_price  = self.selling_price_input.value()
        stock_quantity = self.stock_quantity_input.value()
        reorder_level  = self.reorder_level_input.value()

        if selling_price < purchase_price:
            answer = QMessageBox.question(
                self, "Price Warning",
                "Selling price is less than purchase price. Save anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if answer != QMessageBox.Yes:
                return

        try:
            if self.product_id is None:
                products_db.insert_product(
                    name, category, purchase_price, selling_price,
                    stock_quantity, reorder_level
                )
            else:
                products_db.update_product(
                    self.product_id, name, category, purchase_price,
                    selling_price, stock_quantity, reorder_level
                )
            self.accept()
        except Exception:
            print(traceback.format_exc())
            QMessageBox.critical(self, "Unexpected Error",
                "An unexpected error occurred. Please try again.")
