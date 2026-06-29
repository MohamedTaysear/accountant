import traceback

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QSizePolicy, QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

import products_db
from logic import report_logic
from logic import customers_logic
from ui import theme


def _make_card(title: str, value_label: QLabel, wide: bool = False) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.NoFrame)
    frame.setStyleSheet(
        f"QFrame {{ background-color: {theme._active.surface};"
        f" border: 1px solid {theme._active.border};"
        f" border-radius: {theme._active.card_border_radius}px; }}"
    )
    frame.setSizePolicy(
        QSizePolicy.Expanding if wide else QSizePolicy.Preferred,
        QSizePolicy.Fixed
    )
    frame.setGraphicsEffect(theme.make_card_shadow())

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(
        theme._active.spacing_lg, theme._active.spacing_md,
        theme._active.spacing_lg, theme._active.spacing_md)
    layout.setSpacing(4)

    title_lbl = QLabel(title)
    title_lbl.setAlignment(Qt.AlignCenter)
    title_lbl.setStyleSheet(
        f"background: transparent; border: none;"
        f" font-size: {theme._active.size_kpi_label}pt;"
        f" color: {theme._active.text_secondary};"
        f" font-weight: bold;"
        f" text-transform: uppercase;"
        f" letter-spacing: 0.5px;")

    value_label.setAlignment(Qt.AlignCenter)
    value_label.setStyleSheet(
        f"background: transparent; border: none;"
        f" font-size: {theme._active.size_kpi_value}pt;"
        f" font-weight: bold;"
        f" color: {theme._active.text_primary};")

    layout.addWidget(title_lbl)
    layout.addWidget(value_label)
    return frame


def _section_header(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size: {theme._active.size_heading}pt;"
        f" font-weight: bold;"
        f" color: {theme._active.text_primary};"
        f" background: transparent;"
        f" padding-bottom: 2px;"
    )
    return lbl


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"background-color: {theme._active.border}; border: none;")
    line.setFixedHeight(1)
    return line


class DashboardPage(QWidget):
    navigate_to_product  = Signal(int)
    navigate_to_customer = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet(f"background-color: {theme._active.background};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            theme._active.spacing_xl,
            theme._active.spacing_xl,
            theme._active.spacing_xl,
            theme._active.spacing_xl)
        layout.setSpacing(theme._active.spacing_xl)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        # ── Page title ───────────────────────────────────────────────
        page_title = QLabel("Dashboard")
        title_font = QFont(theme._active.font_family, theme._active.size_page_title)
        title_font.setBold(True)
        page_title.setFont(title_font)
        page_title.setStyleSheet(
            f"color: {theme._active.text_primary}; background: transparent;")
        layout.addWidget(page_title)

        # ── Section: Inventory Overview ──────────────────────────────
        layout.addWidget(_section_header("Inventory Overview"))

        self.lbl_total_products    = QLabel("—")
        self.lbl_active_products   = QLabel("—")
        self.lbl_inactive_products = QLabel("—")
        self.lbl_inventory_value   = QLabel("—")
        self.lbl_potential_profit  = QLabel("—")
        self.lbl_potential_sales   = QLabel("—")
        self.lbl_low_stock_count   = QLabel("—")

        inventory_grid = QGridLayout()
        inventory_grid.setSpacing(theme._active.spacing_md)
        inventory_cards = [
            ("Total Products",         self.lbl_total_products,    0, 0),
            ("Active",                 self.lbl_active_products,   0, 1),
            ("Inactive",               self.lbl_inactive_products, 0, 2),
            ("Inventory Value",        self.lbl_inventory_value,   0, 3),
            ("Potential Stock Profit", self.lbl_potential_profit,  0, 4),
            ("Potential Sales Value",  self.lbl_potential_sales,   0, 5),
            ("Low Stock Items",        self.lbl_low_stock_count,   0, 6),
        ]
        for title, lbl, row, col in inventory_cards:
            inventory_grid.addWidget(_make_card(title, lbl), row, col)
        layout.addLayout(inventory_grid)

        # ── Section: Today's Activity ─────────────────────────────────
        layout.addWidget(_divider())
        layout.addWidget(_section_header("Today's Activity"))

        self.lbl_today_sales      = QLabel("—")
        self.lbl_today_purchases  = QLabel("—")
        self.lbl_today_expenses   = QLabel("—")
        self.lbl_today_profit     = QLabel("—")
        self.lbl_today_net_profit = QLabel("—")

        today_grid = QGridLayout()
        today_grid.setSpacing(theme._active.spacing_md)
        today_cards = [
            ("Sales",       self.lbl_today_sales,      0, 0),
            ("Purchases",   self.lbl_today_purchases,  0, 1),
            ("Expenses",    self.lbl_today_expenses,   0, 2),
            ("Gross Profit", self.lbl_today_profit,    0, 3),
            ("Net Profit",  self.lbl_today_net_profit, 0, 4),
        ]
        for title, lbl, row, col in today_cards:
            today_grid.addWidget(_make_card(title, lbl), row, col)
        layout.addLayout(today_grid)

        # ── Section: This Month ───────────────────────────────────────
        layout.addWidget(_divider())
        layout.addWidget(_section_header("This Month"))

        self.lbl_this_month_profit     = QLabel("—")
        self.lbl_this_month_expenses   = QLabel("—")
        self.lbl_this_month_net_profit = QLabel("—")
        self.lbl_total_profit          = QLabel("—")
        self.lbl_net_profit            = QLabel("—")

        month_grid = QGridLayout()
        month_grid.setSpacing(theme._active.spacing_md)
        month_cards = [
            ("Month Gross Profit",  self.lbl_this_month_profit,     0, 0),
            ("Month Expenses",      self.lbl_this_month_expenses,   0, 1),
            ("Month Net Profit",    self.lbl_this_month_net_profit, 0, 2),
            ("All-Time Gross Profit", self.lbl_total_profit,        0, 3),
            ("All-Time Net Profit", self.lbl_net_profit,            0, 4),
        ]
        for title, lbl, row, col in month_cards:
            month_grid.addWidget(_make_card(title, lbl), row, col)
        layout.addLayout(month_grid)

        # ── Section: Receivables ─────────────────────────────────────
        layout.addWidget(_divider())
        layout.addWidget(_section_header("Receivables"))

        self.lbl_receivables_total    = QLabel("—")
        self.lbl_customers_with_balance = QLabel("—")

        recv_grid = QGridLayout()
        recv_grid.setSpacing(theme._active.spacing_md)

        recv_card = _make_card("Outstanding Receivables", self.lbl_receivables_total)
        recv_card.setCursor(Qt.PointingHandCursor)
        recv_card.mousePressEvent = lambda e: self._on_receivables_clicked()
        recv_grid.addWidget(recv_card, 0, 0)
        recv_grid.addWidget(_make_card("Customers With Balance", self.lbl_customers_with_balance), 0, 1)
        for col in range(2, 7):
            from PySide6.QtWidgets import QSpacerItem, QSizePolicy as SP
            recv_grid.addItem(QSpacerItem(0, 0, SP.Expanding, SP.Minimum), 0, col)
        layout.addLayout(recv_grid)

        # ── Section: Low Stock Products ───────────────────────────────
        layout.addWidget(_divider())
        layout.addWidget(_section_header("Low Stock Products"))

        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(4)
        self.low_stock_table.setHorizontalHeaderLabels(
            ["Product Name", "Category", "Current Stock", "Reorder Level"])
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        theme.apply_table_style(self.low_stock_table, max_height=240)

        self._low_stock_empty_lbl = theme.make_empty_label(
            "No low stock products — all items are adequately stocked.")

        layout.addWidget(self.low_stock_table)
        layout.addWidget(self._low_stock_empty_lbl)
        self._low_stock_empty_lbl.hide()

        # ── Section: Recent Transactions ──────────────────────────────
        layout.addWidget(_divider())
        layout.addWidget(_section_header("Recent Transactions"))

        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(
            ["Invoice #", "Type", "Date & Time", "Party", "Total"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        theme.apply_table_style(self.recent_table, max_height=360)

        self._recent_empty_lbl = theme.make_empty_label(
            "No recent transactions recorded.")

        layout.addWidget(self.recent_table)
        layout.addWidget(self._recent_empty_lbl)
        self._recent_empty_lbl.hide()

        layout.addStretch()

        self.low_stock_table.cellClicked.connect(self._on_low_stock_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

    def _refresh(self):
        try:
            import datetime
            today_date = datetime.date.today()
            today = str(today_date)
            first_of_month = str(today_date.replace(day=1))

            counts = products_db.get_product_counts()
            self.lbl_total_products.setText(str(counts["total"]))
            self.lbl_active_products.setText(str(counts["active"]))
            self.lbl_inactive_products.setText(str(counts["inactive"]))
            self.lbl_inventory_value.setText(
                f"{report_logic.get_inventory_value():,.2f}")
            self.lbl_potential_profit.setText(
                f"{report_logic.get_potential_stock_profit():,.2f}")
            self.lbl_potential_sales.setText(
                f"{report_logic.get_potential_sales_value():,.2f}")

            low_stock_count = report_logic.get_low_stock_count()
            self.lbl_low_stock_count.setText(str(low_stock_count))

            self.lbl_today_sales.setText(
                f"{report_logic.get_total_sales(today, today):,.2f}")
            self.lbl_today_purchases.setText(
                f"{report_logic.get_total_purchases(today, today):,.2f}")

            today_profit       = report_logic.get_total_profit(today, today)
            this_month_profit  = report_logic.get_total_profit(first_of_month, today)
            total_profit       = report_logic.get_total_profit()
            self.lbl_today_profit.setText(f"{today_profit:,.2f}")
            self.lbl_this_month_profit.setText(f"{this_month_profit:,.2f}")
            self.lbl_total_profit.setText(f"{total_profit:,.2f}")

            today_expenses        = report_logic.get_today_expenses()
            this_month_expenses   = report_logic.get_this_month_expenses()
            net_profit            = report_logic.get_net_profit()
            today_net_profit      = round(today_profit - today_expenses, 2)
            this_month_net_profit = round(this_month_profit - this_month_expenses, 2)

            self.lbl_today_expenses.setText(f"{today_expenses:,.2f}")
            self.lbl_this_month_expenses.setText(f"{this_month_expenses:,.2f}")
            self.lbl_net_profit.setText(f"{net_profit:,.2f}")
            self.lbl_today_net_profit.setText(f"{today_net_profit:,.2f}")
            self.lbl_this_month_net_profit.setText(f"{this_month_net_profit:,.2f}")

            kpi_base = (
                f"background: transparent; border: none;"
                f" font-size: {theme._active.size_kpi_value}pt; font-weight: bold;")

            # Profit/net labels get color coding
            for val, lbl in [
                (today_profit,          self.lbl_today_profit),
                (today_net_profit,      self.lbl_today_net_profit),
                (this_month_profit,     self.lbl_this_month_profit),
                (this_month_net_profit, self.lbl_this_month_net_profit),
                (total_profit,          self.lbl_total_profit),
                (net_profit,            self.lbl_net_profit),
            ]:
                lbl.setStyleSheet(
                    f"{kpi_base} color: {theme.color_for_value(val)};")

            # Low stock count — warning color if any
            if low_stock_count > 0:
                self.lbl_low_stock_count.setStyleSheet(
                    f"{kpi_base} color: {theme._active.error};")
            else:
                self.lbl_low_stock_count.setStyleSheet(
                    f"{kpi_base} color: {theme._active.success};")

            try:
                self.lbl_receivables_total.setText(
                    f"{customers_logic.get_outstanding_receivables_total():,.2f}")
                self.lbl_customers_with_balance.setText(
                    str(customers_logic.get_customers_with_outstanding_count()))
            except Exception:
                pass

            self._refresh_low_stock()
            self._refresh_recent_activity()
        except Exception:
            print(traceback.format_exc())

    def _refresh_low_stock(self):
        self.low_stock_table.setRowCount(0)
        for row in products_db.get_low_stock_products():
            r = self.low_stock_table.rowCount()
            self.low_stock_table.insertRow(r)
            cells = [
                row["name"] or "",
                row["category"] or "",
                str(row["stock_quantity"]),
                str(row["reorder_level"]),
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setToolTip(text)
                if c == 0:
                    item.setData(Qt.UserRole, row["id"])
                item.setForeground(QColor(theme._active.error))
                self.low_stock_table.setItem(r, c, item)
        has_rows = self.low_stock_table.rowCount() > 0
        self.low_stock_table.setVisible(has_rows)
        self._low_stock_empty_lbl.setVisible(not has_rows)

    def _refresh_recent_activity(self):
        self.recent_table.setRowCount(0)
        for row in report_logic.get_recent_activity(limit=10):
            r = self.recent_table.rowCount()
            self.recent_table.insertRow(r)
            self.recent_table.setItem(r, 0, QTableWidgetItem(row["invoice_number"] or ""))
            self.recent_table.setItem(r, 1, QTableWidgetItem(row["type"] or ""))
            self.recent_table.setItem(r, 2, QTableWidgetItem((row["created_at"] or "")[:16]))
            party = row["party"] or ""
            party_item = QTableWidgetItem(party)
            party_item.setToolTip(party)
            self.recent_table.setItem(r, 3, party_item)
            self.recent_table.setItem(r, 4, QTableWidgetItem(f"{row['total_amount']:,.2f}"))
        has_rows = self.recent_table.rowCount() > 0
        self.recent_table.setVisible(has_rows)
        self._recent_empty_lbl.setVisible(not has_rows)

    def _on_receivables_clicked(self):
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
            QHeaderView, QLabel as _QL,
        )
        try:
            rows = customers_logic.get_customers_with_outstanding_list()
        except Exception:
            traceback.print_exc()
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Outstanding Receivables")
        dlg.setMinimumSize(400, 300)
        lay = QVBoxLayout(dlg)
        if not rows:
            lay.addWidget(_QL("No outstanding receivables."))
        else:
            tbl = QTableWidget(len(rows), 2)
            tbl.setHorizontalHeaderLabels(["Customer", "Outstanding Balance"])
            tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            tbl.setColumnWidth(1, 160)
            tbl.setEditTriggers(QTableWidget.NoEditTriggers)
            tbl.setSelectionBehavior(QTableWidget.SelectRows)
            for r, row in enumerate(rows):
                name_item = QTableWidgetItem(row["name"])
                name_item.setData(Qt.UserRole, row["id"])
                tbl.setItem(r, 0, name_item)
                tbl.setItem(r, 1, QTableWidgetItem(f"{row['outstanding_balance']:,.2f}"))

            def _on_double_click(idx):
                cid = tbl.item(idx.row(), 0).data(Qt.UserRole)
                self.navigate_to_customer.emit(cid)
                dlg.accept()

            tbl.doubleClicked.connect(_on_double_click)
            lay.addWidget(tbl)
            lay.addWidget(_QL("Double-click to open customer profile."))
        dlg.exec()

    def _on_low_stock_clicked(self, row, col):
        item = self.low_stock_table.item(row, 0)
        if item is None:
            return
        product_id = item.data(Qt.UserRole)
        if product_id is not None:
            self.navigate_to_product.emit(product_id)
