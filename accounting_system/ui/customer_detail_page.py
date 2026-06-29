import traceback

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QTabWidget, QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from logic import customers_logic
from ui import theme


def _make_card(title: str, value_lbl: QLabel) -> QFrame:
    frame = QFrame()
    frame.setStyleSheet(
        f"QFrame {{ background-color: {theme._active.surface};"
        f" border: 1px solid {theme._active.border};"
        f" border-radius: {theme._active.card_border_radius}px; }}")
    frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(
        theme._active.spacing_lg, theme._active.spacing_md,
        theme._active.spacing_lg, theme._active.spacing_md)
    lay.setSpacing(4)
    t = QLabel(title)
    t.setAlignment(Qt.AlignCenter)
    t.setStyleSheet(
        f"background: transparent; border: none;"
        f" font-size: {theme._active.size_kpi_label}pt;"
        f" color: {theme._active.text_secondary}; font-weight: bold;")
    value_lbl.setAlignment(Qt.AlignCenter)
    value_lbl.setStyleSheet(
        f"background: transparent; border: none;"
        f" font-size: {theme._active.size_kpi_value}pt;"
        f" font-weight: bold; color: {theme._active.text_primary};")
    lay.addWidget(t)
    lay.addWidget(value_lbl)
    return frame


STATUS_COLORS = {
    "Paid":           "#27ae60",
    "Partially Paid": "#e67e22",
    "Unpaid":         "#e74c3c",
    "Voided":         "#95a5a6",
}


class CustomerDetailPage(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._customer_id = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_xl,
            theme._active.spacing_xl, theme._active.spacing_xl)
        layout.setSpacing(theme._active.spacing_lg)

        top = QHBoxLayout()
        back_btn = QPushButton("← Back to Customers")
        back_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none;"
            f" color: {theme._active.primary}; font-size: {theme._active.size_normal}pt; }}"
            f"QPushButton:hover {{ text-decoration: underline; }}")
        back_btn.clicked.connect(self.back_requested.emit)
        top.addWidget(back_btn)
        top.addStretch()
        self.receive_btn = QPushButton("Receive Payment")
        self.receive_btn.setProperty("class", "primary")
        self.receive_btn.clicked.connect(self._on_receive_payment)
        self.receive_btn.hide()
        top.addWidget(self.receive_btn)
        layout.addLayout(top)

        self.name_lbl = QLabel("")
        fn = QFont(theme._active.font_family, theme._active.size_page_title)
        fn.setBold(True)
        self.name_lbl.setFont(fn)
        self.name_lbl.setStyleSheet(f"color: {theme._active.text_primary}; background: transparent;")
        layout.addWidget(self.name_lbl)

        self.phone_lbl = QLabel("")
        self.phone_lbl.setStyleSheet(f"color: {theme._active.text_secondary}; background: transparent;")
        layout.addWidget(self.phone_lbl)

        cards = QHBoxLayout()
        self.balance_lbl   = QLabel("0.00")
        self.purchases_lbl = QLabel("0.00")
        self.paid_lbl      = QLabel("0.00")
        self.count_lbl     = QLabel("0")
        cards.addWidget(_make_card("Outstanding Balance", self.balance_lbl))
        cards.addWidget(_make_card("Total Purchases",     self.purchases_lbl))
        cards.addWidget(_make_card("Total Paid",          self.paid_lbl))
        cards.addWidget(_make_card("Invoices",            self.count_lbl))
        layout.addLayout(cards)

        tabs = QTabWidget()

        self.inv_table = QTableWidget()
        self.inv_table.setColumnCount(6)
        self.inv_table.setHorizontalHeaderLabels(
            ["Invoice #", "Date", "Total", "Paid", "Remaining", "Status"])
        self.inv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.inv_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.inv_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        for col in [2, 3, 4]:
            self.inv_table.setColumnWidth(col, 110)
        self.inv_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inv_table.setSelectionBehavior(QTableWidget.SelectRows)
        theme.apply_table_style(self.inv_table)
        tabs.addTab(self.inv_table, "Invoices")

        self.pay_table = QTableWidget()
        self.pay_table.setColumnCount(5)
        self.pay_table.setHorizontalHeaderLabels(
            ["Date", "Invoice #", "Amount", "Remaining After", "Notes"])
        self.pay_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.pay_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.pay_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        for col in [2, 3]:
            self.pay_table.setColumnWidth(col, 120)
        self.pay_table.setEditTriggers(QTableWidget.NoEditTriggers)
        theme.apply_table_style(self.pay_table)
        tabs.addTab(self.pay_table, "Payment History")

        layout.addWidget(tabs)

    def load_customer(self, customer_id: int):
        self._customer_id = customer_id
        self._refresh()

    def _refresh(self):
        if self._customer_id is None:
            return
        try:
            profile = customers_logic.get_customer_profile(self._customer_id)
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", "Failed to load customer profile.")
            return

        c = profile["customer"]
        self.name_lbl.setText(c["name"])
        self.phone_lbl.setText(c.get("phone") or "")
        self.balance_lbl.setText(f"{profile['outstanding_balance']:,.2f}")
        self.purchases_lbl.setText(f"{profile['total_purchases']:,.2f}")
        self.paid_lbl.setText(f"{profile['total_paid']:,.2f}")
        self.count_lbl.setText(str(profile["invoice_count"]))

        self.receive_btn.setVisible(profile["outstanding_balance"] > 0)

        self.inv_table.setRowCount(len(profile["invoices"]))
        for row, inv in enumerate(profile["invoices"]):
            status = inv["payment_status"]
            color  = STATUS_COLORS.get(status, theme._active.text_primary)
            for col, text in enumerate([
                inv["invoice_number"],
                inv["created_at"][:10],
                f"{inv['total_amount']:,.2f}",
                f"{inv['total_paid']:,.2f}",
                f"{inv['remaining']:,.2f}",
                status,
            ]):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 5:
                    item.setForeground(QColor(color))
                self.inv_table.setItem(row, col, item)

        self.pay_table.setRowCount(len(profile["payments"]))
        for row, pay in enumerate(profile["payments"]):
            for col, text in enumerate([
                pay["payment_date"][:10],
                pay.get("invoice_number", ""),
                f"{pay['amount']:,.2f}",
                f"{pay['remaining_after']:,.2f}",
                pay.get("notes") or "",
            ]):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.pay_table.setItem(row, col, item)

    def _on_receive_payment(self):
        if self._customer_id is None:
            return
        try:
            profile = customers_logic.get_customer_profile(self._customer_id)
        except Exception:
            traceback.print_exc()
            return
        from ui.receive_payment_dialog import ReceivePaymentDialog
        dlg = ReceivePaymentDialog(
            self._customer_id,
            profile["customer"]["name"],
            parent=self
        )
        if dlg.exec():
            self._refresh()
