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
from PySide6.QtGui import QFont, QColor


class _SpinBox(QDoubleSpinBox):
    def textFromValue(self, value: float) -> str:
        s = f"{value:.2f}"
        return s.rstrip("0").rstrip(".")


import products_db
from logic import sales_logic
from logic.customers_logic import get_all_customers_for_selector, create_customer
from ui import theme


class SalesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._build_ui()
        self._refresh_invoice_number()

    def _build_ui(self):
        t = theme._active
        layout = QVBoxLayout(self)
        layout.setContentsMargins(t.spacing_xl, t.spacing_xl, t.spacing_xl, t.spacing_xl)
        layout.setSpacing(t.spacing_lg)

        # ── Page header ──────────────────────────────────────────────
        page_title = QLabel("🛍️ New Sales Invoice")
        title_font = QFont(t.font_family, t.size_page_title)
        title_font.setBold(True)
        page_title.setFont(title_font)
        page_title.setStyleSheet(f"color: {t.text_primary}; background: transparent; font-weight: 700;")
        layout.addWidget(page_title)

        # ── Invoice header card ──────────────────────────────────────
        header_card = QFrame()
        header_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        header_card.setGraphicsEffect(theme.make_card_shadow())
        header_card_layout = QHBoxLayout(header_card)
        header_card_layout.setContentsMargins(t.spacing_xl, t.spacing_md, t.spacing_xl, t.spacing_md)
        header_card_layout.setSpacing(t.spacing_xxl)

        header_form = QFormLayout()
        header_form.setSpacing(t.spacing_md)
        header_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.invoice_number_label = QLabel("SAL-000001")
        self.invoice_number_label.setStyleSheet(
            f"font-weight: 700; font-size: {t.size_section}pt; color: {t.primary}; background: transparent;")
        header_form.addRow("Invoice #:", self.invoice_number_label)

        self.date_label = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
        self.date_label.setStyleSheet(f"background: transparent; color: {t.text_primary}; font-weight: 500;")
        header_form.addRow("Date:", self.date_label)

        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        self.customer_combo.setMaximumWidth(320)
        self.customer_combo.setInsertPolicy(QComboBox.NoInsert)
        self.customer_combo.setStyleSheet(
            f"QComboBox {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px; background: {t.background}; }}"
        )
        self._selected_customer_id = None
        self._customer_data = []
        self._refresh_customer_combo()
        self.customer_combo.currentIndexChanged.connect(self._on_customer_selected)
        self._customer_label = QLabel("Customer (Optional):")
        header_form.addRow(self._customer_label, self.customer_combo)

        header_card_layout.addLayout(header_form)
        header_card_layout.addStretch()
        header_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(header_card)

        # ── Add item row ─────────────────────────────────────────────
        add_card = QFrame()
        add_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        add_card.setGraphicsEffect(theme.make_card_shadow())
        add_card_layout = QHBoxLayout(add_card)
        add_card_layout.setContentsMargins(t.spacing_lg, t.spacing_md, t.spacing_lg, t.spacing_md)
        add_card_layout.setSpacing(t.spacing_md)
        add_card_layout.setAlignment(Qt.AlignVCenter)

        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(260)
        self.product_combo.setEditable(False)
        self.product_combo.setStyleSheet(
            f"QComboBox {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px; background: {t.background}; }}"
        )

        self.qty_spin = _SpinBox()
        self.qty_spin.setRange(0.01, 999_999)
        self.qty_spin.setDecimals(2)
        self.qty_spin.setValue(1.0)
        self.qty_spin.setFixedWidth(100)

        self.add_line_btn = QPushButton("➕ Add to Invoice")
        self.add_line_btn.setProperty("class", "primary")
        self.add_line_btn.setCursor(Qt.PointingHandCursor)

        prod_lbl = QLabel("Product:")
        prod_lbl.setStyleSheet(f"color: {t.text_secondary}; background: transparent; font-weight: 500;")
        qty_lbl = QLabel("Qty:")
        qty_lbl.setStyleSheet(f"color: {t.text_secondary}; background: transparent; font-weight: 500;")

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
        self.table.setHorizontalHeaderLabels(["Product", "Qty", "Unit Price", "Subtotal", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col, w in [(1, 90), (2, 120), (3, 120), (4, 100)]:
            self.table.setColumnWidth(col, w)
        theme.apply_table_style(self.table)
        self._empty_table_lbl = theme.make_empty_label("No items added to this invoice yet.")
        layout.addWidget(self.table)
        layout.addWidget(self._empty_table_lbl)
        self._empty_table_lbl.hide()

        # ── Footer card (totals + payment + actions) ─────────────────
        footer_card = QFrame()
        footer_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        footer_card.setGraphicsEffect(theme.make_card_shadow())
        footer_vbox = QVBoxLayout(footer_card)
        footer_vbox.setContentsMargins(t.spacing_lg, t.spacing_lg, t.spacing_lg, t.spacing_lg)
        footer_vbox.setSpacing(t.spacing_md)

        # -- Totals row --
        totals_row = QHBoxLayout()
        totals_row.setSpacing(t.spacing_md)

        self.subtotal_label = QLabel("Subtotal: 0.00")
        subtotal_font = QFont(t.font_family, t.size_section)
        subtotal_font.setBold(True)
        self.subtotal_label.setFont(subtotal_font)
        self.subtotal_label.setStyleSheet("background: transparent;")

        self.discount_type_combo = QComboBox()
        self.discount_type_combo.addItem("Fixed")
        self.discount_type_combo.addItem("%")
        self.discount_type_combo.setFixedWidth(80)

        self.discount_spin = _SpinBox()
        self.discount_spin.setRange(0, 9_999_999)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setValue(0.0)
        self.discount_spin.setFixedWidth(120)

        self.grand_total_label = QLabel("Grand Total: 0.00")
        gt_font = QFont(t.font_family, t.size_kpi_value)
        gt_font.setBold(True)
        self.grand_total_label.setFont(gt_font)
        self.grand_total_label.setStyleSheet(
            f"color: {t.primary}; background: transparent; font-weight: 700;")

        disc_lbl = QLabel("Discount:")
        disc_lbl.setStyleSheet(f"color: {t.text_secondary}; background: transparent;")

        totals_row.addWidget(self.subtotal_label)
        totals_row.addStretch()
        totals_row.addWidget(disc_lbl)
        totals_row.addWidget(self.discount_spin)
        totals_row.addWidget(self.discount_type_combo)
        totals_row.addSpacing(t.spacing_xl)
        totals_row.addWidget(self.grand_total_label)
        footer_vbox.addLayout(totals_row)

        # -- Payment section --
        self._payment_section = QWidget()
        self._payment_section.setStyleSheet("background: transparent;")
        payment_vbox = QVBoxLayout(self._payment_section)
        payment_vbox.setContentsMargins(0, 0, 0, 0)
        payment_vbox.setSpacing(t.spacing_sm)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet(f"color: {t.border};")
        payment_vbox.addWidget(sep1)

        # Payment Status
        status_row = QHBoxLayout()
        status_row.setSpacing(t.spacing_md)
        status_lbl = QLabel("Payment Status:")
        status_lbl.setStyleSheet(f"color: {t.text_secondary}; background: transparent;")
        
        self.payment_status_combo = QComboBox()
        self.payment_status_combo.addItem("Paid in Full",    "paid_in_full")
        self.payment_status_combo.addItem("Partial Payment", "partial")
        self.payment_status_combo.addItem("Unpaid / Credit", "unpaid")
        self.payment_status_combo.currentIndexChanged.connect(self._on_payment_status_changed)
        status_row.addWidget(status_lbl)
        status_row.addWidget(self.payment_status_combo)
        status_row.addStretch()
        payment_vbox.addLayout(status_row)

        # Amount Paid (partial only)
        self._amount_paid_row = QWidget()
        self._amount_paid_row.setStyleSheet("background: transparent;")
        amt_row_layout = QHBoxLayout(self._amount_paid_row)
        amt_row_layout.setContentsMargins(0, 0, 0, 0)
        amt_row_layout.setSpacing(t.spacing_md)
        amt_lbl = QLabel("Amount Paid:")
        amt_lbl.setStyleSheet(f"color: {t.text_secondary}; background: transparent;")
        self.amount_paid_spin = QDoubleSpinBox()
        self.amount_paid_spin.setDecimals(2)
        self.amount_paid_spin.setRange(0, 0)
        self.amount_paid_spin.setFixedWidth(140)
        self.amount_paid_spin.valueChanged.connect(self._on_amount_paid_changed)
        amt_row_layout.addWidget(amt_lbl)
        amt_row_layout.addWidget(self.amount_paid_spin)
        amt_row_layout.addStretch()
        payment_vbox.addWidget(self._amount_paid_row)
        self._amount_paid_row.hide()

        # Remaining Balance
        self._remaining_row = QWidget()
        self._remaining_row.setStyleSheet("background: transparent;")
        rem_row_layout = QHBoxLayout(self._remaining_row)
        rem_row_layout.setContentsMargins(0, 0, 0, 0)
        rem_row_layout.setSpacing(t.spacing_md)
        rem_lbl = QLabel("Remaining Balance:")
        rem_lbl.setStyleSheet(f"color: {t.text_secondary}; background: transparent;")
        self.remaining_lbl = QLabel("0.00")
        self.remaining_lbl.setStyleSheet(f"font-weight: 700; font-size: {t.size_section}pt; color: {t.text_primary}; background: transparent;")
        rem_row_layout.addWidget(rem_lbl)
        rem_row_layout.addWidget(self.remaining_lbl)
        rem_row_layout.addStretch()
        payment_vbox.addWidget(self._remaining_row)
        self._remaining_row.hide()

        footer_vbox.addWidget(self._payment_section)
        self._payment_section.hide()

        # -- Action buttons --
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"color: {t.border};")
        footer_vbox.addWidget(sep2)

        self.clear_btn = QPushButton("🧹 Clear Invoice")
        self.clear_btn.setProperty("class", "destructive")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        
        self.save_btn = QPushButton("💾 Save Invoice")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setMinimumWidth(150)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(t.spacing_md)
        buttons_row.addStretch()
        buttons_row.addWidget(self.clear_btn)
        buttons_row.addWidget(self.save_btn)
        footer_vbox.addLayout(buttons_row)

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

    def _compute_invoice_total(self) -> float:
        subtotal  = sum(item["subtotal"] for item in self._items)
        disc_type = self.discount_type_combo.currentText()
        disc_val  = self.discount_spin.value()
        discount  = round(subtotal * disc_val / 100, 2) if disc_type == "%" else disc_val
        return max(0.0, round(subtotal - discount, 2))

    def _update_totals(self):
        subtotal = self._get_subtotal()
        discount = self._discount_amount()
        grand_total = max(0.0, subtotal - discount)
        self.subtotal_label.setText(f"Subtotal: {_fmt_total(subtotal)}")
        self.grand_total_label.setText(f"Grand Total: {_fmt_total(grand_total)}")
        if discount > subtotal:
            self.discount_spin.setStyleSheet("QDoubleSpinBox { border: 2px solid red; }")
        else:
            self.discount_spin.setStyleSheet("")

        has_payable = len(self._items) > 0 and grand_total > 0
        self._payment_section.setVisible(has_payable)
        if has_payable:
            self._refresh_payment_section()

    def _refresh_payment_section(self):
        status = self.payment_status_combo.currentData()
        grand_total = self._compute_invoice_total()

        if status == "paid_in_full":
            self._amount_paid_row.hide()
            self._remaining_row.hide()
        elif status == "partial":
            self.amount_paid_spin.setRange(0, grand_total)
            self._amount_paid_row.show()
            remaining = max(0.0, round(grand_total - self.amount_paid_spin.value(), 2))
            self.remaining_lbl.setText(f"{remaining:,.2f}")
            self._remaining_row.show()
        else:  # unpaid / credit
            self._amount_paid_row.hide()
            self.remaining_lbl.setText(f"{grand_total:,.2f}")
            self._remaining_row.show()

    def _rebuild_table(self):
        self.table.setRowCount(0)
        t = theme._active
        for idx, item in enumerate(self._items):
            r = self.table.rowCount()
            self.table.insertRow(r)

            def _item(text):
                it = QTableWidgetItem(text)
                it.setToolTip(text)
                return it

            name_item = _item(item["product_name"])
            name_item.setFont(QFont(t.font_family, t.size_normal, QFont.Bold))
            
            self.table.setItem(r, 0, name_item)
            self.table.setItem(r, 1, _item(_fmt(item["quantity"])))
            self.table.setItem(r, 2, _item(_fmt(item["unit_price"])))
            
            subtotal_item = _item(_fmt(item["subtotal"]))
            subtotal_item.setFont(QFont(t.font_family, t.size_normal, QFont.Bold))
            self.table.setItem(r, 3, subtotal_item)
            
            cell_widget = QWidget()
            btn_layout = QHBoxLayout(cell_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            remove_btn = QPushButton("❌ Remove")
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet(
                f"QPushButton {{ background-color: {t.surface_alt}; color: {t.error};"
                f" border: 1px solid {t.border}; border-radius: 6px; padding: 4px 8px; font-weight: 500; }}"
                f"QPushButton:hover {{ background-color: {t.error}; color: white; border: none; }}"
            )
            remove_btn.clicked.connect(
                lambda checked=False, i=idx: self._on_remove_line(i))
            btn_layout.addWidget(remove_btn)
            self.table.setCellWidget(r, 4, cell_widget)
            
        has_rows = self.table.rowCount() > 0
        self.table.setVisible(has_rows)
        self._empty_table_lbl.setVisible(not has_rows)

    def _reset_form(self):
        self._items = []
        self._refresh_customer_combo()
        self.payment_status_combo.blockSignals(True)
        self.payment_status_combo.setCurrentIndex(0)
        self.payment_status_combo.blockSignals(False)
        self._customer_label.setText("Customer (Optional):")
        self._amount_paid_row.hide()
        self._remaining_row.hide()
        self._payment_section.hide()
        self.discount_type_combo.setCurrentIndex(0)
        self.discount_spin.setRange(0, 9_999_999)
        self.discount_spin.setValue(0.0)
        self.discount_spin.setStyleSheet("")
        self._rebuild_table()
        self._update_totals()
        self._refresh_invoice_number()

    def _refresh_customer_combo(self):
        self.customer_combo.blockSignals(True)
        self.customer_combo.clear()
        self._customer_data = get_all_customers_for_selector()
        self.customer_combo.addItem("(Select or add customer)", None)
        for c in self._customer_data:
            label = c["name"] + (f"  [{c['phone']}]" if c["phone"] else "")
            self.customer_combo.addItem(label, c["id"])
        self.customer_combo.addItem("＋ Add New Customer…", "ADD_NEW")
        self.customer_combo.blockSignals(False)
        self._selected_customer_id = None

    def _on_customer_selected(self, index):
        data = self.customer_combo.itemData(index)
        if data == "ADD_NEW":
            self._add_new_customer()
        else:
            self._selected_customer_id = data

    def _add_new_customer(self):
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout as _QFL2
        dlg = QDialog(self)
        dlg.setWindowTitle("Add New Customer")
        dlg.setStyleSheet(f"background-color: {theme._active.surface}; color: {theme._active.text_primary};")
        lay = _QFL2(dlg)
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

    def _resolve_customer(self) -> tuple:
        idx = self.customer_combo.currentIndex()
        if idx > 0:
            data = self.customer_combo.itemData(idx)
            if isinstance(data, int):
                for c in self._customer_data:
                    if c["id"] == data:
                        self._selected_customer_id = data
                        return data, c["name"]

        typed = self.customer_combo.currentText().strip()
        if not typed or typed in ("(Select or add customer)", "＋ Add New Customer…"):
            return None, ""

        for c in self._customer_data:
            label = c["name"] + (f"  [{c['phone']}]" if c["phone"] else "")
            if typed.lower() in (c["name"].lower(), label.lower()):
                self._selected_customer_id = c["id"]
                return c["id"], c["name"]

        return None, typed

    def _on_payment_status_changed(self, _index):
        self._refresh_payment_section()
        self._update_customer_label()

    def _update_customer_label(self):
        status = self.payment_status_combo.currentData()
        if status == "paid_in_full":
            self._customer_label.setText("Customer (Optional):")
        else:
            self._customer_label.setText("Customer (Required):")

    def _on_amount_paid_changed(self, value):
        total = self._compute_invoice_total()
        remaining = max(0.0, round(total - value, 2))
        self.remaining_lbl.setText(f"{remaining:,.2f}")

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

        payment_status = self.payment_status_combo.currentData()
        customer_id, customer_name = self._resolve_customer()

        if payment_status in ("partial", "unpaid"):
            if customer_id is None and customer_name:
                answer = QMessageBox.question(
                    self, "New Customer",
                    f'"{customer_name}" is not in your customer list.\n'
                    "Create this customer and save the invoice?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
                )
                if answer != QMessageBox.Yes:
                    return
                try:
                    customer_id = create_customer(customer_name, "")
                    self._refresh_customer_combo()
                except ValueError as e:
                    QMessageBox.warning(self, "Validation Error", str(e))
                    return
            elif customer_id is None:
                QMessageBox.warning(self, "Missing Customer",
                    "Customer is required when the invoice has an outstanding balance.")
                return

        partial_amount = self.amount_paid_spin.value() if payment_status == "partial" else 0.0

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            invoice_number = sales_logic.save_sale_with_customer(
                customer_name, customer_id,
                discount, self._items, payment_status, partial_amount
            )
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
        self._reload_products()
        self._refresh_customer_combo()
