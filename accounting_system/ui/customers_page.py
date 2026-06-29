import traceback

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFrame,
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
        t = theme._active
        layout = QVBoxLayout(self)
        layout.setContentsMargins(t.spacing_xl, t.spacing_xl, t.spacing_xl, t.spacing_xl)
        layout.setSpacing(t.spacing_lg)

        title = QLabel("👥 Customers Directory")
        font = QFont(t.font_family, t.size_page_title)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet(f"color: {t.text_primary}; background: transparent; font-weight: 700;")
        layout.addWidget(title)

        # ── Control Bar (Search / Filter) ─────────────────────────────
        control_frame = QFrame()
        control_frame.setStyleSheet(
            f"QFrame {{"
            f" background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px;"
            f"}}"
        )
        control_frame.setGraphicsEffect(theme.make_card_shadow())
        
        controls = QHBoxLayout(control_frame)
        controls.setContentsMargins(t.spacing_md, t.spacing_sm, t.spacing_md, t.spacing_sm)
        controls.setSpacing(t.spacing_md)
        controls.setAlignment(Qt.AlignVCenter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by customer name…")
        self.search_input.setMaximumWidth(400)
        self.search_input.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px 12px; background: {t.background}; }}"
            f"QLineEdit:focus {{ border-color: {t.primary}; }}"
        )
        self.search_input.textChanged.connect(self._apply_filter)
        controls.addWidget(self.search_input)
        
        self.balance_btn = QPushButton("💰 Show With Balance Only")
        self.balance_btn.setCheckable(True)
        self.balance_btn.setStyleSheet(
            f"QPushButton {{ background-color: {t.surface_alt}; color: {t.text_primary};"
            f" border: 1px solid {t.border}; border-radius: 6px; padding: 6px 12px; font-weight: 500; }}"
            f"QPushButton:checked {{ background-color: {t.nav_active_bg}; color: {t.primary}; border-color: {t.primary}; }}"
            f"QPushButton:hover:!checked {{ background-color: {t.surface_hover}; }}"
        )
        self.balance_btn.setCursor(Qt.PointingHandCursor)
        self.balance_btn.toggled.connect(self._on_balance_toggled)
        controls.addWidget(self.balance_btn)
        
        controls.addStretch()
        layout.addWidget(control_frame)

        # ── Customers table ───────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Customer Name", "Phone", "Invoices", "Total Purchases", "Outstanding Balance", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in [1, 2]:
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        for col in [3, 4]:
            self.table.setColumnWidth(col, 150)
        self.table.setColumnWidth(5, 170)
        
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        
        theme.apply_table_style(self.table)
        self.table.doubleClicked.connect(self._on_row_double_clicked)
        # Rebuild action buttons after each sort so they stay aligned with their rows
        self.table.horizontalHeader().sortIndicatorChanged.connect(
            lambda *_: self._repopulate_action_buttons())
            
        self._empty_lbl = theme.make_empty_label("No customers found.")
        layout.addWidget(self.table)
        layout.addWidget(self._empty_lbl)
        self._empty_lbl.hide()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

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

        t = theme._active
        highlight = QColor(t.warning) # Or primary? Let's use warning for outstanding balance
        
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
                if col == 0:
                    item.setFont(QFont(t.font_family, t.size_normal, QFont.Bold))
                
                if has_bal and col == 4:
                    item.setForeground(highlight)
                    item.setFont(QFont(t.font_family, t.size_normal, QFont.Bold))
                    
                self.table.setItem(row, col, item)
            self.table.item(row, 0).setData(Qt.UserRole, r["id"])
            
        self.table.setSortingEnabled(True)
        self._repopulate_action_buttons()
        
        has_rows = self.table.rowCount() > 0
        self.table.setVisible(has_rows)
        self._empty_lbl.setVisible(not has_rows)

    def _repopulate_action_buttons(self):
        """Rebuild Receive Payment buttons after data load or sort."""
        t = theme._active
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            bal_item  = self.table.item(row, 4)
            if name_item is None or bal_item is None:
                self.table.removeCellWidget(row, 5)
                continue
            customer_id = name_item.data(Qt.UserRole)
            try:
                outstanding = float(bal_item.text().replace(",", ""))
            except ValueError:
                outstanding = 0.0
                
            if outstanding > 0:
                cell_widget = QWidget()
                btn_layout  = QHBoxLayout(cell_widget)
                btn_layout.setContentsMargins(4, 4, 4, 4)
                
                btn = QPushButton("💵 Receive Payment")
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: {t.primary}; color: white;"
                    f" border: none; border-radius: 6px; padding: 4px 8px; font-weight: 600; }}"
                    f"QPushButton:hover {{ background-color: {t.primary_hover}; }}"
                )
                btn.clicked.connect(
                    lambda checked=False, cid=customer_id,
                    cn=name_item.text(), ot=outstanding:
                        self._open_receive_payment(cid, cn, ot)
                )
                btn_layout.addWidget(btn)
                self.table.setCellWidget(row, 5, cell_widget)
            else:
                self.table.removeCellWidget(row, 5)

    def _open_receive_payment(self, customer_id: int, customer_name: str, outstanding: float):
        from ui.receive_payment_dialog import ReceivePaymentDialog
        dlg = ReceivePaymentDialog(customer_id, customer_name, outstanding, parent=self)
        if dlg.exec():
            self._refresh()

    def _on_row_double_clicked(self, index):
        customer_id = self.table.item(index.row(), 0).data(Qt.UserRole)
        if customer_id is not None:
            self.open_customer_detail.emit(customer_id)
