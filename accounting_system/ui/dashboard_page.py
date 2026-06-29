import traceback
import qtawesome as qta

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


def _make_card(title: str, value_label: QLabel, wide: bool = False, icon_name: str = "", bg_color: str = None, icon_color: str = None) -> QFrame:
    t = theme._active
    
    # Allow passing custom background color, fallback to surface
    actual_bg_color = bg_color if bg_color else t.surface
    
    frame = QFrame()
    frame.setFrameShape(QFrame.NoFrame)
    frame.setStyleSheet(
        f"QFrame {{"
        f" background-color: {actual_bg_color};"
        f" border: 1px solid {t.border};"
        f" border-radius: {t.card_border_radius}px;"
        f"}}"
    )
    frame.setSizePolicy(
        QSizePolicy.Expanding if wide else QSizePolicy.Preferred,
        QSizePolicy.Fixed
    )
    frame.setGraphicsEffect(theme.make_card_shadow())

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(t.spacing_lg, t.spacing_lg, t.spacing_lg, t.spacing_lg)
    layout.setSpacing(t.spacing_sm)

    # Top row: Title and Icon
    top_layout = QHBoxLayout()
    top_layout.setContentsMargins(0, 0, 0, 0)
    
    title_lbl = QLabel(title)
    title_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    title_lbl.setStyleSheet(
        f"background: transparent; border: none;"
        f" font-size: {t.size_kpi_label}pt;"
        f" color: {t.text_secondary};"
        f" font-weight: 600;"
        f" text-transform: uppercase;"
        f" letter-spacing: 0.5px;")

    top_layout.addWidget(title_lbl)
    top_layout.addStretch()

    if icon_name:
        icon_lbl = QLabel()
        actual_icon_color = icon_color if icon_color else t.primary
        icon_lbl.setPixmap(qta.icon(icon_name, color=actual_icon_color).pixmap(24, 24))
        icon_lbl.setAlignment(Qt.AlignCenter)
        
        # Determine background for icon based on its color for contrast
        # Fallback if no specific logic
        icon_bg = t.nav_active_bg
        
        icon_lbl.setStyleSheet(
            f"background: {icon_bg}; border: none;"
            f" border-radius: 6px;"
            f" padding: 4px;"
        )
        icon_lbl.setFixedSize(36, 36)
        top_layout.addWidget(icon_lbl)

    value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    value_label.setStyleSheet(
        f"background: transparent; border: none;"
        f" font-size: {t.size_kpi_value}pt;"
        f" font-weight: 700;"
        f" color: {t.text_primary};")

    layout.addLayout(top_layout)
    layout.addWidget(value_label)
    return frame


def _section_header(text: str) -> QLabel:
    t = theme._active
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size: {t.size_heading}pt;"
        f" font-weight: 700;"
        f" color: {t.text_primary};"
        f" background: transparent;"
        f" padding-bottom: {t.spacing_xs}px;"
    )
    return lbl


def _divider() -> QFrame:
    t = theme._active
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"background-color: {t.border}; border: none;")
    line.setFixedHeight(1)
    return line


class DashboardPage(QWidget):
    navigate_to_product  = Signal(int)
    navigate_to_customer = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        t = theme._active
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet(f"background-color: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(t.spacing_xl, t.spacing_xl, t.spacing_xl, t.spacing_xl)
        layout.setSpacing(t.spacing_xl)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        # ── Page title ───────────────────────────────────────────────
        page_title = QLabel("📊 Dashboard Overview")
        title_font = QFont(t.font_family, t.size_page_title)
        title_font.setBold(True)
        page_title.setFont(title_font)
        page_title.setStyleSheet(f"color: {t.text_primary}; background: transparent; font-weight: 700;")
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
        inventory_grid.setSpacing(t.spacing_md)
        
        # Colors for the cards
        if not t.is_dark:
            c_blue = "#EEF2FF"
            c_green = "#ECFDF5"
            c_red = "#FEF2F2"
            c_yellow = "#FEF9C3"
            c_purple = "#FAF5FF"
        else:
            c_blue = "#1E3A8A"
            c_green = "#064E3B"
            c_red = "#7F1D1D"
            c_yellow = "#713F12"
            c_purple = "#4C1D95"
            
        inventory_cards = [
            ("Total Products",         self.lbl_total_products,    0, 0, "fa5s.box", c_blue, "#2563EB"),
            ("Active",                 self.lbl_active_products,   0, 1, "fa5s.check-circle", c_green, "#059669"),
            ("Inactive",               self.lbl_inactive_products, 0, 2, "fa5s.times-circle", c_red, "#DC2626"),
            ("Inventory Value",        self.lbl_inventory_value,   0, 3, "fa5s.money-bill-wave", c_purple, "#7C3AED"),
            ("Potential Stock Profit", self.lbl_potential_profit,  0, 4, "fa5s.chart-line", c_green, "#059669"),
            ("Potential Sales Value",  self.lbl_potential_sales,   0, 5, "fa5s.gem", c_yellow, "#D97706"),
            ("Low Stock Items",        self.lbl_low_stock_count,   0, 6, "fa5s.exclamation-triangle", c_red, "#DC2626"),
        ]
        
        for title, lbl, row, col, icon, bg, ic_color in inventory_cards:
            inventory_grid.addWidget(_make_card(title, lbl, icon_name=icon, bg_color=bg, icon_color=ic_color), row, col)
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
        today_grid.setSpacing(t.spacing_md)
        today_cards = [
            ("Sales",       self.lbl_today_sales,      0, 0, "fa5s.shopping-cart", c_green, "#059669"),
            ("Purchases",   self.lbl_today_purchases,  0, 1, "fa5s.truck", c_blue, "#2563EB"),
            ("Expenses",    self.lbl_today_expenses,   0, 2, "fa5s.receipt", c_red, "#DC2626"),
            ("Gross Profit", self.lbl_today_profit,    0, 3, "fa5s.chart-pie", c_purple, "#7C3AED"),
            ("Net Profit",  self.lbl_today_net_profit, 0, 4, "fa5s.wallet", c_green, "#059669"),
        ]
        for title, lbl, row, col, icon, bg, ic_color in today_cards:
            today_grid.addWidget(_make_card(title, lbl, icon_name=icon, bg_color=bg, icon_color=ic_color), row, col)
        layout.addLayout(today_grid)

        # ── Section: This Month ───────────────────────────────────────
        layout.addWidget(_divider())
        layout.addWidget(_section_header("Performance Summary"))

        self.lbl_this_month_profit     = QLabel("—")
        self.lbl_this_month_expenses   = QLabel("—")
        self.lbl_this_month_net_profit = QLabel("—")
        self.lbl_total_profit          = QLabel("—")
        self.lbl_net_profit            = QLabel("—")

        month_grid = QGridLayout()
        month_grid.setSpacing(t.spacing_md)
        month_cards = [
            ("Month Gross Profit",  self.lbl_this_month_profit,     0, 0, "fa5s.calendar-alt", None, None),
            ("Month Expenses",      self.lbl_this_month_expenses,   0, 1, "fa5s.level-down-alt", None, None),
            ("Month Net Profit",    self.lbl_this_month_net_profit, 0, 2, "fa5s.university", None, None),
            ("All-Time Gross Profit", self.lbl_total_profit,        0, 3, "fa5s.star", None, None),
            ("All-Time Net Profit", self.lbl_net_profit,            0, 4, "fa5s.trophy", None, None),
        ]
        for title, lbl, row, col, icon, bg, ic_color in month_cards:
            month_grid.addWidget(_make_card(title, lbl, icon_name=icon, bg_color=bg, icon_color=ic_color), row, col)
        layout.addLayout(month_grid)

        # ── Section: Receivables ─────────────────────────────────────
        layout.addWidget(_divider())
        layout.addWidget(_section_header("Receivables"))

        self.lbl_receivables_total    = QLabel("—")
        self.lbl_customers_with_balance = QLabel("—")

        recv_grid = QGridLayout()
        recv_grid.setSpacing(t.spacing_md)

        recv_card = _make_card("Outstanding Receivables", self.lbl_receivables_total, icon_name="fa5s.file-invoice-dollar", bg_color=c_yellow, icon_color="#D97706")
        recv_card.setCursor(Qt.PointingHandCursor)
        recv_card.mousePressEvent = lambda e: self._on_receivables_clicked()
        recv_grid.addWidget(recv_card, 0, 0)
        
        recv_grid.addWidget(_make_card("Customers With Balance", self.lbl_customers_with_balance, icon_name="fa5s.users", bg_color=c_blue, icon_color="#2563EB"), 0, 1)
        
        for col in range(2, 7):
            from PySide6.QtWidgets import QSpacerItem, QSizePolicy as SP
            recv_grid.addItem(QSpacerItem(0, 0, SP.Expanding, SP.Minimum), 0, col)
        layout.addLayout(recv_grid)

        # ── Section: Low Stock Products ───────────────────────────────
        layout.addWidget(_divider())
        layout.addWidget(_section_header("Alerts: Low Stock Products"))

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

            t = theme._active
            kpi_base = (
                f"background: transparent; border: none;"
                f" font-size: {t.size_kpi_value}pt; font-weight: 700;")

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
                    f"{kpi_base} color: {t.error};")
            else:
                self.lbl_low_stock_count.setStyleSheet(
                    f"{kpi_base} color: {t.success};")

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
                # Warning for low stock, use error color
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
        dlg.setMinimumSize(500, 400)
        lay = QVBoxLayout(dlg)
        
        title_lbl = _QL("Outstanding Receivables")
        title_lbl.setStyleSheet(f"font-size: {theme._active.size_heading}pt; font-weight: bold; color: {theme._active.text_primary};")
        lay.addWidget(title_lbl)

        if not rows:
            lay.addWidget(_QL("No outstanding receivables."))
        else:
            tbl = QTableWidget(len(rows), 2)
            tbl.setHorizontalHeaderLabels(["Customer", "Outstanding Balance"])
            tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            tbl.setColumnWidth(1, 160)
            theme.apply_table_style(tbl, max_height=300)
            
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
            
            help_lbl = _QL("Double-click to open customer profile.")
            help_lbl.setStyleSheet(f"color: {theme._active.text_secondary}; font-style: italic;")
            lay.addWidget(help_lbl)
        dlg.exec()

    def _on_low_stock_clicked(self, row, col):
        item = self.low_stock_table.item(row, 0)
        if item is None:
            return
        product_id = item.data(Qt.UserRole)
        if product_id is not None:
            self.navigate_to_product.emit(product_id)
