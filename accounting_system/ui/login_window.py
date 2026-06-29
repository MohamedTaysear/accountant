import traceback

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import config
import auth
from ui import theme


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(config.APP_NAME)
        self.setFixedSize(config.LOGIN_WINDOW_WIDTH, config.LOGIN_WINDOW_HEIGHT)
        self.setStyleSheet(f"background-color: {theme._active.background};")
        self.main_window = None
        self._build_ui()

    def _build_ui(self):
        # Outer layout — centers the card
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(0, 0, 0, 0)

        # Login card
        card = QFrame()
        card.setFixedWidth(340)
        card.setStyleSheet(
            f"QFrame {{ background-color: {theme._active.surface};"
            f" border: 1px solid {theme._active.border};"
            f" border-radius: {theme._active.card_border_radius + 4}px; }}")
        card.setGraphicsEffect(theme.make_card_shadow())

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            theme._active.spacing_xxl, theme._active.spacing_xxl,
            theme._active.spacing_xxl, theme._active.spacing_xxl)
        card_layout.setSpacing(theme._active.spacing_md)

        # App name / logo area
        title = QLabel(config.APP_NAME)
        title_font = QFont(theme._active.font_family, theme._active.size_page_title + 2)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {theme._active.primary}; background: transparent; border: none;")
        card_layout.addWidget(title)

        subtitle = QLabel("Sign in to your account")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"color: {theme._active.text_secondary};"
            f" font-size: {theme._active.size_small}pt;"
            f" background: transparent; border: none;")
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(theme._active.spacing_md)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(36)
        card_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(36)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(theme._active.spacing_sm)

        self.login_btn = QPushButton("Sign In")
        self.login_btn.setProperty("class", "primary")
        self.login_btn.setMinimumHeight(36)
        card_layout.addWidget(self.login_btn)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet(
            f"color: {theme._active.error}; background: transparent;"
            f" border: none; font-size: {theme._active.size_small}pt;")
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        outer.addWidget(card)

        self.login_btn.clicked.connect(self._on_login)
        self.password_input.returnPressed.connect(self._on_login)
        self.username_input.setFocus()

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        self.error_label.hide()
        try:
            if auth.check_login(username, password):
                self._open_main_window(username)
            else:
                self.error_label.setText("Invalid username or password.")
                self.error_label.show()
                self.password_input.clear()
        except Exception:
            print(traceback.format_exc())
            self.error_label.setText("An unexpected error occurred. Please try again.")
            self.error_label.show()

    def _open_main_window(self, username: str):
        from ui.main_window import MainWindow
        self.main_window = MainWindow(username)
        self.main_window.logged_out.connect(self._on_logged_out)
        self.main_window.show()
        self.hide()

    def _on_logged_out(self):
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.hide()
        self.username_input.setFocus()
        self.show()
