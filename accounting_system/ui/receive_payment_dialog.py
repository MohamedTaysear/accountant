import traceback

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel,
    QDoubleSpinBox, QLineEdit, QDialogButtonBox, QMessageBox, QApplication,
)
from PySide6.QtCore import Qt

from logic import customers_logic
from ui import theme


class ReceivePaymentDialog(QDialog):
    """Collect a customer payment and allocate it across outstanding invoices via FIFO."""

    def __init__(self, customer_id: int, customer_name: str, outstanding: float, parent=None):
        super().__init__(parent)
        self._customer_id = customer_id
        self._outstanding = round(outstanding, 2)
        self.setWindowTitle(f"Receive Payment — {customer_name}")
        self.setMinimumWidth(440)
        self._build_ui(customer_name)

    def _build_ui(self, customer_name: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        customer_lbl = QLabel(customer_name)
        customer_lbl.setStyleSheet(
            f"font-weight: bold; background: transparent;"
            f" color: {theme._active.text_primary};")
        form.addRow("Customer:", customer_lbl)

        outstanding_lbl = QLabel(f"{self._outstanding:,.2f}")
        outstanding_lbl.setStyleSheet(
            f"font-weight: bold; font-size: {theme._active.size_heading}pt;"
            f" color: {theme._active.primary}; background: transparent;")
        form.addRow("Outstanding Balance:", outstanding_lbl)

        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setDecimals(2)
        self.amount_spin.setRange(0.01, self._outstanding)
        self.amount_spin.setValue(self._outstanding)
        self.amount_spin.setFixedWidth(160)
        self.amount_spin.valueChanged.connect(self._on_amount_changed)
        form.addRow("Amount Received:", self.amount_spin)

        self.remaining_lbl = QLabel("0.00")
        self.remaining_lbl.setStyleSheet(
            f"background: transparent; color: {theme._active.text_secondary};")
        form.addRow("Remaining After Payment:", self.remaining_lbl)

        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional")
        form.addRow("Notes:", self.notes_edit)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Receive Payment")
        btns.accepted.connect(self._on_confirm)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._on_amount_changed(self._outstanding)

    def _on_amount_changed(self, value: float):
        remaining = max(0.0, round(self._outstanding - value, 2))
        self.remaining_lbl.setText(f"{remaining:,.2f}")

    def _on_confirm(self):
        amount = self.amount_spin.value()
        notes  = self.notes_edit.text().strip()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            customers_logic.receive_payment_fifo(self._customer_id, amount, notes)
            QApplication.restoreOverrideCursor()
            QMessageBox.information(
                self, "Payment Recorded",
                f"Payment of {amount:,.2f} recorded successfully.")
            self.accept()
        except ValueError as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception:
            QApplication.restoreOverrideCursor()
            traceback.print_exc()
            QMessageBox.critical(self, "Error",
                "An unexpected error occurred. Payment was not recorded.")
