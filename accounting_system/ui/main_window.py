import os
import traceback
import qtawesome as qta

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QPushButton, QApplication, QMessageBox,
    QMenu, QFileDialog, QFrame, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QIcon, QFont, QColor

from ui import theme

import config
import database
from ui.dashboard_page       import DashboardPage
from ui.products_page        import ProductsPage
from ui.sales_page           import SalesPage
from ui.purchases_page       import PurchasesPage
from ui.reports_page         import ReportsPage
from ui.expenses_page        import ExpensesPage
from ui.customers_page       import CustomersPage


class MainWindow(QMainWindow):
    logged_out = Signal()

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle(config.APP_NAME)
        self.setMinimumSize(config.MAIN_WINDOW_MIN_WIDTH, config.MAIN_WINDOW_MIN_HEIGHT)
        self._build_ui()

    def _build_ui(self):
        t = theme._active
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(t.sidebar_width)
        # Using a distinct blue color for the sidebar instead of standard gray
        sidebar.setStyleSheet(f"background-color: #1E3A8A; border-right: none;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App name header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: transparent; border: none;")
        header_frame.setFixedHeight(64) # Match navbar height
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(t.spacing_lg, t.spacing_md, t.spacing_lg, t.spacing_md)
        header_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon('fa5s.gem', color='white').pixmap(24, 24))
        logo_icon.setStyleSheet("background: transparent; border: none;")
        header_layout.addWidget(logo_icon)
        
        app_name_lbl = QLabel(config.APP_NAME)
        app_name_font = QFont(t.font_family, 12)
        app_name_font.setBold(True)
        app_name_lbl.setFont(app_name_font)
        app_name_lbl.setStyleSheet(f"color: white; font-weight: 700; border: none;")
        app_name_lbl.setWordWrap(True)
        header_layout.addWidget(app_name_lbl)
        sidebar_layout.addWidget(header_frame)

        # Navigation section
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent; border: none;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(t.spacing_md, t.spacing_lg, t.spacing_md, t.spacing_lg)
        nav_layout.setSpacing(t.spacing_xs)

        nav_buttons = [
            ("Dashboard",  0, "fa5s.home"),
            ("Products",   1, "fa5s.box"),
            ("Sales",      2, "fa5s.shopping-cart"),
            ("Purchases",  3, "fa5s.truck"),
            ("Expenses",   4, "fa5s.receipt"),
            ("Customers",  5, "fa5s.users"),
            ("Reports",    6, "fa5s.chart-bar"),
        ]
        self._nav_btns = []
        for label, idx, icon_name in nav_buttons:
            btn = QPushButton(f"  {label}")
            btn.setIcon(qta.icon(icon_name, color='white'))
            btn.setIconSize(QSize(20, 20))
            btn.setStyleSheet(self._nav_btn_normal_style())
            btn.setMinimumHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            nav_layout.addWidget(btn)
            self._nav_btns.append(btn)

        sidebar_layout.addWidget(nav_widget)
        sidebar_layout.addStretch()

        # Bottom utility buttons
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background: transparent; border: none;")
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(t.spacing_md, t.spacing_md, t.spacing_md, t.spacing_xl)
        bottom_layout.setSpacing(t.spacing_sm)

        for label, slot, icon_name in [
            ("Change Password", self._on_change_password, "fa5s.key"),
            ("Logout",          self._on_logout, "fa5s.sign-out-alt")
        ]:
            btn = QPushButton(f"  {label}")
            btn.setIcon(qta.icon(icon_name, color='rgba(255, 255, 255, 0.7)'))
            btn.setIconSize(QSize(18, 18))
            btn.setStyleSheet(self._utility_btn_style())
            btn.setMinimumHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            bottom_layout.addWidget(btn)

        backup_btn = QPushButton("  Backup & Restore")
        backup_btn.setIcon(qta.icon("fa5s.database", color='rgba(255, 255, 255, 0.7)'))
        backup_btn.setIconSize(QSize(18, 18))
        backup_btn.setStyleSheet(self._utility_btn_style())
        backup_btn.setMinimumHeight(44)
        backup_btn.setCursor(Qt.PointingHandCursor)
        backup_menu = QMenu(backup_btn)
        backup_menu.setStyleSheet(
            f"QMenu {{ background-color: {t.surface}; border: 1px solid {t.border};"
            f" border-radius: 8px; padding: 4px; }}"
            f"QMenu::item {{ padding: 8px 24px; color: {t.text_primary}; border-radius: 4px; }}"
            f"QMenu::item:selected {{ background-color: {t.nav_active_bg}; color: {t.primary}; }}")
        
        backup_menu.addAction(qta.icon("fa5s.download", color=t.text_primary), "Create Backup…", self._on_create_backup)
        backup_menu.addAction(qta.icon("fa5s.upload", color=t.text_primary), "Restore Backup…", self._on_restore_backup)
        
        backup_btn.setMenu(backup_menu)
        bottom_layout.addWidget(backup_btn)

        sidebar_layout.addWidget(bottom_widget)

        # ── Main Content Area (Navbar + Stack) ──────────────────────────
        main_area = QWidget()
        main_area.setStyleSheet(f"background-color: {t.background};")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Navbar
        navbar = QFrame()
        navbar.setFixedHeight(64)
        navbar.setStyleSheet(
            f"background-color: {t.surface}; border-bottom: 1px solid {t.border};"
        )
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(t.spacing_xl, 0, t.spacing_xl, 0)
        
        # User greeting
        greeting_lbl = QLabel(f"Welcome back, {self.username}")
        greeting_lbl.setStyleSheet(f"color: {t.text_secondary}; font-size: {t.size_section}pt; border: none; background: transparent;")
        navbar_layout.addWidget(greeting_lbl)
        
        navbar_layout.addStretch()

        # Theme Switch Button
        self.theme_btn = QPushButton("🌙 Dark Mode" if not t.is_dark else "☀️ Light Mode")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setStyleSheet(
            f"QPushButton {{"
            f" background-color: transparent; color: {t.text_secondary};"
            f" border: 1px solid {t.border}; border-radius: 20px; padding: 0 16px;"
            f"}}"
            f"QPushButton:hover {{"
            f" background-color: {t.surface_hover}; color: {t.text_primary};"
            f"}}"
        )
        self.theme_btn.setFixedHeight(40)
        self.theme_btn.clicked.connect(self._toggle_theme)
        navbar_layout.addWidget(self.theme_btn)

        main_layout.addWidget(navbar)

        # Page stack
        self.stack = QStackedWidget()
        self.dashboard_page  = DashboardPage()
        self.products_page   = ProductsPage()
        self.customers_page  = CustomersPage()
        self.stack.addWidget(self.dashboard_page)   # 0
        self.stack.addWidget(self.products_page)    # 1
        self.stack.addWidget(SalesPage())           # 2
        self.stack.addWidget(PurchasesPage())       # 3
        self.stack.addWidget(ExpensesPage())        # 4
        self.stack.addWidget(self.customers_page)   # 5
        self.stack.addWidget(ReportsPage())         # 6

        self.dashboard_page.navigate_to_product.connect(self._on_navigate_to_product)
        self.customers_page.open_customer_detail.connect(self._on_open_customer_detail)
        self.dashboard_page.navigate_to_customer.connect(self._on_open_customer_detail)

        # Apply initial active state
        self._current_nav_idx = 0
        self._nav_btns[0].setStyleSheet(self._nav_btn_active_style())

        main_layout.addWidget(self.stack, 1)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(main_area, 1)

    @staticmethod
    def _nav_btn_normal_style() -> str:
        t = theme._active
        return (
            f"QPushButton {{ color: rgba(255, 255, 255, 0.7); background: transparent;"
            f" border: none; border-radius: {t.button_border_radius}px;"
            f" text-align: left; padding: 8px 16px; font-size: {t.size_section}pt; font-weight: 500; }}"
            f"QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.1);"
            f" color: white; }}"
        )

    @staticmethod
    def _nav_btn_active_style() -> str:
        t = theme._active
        return (
            f"QPushButton {{ color: white; background-color: rgba(255, 255, 255, 0.15);"
            f" border: none; border-radius: {t.button_border_radius}px;"
            f" text-align: left; padding: 8px 16px;"
            f" font-size: {t.size_section}pt; font-weight: 700; }}"
        )

    @staticmethod
    def _utility_btn_style() -> str:
        t = theme._active
        return (
            f"QPushButton {{ color: rgba(255, 255, 255, 0.7); background: transparent;"
            f" border: none; border-radius: {t.button_border_radius}px;"
            f" text-align: left; padding: 6px 16px; font-size: {t.size_normal}pt; font-weight: 500; }}"
            f"QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.1);"
            f" color: white; }}"
            f"QPushButton::menu-indicator {{ image: none; }}"
        )

    def _toggle_theme(self):
        if theme._active.is_dark:
            theme.set_theme(theme.LightTheme())
        else:
            theme.set_theme(theme.DarkTheme())
            
        # Re-apply the stylesheet to the entire app
        app = QApplication.instance()
        app.setStyleSheet(theme.build_app_stylesheet())
        
        QMessageBox.information(self, "Theme Changed", "Theme has been changed. Some pages might require you to switch to them or restart to fully apply the theme colors.")
        
        self.theme_btn.setText("🌙 Dark Mode" if not theme._active.is_dark else "☀️ Light Mode")

    def _switch_page(self, index: int):
        self._nav_btns[self._current_nav_idx].setStyleSheet(self._nav_btn_normal_style())
        self._current_nav_idx = index
        self._nav_btns[index].setStyleSheet(self._nav_btn_active_style())
        self.stack.setCurrentIndex(index)

    def _on_navigate_to_product(self, product_id: int):
        self._switch_page(1)
        self.products_page.highlight_product(product_id)

    def _on_open_customer_detail(self, customer_id: int):
        if not hasattr(self, '_customer_detail_page'):
            from ui.customer_detail_page import CustomerDetailPage
            self._customer_detail_page = CustomerDetailPage()
            self.stack.addWidget(self._customer_detail_page)
            self._customer_detail_page.back_requested.connect(
                lambda: self._switch_page(5)
            )
        self._customer_detail_page.load_customer(customer_id)
        detail_idx = self.stack.indexOf(self._customer_detail_page)
        self._current_nav_idx = 5
        for i, btn in enumerate(self._nav_btns):
            btn.setStyleSheet(self._nav_btn_active_style() if i == 5 else self._nav_btn_normal_style())
        self.stack.setCurrentIndex(detail_idx)

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
        if hasattr(self, 'customers_page'):
            self.customers_page._refresh()

    def _on_logout(self):
        self.logged_out.emit()
        self.close()
