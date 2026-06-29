import traceback

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

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
        t = theme._active
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Left Branding Panel ──────────────────────────────────────
        brand_panel = QFrame()
        brand_panel.setStyleSheet(f"background-color: {t.primary};")
        brand_layout = QVBoxLayout(brand_panel)
        brand_layout.setContentsMargins(40, 40, 40, 40)
        
        logo_lbl = QLabel("💎")
        logo_lbl.setStyleSheet("font-size: 48pt; color: white; background: transparent;")
        
        brand_title = QLabel(config.APP_NAME)
        title_font = QFont(t.font_family, 28)
        title_font.setBold(True)
        brand_title.setFont(title_font)
        brand_title.setStyleSheet("color: white; background: transparent; font-weight: 700;")
        brand_title.setWordWrap(True)
        
        brand_subtitle = QLabel("The premium accounting and inventory management solution.")
        brand_subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 14pt; background: transparent;")
        brand_subtitle.setWordWrap(True)
        
        brand_layout.addStretch()
        brand_layout.addWidget(logo_lbl)
        brand_layout.addSpacing(16)
        brand_layout.addWidget(brand_title)
        brand_layout.addSpacing(16)
        brand_layout.addWidget(brand_subtitle)
        brand_layout.addStretch()
        
        # ── Right Login Panel ────────────────────────────────────────
        login_panel = QFrame()
        login_panel.setStyleSheet(f"background-color: {t.surface};")
        login_layout = QVBoxLayout(login_panel)
        login_layout.setContentsMargins(60, 60, 60, 60)
        login_layout.setAlignment(Qt.AlignCenter)
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(t.spacing_lg)
        form_container.setFixedWidth(360)
        
        welcome_lbl = QLabel("Welcome Back")
        welcome_font = QFont(t.font_family, 24)
        welcome_font.setBold(True)
        welcome_lbl.setFont(welcome_font)
        welcome_lbl.setStyleSheet(f"color: {t.text_primary}; background: transparent; font-weight: 700;")
        
        instruction_lbl = QLabel("Please enter your details to sign in.")
        instruction_lbl.setStyleSheet(f"color: {t.text_secondary}; font-size: 11pt; background: transparent;")
        
        form_layout.addWidget(welcome_lbl)
        form_layout.addWidget(instruction_lbl)
        form_layout.addSpacing(t.spacing_xl)
        
        # Username input
        user_lbl = QLabel("Username")
        user_lbl.setStyleSheet(f"color: {t.text_primary}; font-weight: 600; background: transparent;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(44)
        self.username_input.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 0 12px; font-size: 11pt; background: {t.background}; }}"
            f"QLineEdit:focus {{ border: 2px solid {t.primary}; background: {t.surface}; }}"
        )
        form_layout.addWidget(user_lbl)
        form_layout.addWidget(self.username_input)
        form_layout.addSpacing(t.spacing_md)
        
        # Password input
        pass_lbl = QLabel("Password")
        pass_lbl.setStyleSheet(f"color: {t.text_primary}; font-weight: 600; background: transparent;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(44)
        self.password_input.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 0 12px; font-size: 11pt; background: {t.background}; }}"
            f"QLineEdit:focus {{ border: 2px solid {t.primary}; background: {t.surface}; }}"
        )
        form_layout.addWidget(pass_lbl)
        form_layout.addWidget(self.password_input)
        
        form_layout.addSpacing(t.spacing_xl)
        
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setMinimumHeight(48)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet(
            f"QPushButton {{ background-color: {t.primary}; color: white; border: none; border-radius: 8px; font-size: 12pt; font-weight: 700; }}"
            f"QPushButton:hover {{ background-color: {t.primary_hover}; }}"
        )
        form_layout.addWidget(self.login_btn)
        
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet(
            f"color: {t.error}; background: transparent;"
            f" border: none; font-size: {t.size_small}pt; font-weight: 500;")
        self.error_label.hide()
        form_layout.addWidget(self.error_label)
        
        login_layout.addWidget(form_container)
        
        # Add to main layout (50/50 split)
        main_layout.addWidget(brand_panel, 1)
        main_layout.addWidget(login_panel, 1)

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
