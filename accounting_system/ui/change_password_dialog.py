import traceback

from PySide6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QFrame,
    QFormLayout, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import auth
from ui import theme


class ChangePasswordDialog(QDialog):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Change Password")
        self.setFixedWidth(400)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_xl,
            theme._active.spacing_xl, theme._active.spacing_xl)
        outer.setSpacing(theme._active.spacing_lg)

        title_lbl = QLabel("Change Password")
        title_font = QFont(theme._active.font_family, theme._active.size_heading)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(
            f"color: {theme._active.text_primary}; background: transparent;")
        outer.addWidget(title_lbl)

        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: {theme._active.surface};"
            f" border: 1px solid {theme._active.border};"
            f" border-radius: {theme._active.card_border_radius}px; }}")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_lg,
            theme._active.spacing_xl, theme._active.spacing_lg)

        self.current_password_input  = QLineEdit()
        self.new_password_input      = QLineEdit()
        self.confirm_password_input  = QLineEdit()
        self.current_password_input.setPlaceholderText("Enter current password")
        self.new_password_input.setPlaceholderText("Enter new password")
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        for field in (
            self.current_password_input,
            self.new_password_input,
            self.confirm_password_input,
        ):
            field.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.setSpacing(theme._active.spacing_md)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.addRow("Current Password:",     self.current_password_input)
        form.addRow("New Password:",         self.new_password_input)
        form.addRow("Confirm Password:",     self.confirm_password_input)
        card_layout.addLayout(form)
        outer.addWidget(card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(theme._active.spacing_md)
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn   = QPushButton("Change Password")
        self.save_btn.setProperty("class", "primary")
        btn_row.addStretch()
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.save_btn)
        outer.addLayout(btn_row)

        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.reject)

    def _on_save(self):
        current = self.current_password_input.text()
        new_pw  = self.new_password_input.text()
        confirm = self.confirm_password_input.text()
        try:
            success, message = auth.change_password(
                self.username, current, new_pw, confirm
            )
            if success:
                QMessageBox.information(self, "Success", "Password changed successfully.")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception:
            print(traceback.format_exc())
            QMessageBox.critical(
                self, "Unexpected Error",
                "An unexpected error occurred. Please try again."
            )
