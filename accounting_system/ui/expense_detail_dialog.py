from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from logic import expenses_logic
from ui import theme


class ExpenseDetailDialog(QDialog):
    def __init__(self, invoice_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Expense Invoice Detail")
        self.setMinimumWidth(580)
        invoice = expenses_logic.get_expense_invoice_by_id(invoice_id)
        items = expenses_logic.get_expense_items_by_invoice(invoice_id)
        self._build_ui(invoice, items)

    def _build_ui(self, invoice, items):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_xl,
            theme._active.spacing_xl, theme._active.spacing_xl)
        layout.setSpacing(theme._active.spacing_lg)

        # Dialog title
        title_lbl = QLabel("Expense Invoice")
        title_font = QFont(theme._active.font_family, theme._active.size_page_title)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(
            f"color: {theme._active.text_primary}; background: transparent;")
        layout.addWidget(title_lbl)

        def lbl(text: str) -> QLabel:
            l = QLabel(text)
            l.setTextInteractionFlags(Qt.TextSelectableByMouse)
            l.setStyleSheet("background: transparent;")
            return l

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
        if invoice:
            inv_num_lbl = lbl(invoice["invoice_number"] or "")
            inv_num_lbl.setStyleSheet(
                f"font-weight: bold; color: {theme._active.primary}; background: transparent;")
            form.addRow("Invoice #:",    inv_num_lbl)
            form.addRow("Date & Time:", lbl(invoice["expense_datetime"] or ""))
            total_lbl = lbl(f"{float(invoice['total_amount']):,.2f}")
            total_lbl.setStyleSheet(
                f"font-weight: bold; color: {theme._active.primary}; background: transparent;")
            form.addRow("Total Amount:", total_lbl)
        else:
            form.addRow(QLabel("Invoice not found."))
        hc_layout.addLayout(form)
        hc_layout.addStretch()
        layout.addWidget(header_card)

        # Line items table
        if items:
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(
                ["Category", "Description", "Amount", "Notes"])
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.setColumnWidth(0, 130)
            table.setColumnWidth(2, 100)
            table.setColumnWidth(3, 130)
            table.setStyleSheet(
                f"QTableWidget {{ border-radius: {theme._active.card_border_radius}px;"
                f" border: 1px solid {theme._active.border}; }}")
            theme.apply_table_style(table)
            for row in items:
                r = table.rowCount()
                table.insertRow(r)

                def _item(text):
                    it = QTableWidgetItem(text)
                    it.setToolTip(text)
                    return it

                table.setItem(r, 0, _item(row["category"] or ""))
                table.setItem(r, 1, _item(row["description"] or ""))
                table.setItem(r, 2, _item(f"{float(row['amount']):,.2f}"))
                table.setItem(r, 3, _item(row["notes"] or ""))
            layout.addWidget(table)

        btn_row = QHBoxLayout()
        close_btn = QPushButton("Close")
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        close_btn.clicked.connect(self.reject)
        layout.addLayout(btn_row)
