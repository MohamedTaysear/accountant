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
from logic import purchase_logic
from ui import theme


class PurchasesPage(QWidget):
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
        page_title = QLabel("🛒 New Purchase Invoice")
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
        hc_layout = QHBoxLayout(header_card)
        hc_layout.setContentsMargins(t.spacing_xl, t.spacing_md, t.spacing_xl, t.spacing_md)
        hc_layout.setSpacing(t.spacing_xxl)

        header_form = QFormLayout()
        header_form.setSpacing(t.spacing_md)
        header_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.invoice_number_label = QLabel("PUR-000001")
        self.invoice_number_label.setStyleSheet(
            f"font-weight: 700; font-size: {t.size_section}pt; color: {t.primary}; background: transparent;")
        header_form.addRow("Invoice #:", self.invoice_number_label)

        self.date_label = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
        self.date_label.setStyleSheet(f"background: transparent; color: {t.text_primary}; font-weight: 500;")
        header_form.addRow("Date:", self.date_label)

        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Optional supplier name")
        self.supplier_input.setMaximumWidth(280)
        self.supplier_input.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px 12px; background: {t.background}; }}"
            f"QLineEdit:focus {{ border-color: {t.primary}; }}"
        )
        header_form.addRow("Supplier:", self.supplier_input)

        hc_layout.addLayout(header_form)
        hc_layout.addStretch()
        header_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(header_card)

        # ── Add item row ─────────────────────────────────────────────
        add_card = QFrame()
        add_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        add_card.setGraphicsEffect(theme.make_card_shadow())
        add_layout = QHBoxLayout(add_card)
        add_layout.setContentsMargins(t.spacing_lg, t.spacing_md, t.spacing_lg, t.spacing_md)
        add_layout.setSpacing(t.spacing_md)
        add_layout.setAlignment(Qt.AlignVCenter)

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
        self.qty_spin.setFixedWidth(90)

        self.price_spin = _SpinBox()
        self.price_spin.setRange(0, 9_999_999)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(0.0)
        self.price_spin.setFixedWidth(110)

        self.add_line_btn = QPushButton("➕ Add to Invoice")
        self.add_line_btn.setProperty("class", "primary")
        self.add_line_btn.setCursor(Qt.PointingHandCursor)

        def _lbl(lbl_text):
            l = QLabel(lbl_text)
            l.setStyleSheet(f"color: {t.text_secondary}; background: transparent; font-weight: 500;")
            return l

        add_layout.addWidget(_lbl("Product:"))
        add_layout.addWidget(self.product_combo, 2)
        add_layout.addWidget(_lbl("Qty:"))
        add_layout.addWidget(self.qty_spin)
        add_layout.addWidget(_lbl("Unit Price:"))
        add_layout.addWidget(self.price_spin)
        add_layout.addWidget(self.add_line_btn)
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

        # ── Footer / totals ──────────────────────────────────────────
        footer_card = QFrame()
        footer_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        footer_card.setGraphicsEffect(theme.make_card_shadow())
        footer = QHBoxLayout(footer_card)
        footer.setContentsMargins(t.spacing_lg, t.spacing_lg, t.spacing_lg, t.spacing_lg)
        footer.setSpacing(t.spacing_md)

        self.total_label = QLabel("Total: 0.00")
        total_font = QFont(t.font_family, t.size_kpi_value)
        total_font.setBold(True)
        self.total_label.setFont(total_font)
        self.total_label.setStyleSheet(f"color: {t.primary}; background: transparent; font-weight: 700;")

        self.clear_btn = QPushButton("🧹 Clear Invoice")
        self.clear_btn.setProperty("class", "destructive")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn  = QPushButton("💾 Save Invoice")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setMinimumWidth(150)

        footer.addWidget(self.total_label)
        footer.addStretch()
        footer.addWidget(self.clear_btn)
        footer.addWidget(self.save_btn)
        footer_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(footer_card)
        layout.addStretch()

        # ── Signals ────────────────────────────────────────────────
        self.product_combo.currentIndexChanged.connect(self._on_product_selected)
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
        self.product_combo.blockSignals(True)
        self.product_combo.clear()
        try:
            rows = products_db.get_active_products()
            for row in rows:
                self.product_combo.addItem(
                    row["name"],
                    userData={"id": row["id"], "name": row["name"]}
                )
        except Exception:
            print(traceback.format_exc())
        self.product_combo.blockSignals(False)

    def _update_total_label(self):
        total = purchase_logic.calculate_total(self._items)
        self.total_label.setText(f"Total: {_fmt_total(total)}")

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
            
            self.table.setItem(r, 1, _item(_fmt(item['quantity'])))
            self.table.setItem(r, 2, _item(_fmt(item['unit_price'])))
            
            subtotal_item = _item(_fmt(item['subtotal']))
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
        self.supplier_input.clear()
        self.qty_spin.setValue(1.0)
        self.price_spin.setValue(0.0)
        self._rebuild_table()
        self._update_total_label()
        self._refresh_invoice_number()

    # ── Signal Handlers ────────────────────────────────────────────

    def _on_product_selected(self, index):
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
        super().showEvent(event)
        self._reload_products()
