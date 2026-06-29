import traceback

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox,
    QDoubleSpinBox, QLineEdit, QDialogButtonBox, QMessageBox, QApplication,
)
from PySide6.QtCore import Qt

from logic import customers_logic
from ui import theme


class ReceivePaymentDialog(QDialog):
    def __init__(self, customer_id: int, customer_name: str, parent=None):
        super().__init__(parent)
        self._customer_id = customer_id
        self._outstanding_invoices = []
        self.setWindowTitle(f"Receive Payment — {customer_name}")
        self.setMinimumWidth(420)
        self._load_invoices()
        self._build_ui()

    def _load_invoices(self):
        try:
            self._outstanding_invoices = customers_logic.get_outstanding_invoices_for_customer(
                self._customer_id
            )
        except Exception:
            traceback.print_exc()
            self._outstanding_invoices = []

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        if not self._outstanding_invoices:
            layout.addWidget(QLabel("No outstanding invoices for this customer."))
            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(self.reject)
            layout.addWidget(btns)
            return

        form = QFormLayout()
        form.setSpacing(10)

        self.invoice_combo = QComboBox()
        for inv in self._outstanding_invoices:
            label = f"{inv['invoice_number']} | {inv['created_at'][:10]} | Outstanding: {inv['remaining']:,.2f}"
            self.invoice_combo.addItem(label, userData=inv)
        self.invoice_combo.currentIndexChanged.connect(self._on_invoice_changed)
        form.addRow("Invoice:", self.invoice_combo)

        self.outstanding_lbl = QLabel("0.00")
        self.outstanding_lbl.setStyleSheet(
            f"font-weight: bold; font-size: {theme._active.size_heading}pt;"
            f" background: transparent;")
        form.addRow("Invoice Outstanding:", self.outstanding_lbl)

        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setDecimals(2)
        self.amount_spin.setFixedWidth(160)
        self.amount_spin.valueChanged.connect(self._on_amount_changed)
        form.addRow("Amount Received:", self.amount_spin)

        self.remaining_lbl = QLabel("0.00")
        self.remaining_lbl.setStyleSheet("background: transparent;")
        form.addRow("Remaining After Payment:", self.remaining_lbl)

        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional note")
        form.addRow("Notes:", self.notes_edit)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Confirm Payment")
        btns.accepted.connect(self._on_confirm)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._on_invoice_changed(0)

    def _current_invoice(self):
        return self.invoice_combo.currentData()

    def _on_invoice_changed(self, _index):
        inv = self._current_invoice()
        if not inv:
            return
        outstanding = inv["remaining"]
        self.outstanding_lbl.setText(f"{outstanding:,.2f}")
        self.amount_spin.setRange(0.01, outstanding)
        self.amount_spin.setValue(outstanding)
        self._on_amount_changed(outstanding)

    def _on_amount_changed(self, value):
        inv = self._current_invoice()
        if not inv:
            return
        remaining = max(0.0, round(inv["remaining"] - value, 2))
        self.remaining_lbl.setText(f"{remaining:,.2f}")

    def _on_confirm(self):
        inv    = self._current_invoice()
        amount = self.amount_spin.value()
        notes  = self.notes_edit.text().strip()
        if not inv:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            customers_logic.record_payment(
                self._customer_id, inv["id"], amount, notes
            )
            QApplication.restoreOverrideCursor()
            QMessageBox.information(
                self, "Payment Recorded",
                f"Payment of {amount:,.2f} recorded against {inv['invoice_number']}."
            )
            self.accept()
        except ValueError as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception:
            QApplication.restoreOverrideCursor()
            traceback.print_exc()
            QMessageBox.critical(self, "Error",
                "An unexpected error occurred. Payment was not recorded.")
