import os
import traceback

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QPushButton, QApplication, QMessageBox,
    QMenu, QFileDialog, QFrame, QLabel,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon, QFont

from ui import theme

import config
import database
from ui.dashboard_page       import DashboardPage
from ui.products_page        import ProductsPage
from ui.sales_page           import SalesPage
from ui.purchases_page       import PurchasesPage
from ui.reports_page         import ReportsPage
from ui.expenses_page        import ExpensesPage


class MainWindow(QMainWindow):
    logged_out = Signal()

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle(config.APP_NAME)
        self.setMinimumSize(config.MAIN_WINDOW_MIN_WIDTH, config.MAIN_WINDOW_MIN_HEIGHT)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(theme._active.sidebar_width)
        sidebar.setStyleSheet(f"background-color: {theme._active.nav_bg};")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App name header
        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"background-color: {theme._active.nav_bg};"
            f" border-bottom: 1px solid rgba(255,255,255,0.08);")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 16, 16, 16)
        app_name_lbl = QLabel(config.APP_NAME)
        app_name_font = QFont(theme._active.font_family, 11)
        app_name_font.setBold(True)
        app_name_lbl.setFont(app_name_font)
        app_name_lbl.setStyleSheet(
            "color: white; background: transparent; border: none;")
        app_name_lbl.setWordWrap(True)
        header_layout.addWidget(app_name_lbl)
        sidebar_layout.addWidget(header_frame)

        # Navigation section
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(8, 12, 8, 12)
        nav_layout.setSpacing(2)

        _icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        nav_buttons = [
            ("Dashboard",  0, "dashboard.svg"),
            ("Products",   1, "products.svg"),
            ("Sales",      2, "sales.svg"),
            ("Purchases",  3, "purchases.svg"),
            ("Expenses",   4, "expenses.svg"),
            ("Reports",    5, "reports.svg"),
        ]
        self._nav_btns = []
        for label, idx, icon_file in nav_buttons:
            btn = QPushButton(f"  {label}")
            icon_path = os.path.join(_icons_dir, icon_file)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            btn.setStyleSheet(self._nav_btn_normal_style())
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            nav_layout.addWidget(btn)
            self._nav_btns.append(btn)

        sidebar_layout.addWidget(nav_widget)
        sidebar_layout.addStretch()

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.08); border: none;")
        sep.setFixedHeight(1)
        sidebar_layout.addWidget(sep)

        # Bottom utility buttons
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background: transparent;")
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(8, 8, 8, 12)
        bottom_layout.setSpacing(2)

        for label, slot in [("Change Password", self._on_change_password),
                             ("Logout",          self._on_logout)]:
            btn = QPushButton(f"  {label}")
            btn.setStyleSheet(self._utility_btn_style())
            btn.setMinimumHeight(36)
            btn.clicked.connect(slot)
            bottom_layout.addWidget(btn)

        backup_btn = QPushButton("  Backup & Restore")
        backup_btn.setStyleSheet(self._utility_btn_style())
        backup_btn.setMinimumHeight(36)
        backup_menu = QMenu(backup_btn)
        backup_menu.setStyleSheet(
            f"QMenu {{ background-color: white; border: 1px solid {theme._active.border};"
            f" border-radius: 6px; padding: 4px; }}"
            f"QMenu::item {{ padding: 6px 20px; color: {theme._active.text_primary}; }}"
            f"QMenu::item:selected {{ background-color: {theme._active.primary}; color: white; }}")
        backup_menu.addAction(QAction("Create Backup…", self,
                                      triggered=self._on_create_backup))
        backup_menu.addAction(QAction("Restore Backup…", self,
                                      triggered=self._on_restore_backup))
        backup_btn.setMenu(backup_menu)
        bottom_layout.addWidget(backup_btn)

        sidebar_layout.addWidget(bottom_widget)

        # ── Page stack ─────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.dashboard_page  = DashboardPage()
        self.products_page   = ProductsPage()
        self.stack.addWidget(self.dashboard_page)   # 0
        self.stack.addWidget(self.products_page)    # 1
        self.stack.addWidget(SalesPage())           # 2
        self.stack.addWidget(PurchasesPage())       # 3
        self.stack.addWidget(ExpensesPage())        # 4
        self.stack.addWidget(ReportsPage())         # 5

        self.dashboard_page.navigate_to_product.connect(self._on_navigate_to_product)

        # Apply initial active state
        self._current_nav_idx = 0
        self._nav_btns[0].setStyleSheet(self._nav_btn_active_style())

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack, 1)

    @staticmethod
    def _nav_btn_normal_style() -> str:
        t = theme._active
        return (
            f"QPushButton {{ color: {t.nav_text}; background: transparent;"
            f" border: none; border-radius: 6px;"
            f" text-align: left; padding: 8px 12px; font-size: {t.size_normal}pt; }}"
            f"QPushButton:hover {{ background-color: rgba(255,255,255,0.10);"
            f" color: white; }}"
        )

    @staticmethod
    def _nav_btn_active_style() -> str:
        t = theme._active
        return (
            f"QPushButton {{ color: white; background-color: {t.nav_active};"
            f" border: none; border-radius: 6px;"
            f" text-align: left; padding: 8px 12px;"
            f" font-size: {t.size_normal}pt; font-weight: bold; }}"
        )

    @staticmethod
    def _utility_btn_style() -> str:
        t = theme._active
        return (
            f"QPushButton {{ color: {t.nav_text}; background: transparent;"
            f" border: none; border-radius: 6px;"
            f" text-align: left; padding: 6px 12px; font-size: {t.size_small}pt; }}"
            f"QPushButton:hover {{ background-color: rgba(255,255,255,0.10);"
            f" color: white; }}"
            f"QPushButton::menu-indicator {{ image: none; }}"
        )

    def _switch_page(self, index: int):
        self._nav_btns[self._current_nav_idx].setStyleSheet(self._nav_btn_normal_style())
        self._current_nav_idx = index
        self._nav_btns[index].setStyleSheet(self._nav_btn_active_style())
        self.stack.setCurrentIndex(index)

    def _on_navigate_to_product(self, product_id: int):
        self._switch_page(1)
        self.products_page.highlight_product(product_id)

    def _on_change_password(self):
        from ui.change_password_dialog import ChangePasswordDialog
        dlg = ChangePasswordDialog(self.username, self)
        dlg.exec()

    def _on_create_backup(self):
        from datetime import datetime
        default_name = datetime.now().strftime("StoreBackup_%Y-%m-%d_%H-%M-%S.db")
        path, _ = QFileDialog.getSaveFileName(
            self, "Create Backup", default_name, "Database Files (*.db)"
        )
        if not path:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            database.backup_to(path)
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "Backup Complete",
                f"Database backed up to:\n{path}")
        except Exception:
            QApplication.restoreOverrideCursor()
            print(traceback.format_exc())
            QMessageBox.critical(self, "Backup Failed",
                "An error occurred during backup.\n"
                "Please check disk space and permissions.")

    def _on_restore_backup(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "Database Files (*.db)"
        )
        if not path:
            return
        answer = QMessageBox.warning(
            self, "Confirm Restore",
            "This will replace the current database with the selected backup.\n"
            "Any unsaved changes will be lost.\n\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            database.restore_from(path)
            QApplication.restoreOverrideCursor()
            self._refresh_all_pages()
            QMessageBox.information(self, "Restore Complete",
                "The database has been restored successfully.\n"
                "It is recommended to restart the application.")
        except Exception:
            QApplication.restoreOverrideCursor()
            print(traceback.format_exc())
            QMessageBox.critical(self, "Restore Failed",
                "An error occurred during restore.\n"
                "The selected file may not be a valid database backup.")

    def _refresh_all_pages(self):
        for i in range(self.stack.count()):
            page = self.stack.widget(i)
            if hasattr(page, '_refresh'):
                page._refresh()
            elif hasattr(page, '_apply_filter'):
                page._apply_filter()
            elif hasattr(page, '_load_products'):
                page._load_products()
            elif hasattr(page, '_load_expenses'):
                page._load_expenses()

    def _on_logout(self):
        self.logged_out.emit()
        self.close()
