import traceback

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QApplication,
)
from PySide6.QtCore import Qt
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter, QFont

import sales_db
import purchases_db
from logic import sales_logic, purchase_logic
from ui import theme


class InvoiceDetailDialog(QDialog):
    def __init__(self, invoice_type: str, invoice_id: int, parent=None):
        super().__init__(parent)
        self._invoice_type = invoice_type
        self._invoice_id = invoice_id
        self.setModal(True)
        self.setMinimumWidth(750)
        label = "Sale Invoice Detail" if invoice_type == "sale" else "Purchase Invoice Detail"
        self.setWindowTitle(label)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_xl,
            theme._active.spacing_xl, theme._active.spacing_xl)
        layout.setSpacing(theme._active.spacing_lg)

        # Dialog title
        type_label = "Sales Invoice" if self._invoice_type == "sale" else "Purchase Invoice"
        title_lbl = QLabel(type_label)
        title_font = QFont(theme._active.font_family, theme._active.size_page_title)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(
            f"color: {theme._active.text_primary}; background: transparent;")
        layout.addWidget(title_lbl)

        # Header card
        header_card = QFrame()
        header_card.setStyleSheet(
            f"QFrame {{ background-color: {theme._active.surface};"
            f" border: 1px solid {theme._active.border};"
            f" border-radius: {theme._active.card_border_radius}px; }}")
        hc_layout = QHBoxLayout(header_card)
        hc_layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_lg,
            theme._active.spacing_xl, theme._active.spacing_lg)

        form = QFormLayout()
        form.setSpacing(theme._active.spacing_sm)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.invoice_number_label = QLabel()
        self.invoice_number_label.setStyleSheet(
            f"font-weight: bold; color: {theme._active.primary}; background: transparent;")
        self.date_label   = QLabel()
        self.date_label.setStyleSheet("background: transparent;")
        self.status_label = QLabel()
        self.status_label.setStyleSheet("background: transparent;")
        self.party_label  = QLabel()
        self.party_label.setStyleSheet("background: transparent;")

        party_title = "Customer" if self._invoice_type == "sale" else "Supplier"
        form.addRow("Invoice #:", self.invoice_number_label)
        form.addRow("Date & Time:", self.date_label)
        form.addRow("Status:",    self.status_label)
        form.addRow(f"{party_title}:", self.party_label)
        hc_layout.addLayout(form)
        hc_layout.addStretch()
        layout.addWidget(header_card)

        # Line-items table
        if self._invoice_type == "sale":
            cols = ["Product", "Qty", "Unit Price", "Cost Price", "Profit / Line", "Subtotal"]
        else:
            cols = ["Product", "Qty", "Unit Price", "Subtotal"]
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(len(cols))
        self.items_table.setHorizontalHeaderLabels(cols)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        if self._invoice_type == "sale":
            # Qty, Unit Price, Cost Price, Profit / Line, Subtotal
            for col, w in [(1, 60), (2, 95), (3, 95), (4, 105), (5, 90)]:
                self.items_table.setColumnWidth(col, w)
        else:
            # Qty, Unit Price, Subtotal
            for col, w in [(1, 60), (2, 95), (3, 90)]:
                self.items_table.setColumnWidth(col, w)
        self.items_table.setStyleSheet(
            f"QTableWidget {{ border-radius: {theme._active.card_border_radius}px;"
            f" border: 1px solid {theme._active.border}; }}")
        theme.apply_table_style(self.items_table)
        layout.addWidget(self.items_table)

        # Footer card
        footer_card = QFrame()
        footer_card.setStyleSheet(
            f"QFrame {{ background-color: {theme._active.surface};"
            f" border: 1px solid {theme._active.border};"
            f" border-radius: {theme._active.card_border_radius}px; }}")
        footer_layout = QHBoxLayout(footer_card)
        footer_layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_md,
            theme._active.spacing_xl, theme._active.spacing_md)
        footer_layout.setSpacing(theme._active.spacing_md)

        self.footer_label = QLabel()
        total_font = QFont(theme._active.font_family, theme._active.size_heading)
        total_font.setBold(True)
        self.footer_label.setFont(total_font)
        self.footer_label.setStyleSheet("background: transparent;")

        self.void_btn  = QPushButton("Void Invoice")
        self.void_btn.setProperty("class", "destructive")
        self.print_btn = QPushButton("Print")
        close_btn      = QPushButton("Close")

        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.void_btn)
        footer_layout.addWidget(self.print_btn)
        footer_layout.addWidget(close_btn)
        layout.addWidget(footer_card)

        close_btn.clicked.connect(self.accept)
        self.void_btn.clicked.connect(self._on_void)
        self.print_btn.clicked.connect(self._on_print)

    def _load_data(self):
        if self._invoice_type == "sale":
            header = sales_db.get_sale_by_id(self._invoice_id)
            if header is None:
                QMessageBox.critical(self, "Error", "Sale invoice not found.")
                self.reject()
                return
            items = sales_db.get_sale_items(self._invoice_id)
            self.invoice_number_label.setText(header["invoice_number"] or "")
            self.date_label.setText((header["created_at"] or "")[:16])
            self.status_label.setText(header["status"] or "")
            self.party_label.setText(header["customer_name"] or "—")

            self.items_table.setRowCount(0)
            subtotal_sum = 0.0
            for item in items:
                r = self.items_table.rowCount()
                self.items_table.insertRow(r)
                cost = item["purchase_price_at_sale"]
                profit_per_line = round((item["unit_price"] - cost) * item["quantity"], 2)
                name = item["product_name"] or ""
                name_it = QTableWidgetItem(name)
                name_it.setToolTip(name)
                self.items_table.setItem(r, 0, name_it)
                self.items_table.setItem(r, 1, QTableWidgetItem(str(item["quantity"])))
                self.items_table.setItem(r, 2, QTableWidgetItem(f"{item['unit_price']:,.2f}"))
                self.items_table.setItem(r, 3, QTableWidgetItem(f"{cost:,.2f}"))
                self.items_table.setItem(r, 4, QTableWidgetItem(f"{profit_per_line:,.2f}"))
                self.items_table.setItem(r, 5, QTableWidgetItem(f"{item['subtotal']:,.2f}"))
                subtotal_sum += item["subtotal"]

            discount = header["discount_amount"] or 0.0
            grand_total = header["total_amount"] or 0.0
            self.footer_label.setText(
                f"Subtotal: {subtotal_sum:,.2f}   "
                f"Discount: {discount:,.2f}   "
                f"Grand Total: {grand_total:,.2f}"
            )
            self.footer_label.setStyleSheet(
                f"font-weight: bold; background: transparent;"
                f" color: {theme.color_for_value(grand_total - discount)};")
            self.void_btn.setEnabled(header["status"] == "active")

        else:  # purchase
            header = purchases_db.get_purchase_by_id(self._invoice_id)
            if header is None:
                QMessageBox.critical(self, "Error", "Purchase invoice not found.")
                self.reject()
                return
            items = purchases_db.get_purchase_items(self._invoice_id)
            self.invoice_number_label.setText(header["invoice_number"] or "")
            self.date_label.setText((header["created_at"] or "")[:16])
            self.status_label.setText(header["status"] or "")
            self.party_label.setText(header["supplier_name"] or "—")

            self.items_table.setRowCount(0)
            for item in items:
                r = self.items_table.rowCount()
                self.items_table.insertRow(r)
                name = item["product_name"] or ""
                name_it = QTableWidgetItem(name)
                name_it.setToolTip(name)
                self.items_table.setItem(r, 0, name_it)
                self.items_table.setItem(r, 1, QTableWidgetItem(str(item["quantity"])))
                self.items_table.setItem(r, 2, QTableWidgetItem(f"{item['unit_price']:,.2f}"))
                self.items_table.setItem(r, 3, QTableWidgetItem(f"{item['subtotal']:,.2f}"))

            grand_total = header["total_amount"] or 0.0
            self.footer_label.setText(f"Grand Total: {grand_total:,.2f}")
            self.void_btn.setEnabled(header["status"] == "active")

    def _on_void(self):
        inv_num = self.invoice_number_label.text()
        answer = QMessageBox.question(
            self, "Confirm Void",
            f"Are you sure you want to void invoice {inv_num}?\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self._invoice_type == "sale":
                sales_logic.void_sale(self._invoice_id)
            else:
                purchase_logic.void_purchase(self._invoice_id)
            QApplication.restoreOverrideCursor()
            self.void_btn.setEnabled(False)
            self.status_label.setText("voided")
            QMessageBox.information(self, "Voided", "Invoice voided successfully.")
        except ValueError as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Cannot Void", str(e))
        except Exception:
            QApplication.restoreOverrideCursor()
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error",
                "An unexpected error occurred while voiding the invoice.")

    def _on_print(self):
        printer = QPrinter(QPrinter.HighResolution)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        dialog = QPrintDialog(printer, self)
        QApplication.restoreOverrideCursor()
        if dialog.exec() == QPrintDialog.Accepted:
            try:
                painter = QPainter(printer)
                self.render(painter)
                painter.end()
            except Exception:
                print(traceback.format_exc())
                QMessageBox.critical(self, "Print Error",
                    "An error occurred while printing.")
