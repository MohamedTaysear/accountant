import traceback

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from logic import customers_logic
from ui import theme


class CustomersPage(QWidget):
    open_customer_detail = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_data = []
        self._show_balance_only = False
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme._active.spacing_xl, theme._active.spacing_xl,
            theme._active.spacing_xl, theme._active.spacing_xl)
        layout.setSpacing(theme._active.spacing_lg)

        title = QLabel("Customers")
        font = QFont(theme._active.font_family, theme._active.size_page_title)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet(f"color: {theme._active.text_primary}; background: transparent;")
        layout.addWidget(title)

        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by customer name…")
        self.search_input.textChanged.connect(self._apply_filter)
        controls.addWidget(self.search_input, 1)
        self.balance_btn = QPushButton("Show With Balance Only")
        self.balance_btn.setCheckable(True)
        self.balance_btn.toggled.connect(self._on_balance_toggled)
        controls.addWidget(self.balance_btn)
        layout.addLayout(controls)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Customer Name", "Phone", "Invoices", "Total Purchases", "Outstanding Balance"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in [1, 2]:
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        for col in [3, 4]:
            self.table.setColumnWidth(col, 150)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet(
            f"QTableWidget {{ border-radius: {theme._active.card_border_radius}px;"
            f" border: 1px solid {theme._active.border}; }}")
        theme.apply_table_style(self.table)
        self.table.doubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self.table)

    def _refresh(self):
        try:
            self._all_data = customers_logic.get_customers_list()
            self._apply_filter()
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", "Failed to load customers.")

    def _on_balance_toggled(self, checked):
        self._show_balance_only = checked
        self._apply_filter()

    def _apply_filter(self):
        query = self.search_input.text().lower().strip()
        data  = self._all_data
        if query:
            data = [r for r in data if query in r["name"].lower()]
        if self._show_balance_only:
            data = [r for r in data if float(r["outstanding_balance"]) > 0]

        highlight = QColor("#e67e22")
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(data))
        for row, r in enumerate(data):
            has_bal = float(r["outstanding_balance"]) > 0
            values  = [
                r["name"],
                r["phone"] or "",
                str(r["invoice_count"]),
                f"{float(r['total_purchases']):,.2f}",
                f"{float(r['outstanding_balance']):,.2f}",
            ]
            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if has_bal:
                    item.setForeground(highlight)
                self.table.setItem(row, col, item)
            self.table.item(row, 0).setData(Qt.UserRole, r["id"])
        self.table.setSortingEnabled(True)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

    def _on_row_double_clicked(self, index):
        customer_id = self.table.item(index.row(), 0).data(Qt.UserRole)
        if customer_id is not None:
            self.open_customer_detail.emit(customer_id)
