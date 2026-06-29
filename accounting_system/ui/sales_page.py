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
    QHeaderView, QMessageBox, QApplication, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont


class _SpinBox(QDoubleSpinBox):
    def textFromValue(self, value: float) -> str:
        s = f"{value:.2f}"
        return s.rstrip("0").rstrip(".")


import products_db
from logic import sales_logic
from ui import theme


class SalesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._build_ui()
        self._refresh_invoice_number()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_xl,
            theme._active.spacing_xl, theme._active.spacing_xl)
        layout.setSpacing(theme._active.spacing_lg)

        # ── Page header ──────────────────────────────────────────────
        page_title = QLabel("New Sales Invoice")
        title_font = QFont(theme._active.font_family, theme._active.size_page_title)
        title_font.setBold(True)
        page_title.setFont(title_font)
        page_title.setStyleSheet(
            f"color: {theme._active.text_primary}; background: transparent;")
        layout.addWidget(page_title)

        # ── Invoice header card ──────────────────────────────────────
        header_card = QFrame()
        header_card.setStyleSheet(
            f"QFrame {{ background-color: {theme._active.surface};"
            f" border: 1px solid {theme._active.border};"
            f" border-radius: {theme._active.card_border_radius}px; }}")
        header_card_layout = QHBoxLayout(header_card)
        header_card_layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_lg,
            theme._active.spacing_xl, theme._active.spacing_lg)
        header_card_layout.setSpacing(theme._active.spacing_xxl)

        header_form = QFormLayout()
        header_form.setSpacing(theme._active.spacing_sm)
        header_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.invoice_number_label = QLabel("SAL-000001")
        self.invoice_number_label.setStyleSheet(
            f"font-weight: bold; color: {theme._active.primary}; background: transparent;")
        header_form.addRow("Invoice #:", self.invoice_number_label)

        self.date_label = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
        self.date_label.setStyleSheet("background: transparent;")
        header_form.addRow("Date:", self.date_label)

        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Optional customer name")
        self.customer_input.setMaximumWidth(280)
        header_form.addRow("Customer:", self.customer_input)

        header_card_layout.addLayout(header_form)
        header_card_layout.addStretch()
        header_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(header_card)

        # ── Add item row ─────────────────────────────────────────────
        add_card = QFrame()
        add_card.setStyleSheet(
            f"QFrame {{ background-color: {theme._active.surface};"
            f" border: 1px solid {theme._active.border};"
            f" border-radius: {theme._active.card_border_radius}px; }}")
        add_card_layout = QHBoxLayout(add_card)
        add_card_layout.setContentsMargins(
            theme._active.spacing_lg, theme._active.spacing_md,
            theme._active.spacing_lg, theme._active.spacing_md)
        add_card_layout.setSpacing(theme._active.spacing_md)
        add_card_layout.setAlignment(Qt.AlignVCenter)

        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(260)
        self.product_combo.setEditable(False)

        self.qty_spin = _SpinBox()
        self.qty_spin.setRange(0.01, 999_999)
        self.qty_spin.setDecimals(2)
        self.qty_spin.setValue(1.0)
        self.qty_spin.setFixedWidth(90)

        self.add_line_btn = QPushButton("+ Add to Invoice")
        self.add_line_btn.setProperty("class", "primary")

        prod_lbl = QLabel("Product:")
        prod_lbl.setStyleSheet(
            f"color: {theme._active.text_secondary}; background: transparent;")
        qty_lbl = QLabel("Qty:")
        qty_lbl.setStyleSheet(
            f"color: {theme._active.text_secondary}; background: transparent;")

        add_card_layout.addWidget(prod_lbl)
        add_card_layout.addWidget(self.product_combo, 2)
        add_card_layout.addWidget(qty_lbl)
        add_card_layout.addWidget(self.qty_spin)
        add_card_layout.addWidget(self.add_line_btn)
        add_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(add_card)

        # ── Line items table ─────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Product", "Qty", "Unit Price", "Subtotal", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col, w in [(1, 70), (2, 100), (3, 100), (4, 80)]:
            self.table.setColumnWidth(col, w)
        self.table.setStyleSheet(
            f"QTableWidget {{ border-radius: {theme._active.card_border_radius}px;"
            f" border: 1px solid {theme._active.border}; }}")
        theme.apply_table_style(self.table)
        self._empty_table_lbl = theme.make_empty_label("No items added to this invoice yet.")
        layout.addWidget(self.table)
        layout.addWidget(self._empty_table_lbl)
        self._empty_table_lbl.hide()

        # ── Footer / totals ──────────────────────────────────────────
        footer_card = QFrame()
        footer_card.setStyleSheet(
            f"QFrame {{ background-color: {theme._active.surface};"
            f" border: 1px solid {theme._active.border};"
            f" border-radius: {theme._active.card_border_radius}px; }}")
        footer = QHBoxLayout(footer_card)
        footer.setContentsMargins(
            theme._active.spacing_lg, theme._active.spacing_md,
            theme._active.spacing_lg, theme._active.spacing_md)
        footer.setSpacing(theme._active.spacing_md)

        self.subtotal_label = QLabel("Subtotal: 0.00")
        subtotal_font = QFont(theme._active.font_family, theme._active.size_normal)
        subtotal_font.setBold(True)
        self.subtotal_label.setFont(subtotal_font)
        self.subtotal_label.setStyleSheet("background: transparent;")

        self.discount_type_combo = QComboBox()
        self.discount_type_combo.addItem("Fixed")
        self.discount_type_combo.addItem("%")
        self.discount_type_combo.setFixedWidth(70)

        self.discount_spin = _SpinBox()
        self.discount_spin.setRange(0, 9_999_999)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setValue(0.0)
        self.discount_spin.setFixedWidth(100)

        self.grand_total_label = QLabel("Grand Total: 0.00")
        gt_font = QFont(theme._active.font_family, theme._active.size_heading)
        gt_font.setBold(True)
        self.grand_total_label.setFont(gt_font)
        self.grand_total_label.setStyleSheet(
            f"color: {theme._active.primary}; background: transparent;")

        self.clear_btn = QPushButton("Clear Invoice")
        self.clear_btn.setProperty("class", "destructive")
        self.save_btn = QPushButton("Save Invoice")
        self.save_btn.setProperty("class", "primary")

        disc_lbl = QLabel("Discount:")
        disc_lbl.setStyleSheet(
            f"color: {theme._active.text_secondary}; background: transparent;")

        footer.addWidget(self.subtotal_label)
        footer.addStretch()
        footer.addWidget(disc_lbl)
        footer.addWidget(self.discount_spin)
        footer.addWidget(self.discount_type_combo)
        footer.addSpacing(theme._active.spacing_lg)
        footer.addWidget(self.grand_total_label)
        footer.addSpacing(theme._active.spacing_xl)
        footer.addWidget(self.clear_btn)
        footer.addWidget(self.save_btn)
        footer_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(footer_card)
        layout.addStretch()

        # ── Signals ────────────────────────────────────────────────
        self.product_combo.currentIndexChanged.connect(self._on_product_selected)
        self.add_line_btn.clicked.connect(self._on_add_line)
        self.discount_spin.valueChanged.connect(self._on_discount_changed)
        self.discount_type_combo.currentIndexChanged.connect(self._on_discount_type_changed)
        self.clear_btn.clicked.connect(self._on_clear)
        self.save_btn.clicked.connect(self._on_save)

    # ── Helpers ────────────────────────────────────────────────────

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
                    userData={
                        "id": row["id"],
                        "name": row["name"],
                        "selling_price": row["selling_price"],
                    }
                )
        except Exception:
            print(traceback.format_exc())
        self.product_combo.blockSignals(False)

    def _get_subtotal(self) -> float:
        return sum(item["subtotal"] for item in self._items)

    def _discount_amount(self) -> float:
        subtotal = self._get_subtotal()
        value = self.discount_spin.value()
        if self.discount_type_combo.currentText() == "%":
            return round(subtotal * value / 100, 2)
        return value

    def _update_totals(self):
        subtotal = self._get_subtotal()
        discount = self._discount_amount()
        grand_total = max(0.0, subtotal - discount)
        self.subtotal_label.setText(f"Subtotal: {_fmt_total(subtotal)}")
        self.grand_total_label.setText(f"Grand Total: {_fmt_total(grand_total)}")
        if discount > subtotal:
            self.discount_spin.setStyleSheet(
                "QDoubleSpinBox { border: 2px solid red; }")
        else:
            self.discount_spin.setStyleSheet("")

    def _rebuild_table(self):
        self.table.setRowCount(0)
        for idx, item in enumerate(self._items):
            r = self.table.rowCount()
            self.table.insertRow(r)

            def _item(text):
                it = QTableWidgetItem(text)
                it.setToolTip(text)
                return it

            self.table.setItem(r, 0, _item(item["product_name"]))
            self.table.setItem(r, 1, _item(_fmt(item["quantity"])))
            self.table.setItem(r, 2, _item(_fmt(item["unit_price"])))
            self.table.setItem(r, 3, _item(_fmt(item["subtotal"])))
            remove_btn = QPushButton("Remove")
            remove_btn.setMinimumWidth(theme._BTN_MIN_REMOVE)
            remove_btn.clicked.connect(
                lambda checked=False, i=idx: self._on_remove_line(i))
            self.table.setCellWidget(r, 4, remove_btn)
        has_rows = self.table.rowCount() > 0
        self.table.setVisible(has_rows)
        self._empty_table_lbl.setVisible(not has_rows)

    def _reset_form(self):
        self._items = []
        self.customer_input.clear()
        self.discount_type_combo.setCurrentIndex(0)
        self.discount_spin.setRange(0, 9_999_999)
        self.discount_spin.setValue(0.0)
        self.discount_spin.setStyleSheet("")
        self._rebuild_table()
        self._update_totals()
        self._refresh_invoice_number()

    # ── Signal Handlers ────────────────────────────────────────────

    def _on_product_selected(self, index):
        if index >= 0:
            self.qty_spin.setFocus()
            self.qty_spin.selectAll()

    def _on_discount_changed(self, value: float):
        self._update_totals()

    def _on_discount_type_changed(self, index: int):
        if self.discount_type_combo.itemText(index) == "%":
            self.discount_spin.setRange(0, 100)
            if self.discount_spin.value() > 100:
                self.discount_spin.setValue(100)
        else:
            self.discount_spin.setRange(0, 9_999_999)
        self.discount_spin.setValue(0.0)
        self._update_totals()

    def _on_add_line(self):
        idx = self.product_combo.currentIndex()
        if idx < 0:
            QMessageBox.warning(self, "No Product",
                                "Please select a product first.")
            return

        product_data = self.product_combo.itemData(idx)
        quantity = self.qty_spin.value()
        unit_price = product_data["selling_price"]

        ok, msg = sales_logic.validate_line(quantity, unit_price)
        if not ok:
            QMessageBox.warning(self, "Validation Error", msg)
            return

        ok, msg = sales_logic.validate_stock(
            product_data["id"], quantity, self._items)
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

        discount = self._discount_amount()
        subtotal = self._get_subtotal()
        if discount > subtotal:
            QMessageBox.warning(self, "Invalid Discount",
                f"Discount ({_fmt(discount)}) cannot exceed "
                f"invoice subtotal ({_fmt(subtotal)}).")
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
        self._reload_products()  # refresh active products — do NOT call _reset_form()
