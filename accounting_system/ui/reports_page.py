import csv
import traceback
from datetime import date, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QApplication, QSplitter,
    QLineEdit, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from logic import expenses_logic, report_logic
from ui import theme

PAGE_SIZE = 10


class ReportsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_active_table = "sales"
        self._sales_rows = []
        self._purchases_rows = []
        self._expenses_rows = []
        self._sales_page = 0
        self._purchases_page = 0
        self._expenses_page = 0
        self._build_ui()

    @staticmethod
    def _section_panel(title: str, icon: str = "", icon_color: str = "") -> tuple:
        """Return (frame, layout, header_hbox) for a section panel."""
        t = theme._active
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        vl = QVBoxLayout(frame)
        vl.setContentsMargins(t.spacing_sm, t.spacing_sm, t.spacing_sm, t.spacing_sm)
        vl.setSpacing(t.spacing_xs)

        hdr_hbox = QHBoxLayout()
        hdr_hbox.setSpacing(t.spacing_xs)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(
                f"font-size: 14pt; color: {icon_color or t.primary};"
                f" background: transparent; border: none;")
            hdr_hbox.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: {t.size_heading}pt; font-weight: bold;"
            f" color: {t.text_primary}; background: transparent;"
            f" border: none; padding: 0px;")
        hdr_hbox.addWidget(title_lbl)

        vl.addLayout(hdr_hbox)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {t.border}; border: none; max-height: 1px;")
        vl.addWidget(sep)

        return frame, vl, hdr_hbox

    def _add_pagination_footer(self, parent_vl, prefix: str):
        """Add Showing label + [<] [page] [>] buttons to parent_vl. Returns widget refs."""
        t = theme._active
        foot = QHBoxLayout()
        foot.setSpacing(t.spacing_xs)

        showing_lbl = QLabel("Showing 0 of 0")
        showing_lbl.setStyleSheet(
            f"color: {t.text_secondary}; background: transparent; border: none;"
            f" font-size: {t.size_small}pt;")
        foot.addWidget(showing_lbl)
        foot.addStretch()

        prev_btn = QPushButton("‹")
        prev_btn.setFixedSize(28, 28)
        prev_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid {t.border};"
            f" border-radius: 4px; color: {t.text_secondary}; font-size: 12pt; }}"
            f"QPushButton:hover {{ background: {t.surface_alt}; }}"
            f"QPushButton:disabled {{ color: {t.text_disabled}; }}")

        page_btn = QPushButton("1")
        page_btn.setFixedSize(28, 28)
        page_btn.setStyleSheet(
            f"QPushButton {{ background: {t.primary}; border: none;"
            f" border-radius: 4px; color: #fff; font-weight: bold; }}")

        next_btn = QPushButton("›")
        next_btn.setFixedSize(28, 28)
        next_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid {t.border};"
            f" border-radius: 4px; color: {t.text_secondary}; font-size: 12pt; }}"
            f"QPushButton:hover {{ background: {t.surface_alt}; }}"
            f"QPushButton:disabled {{ color: {t.text_disabled}; }}")

        foot.addWidget(prev_btn)
        foot.addWidget(page_btn)
        foot.addWidget(next_btn)
        parent_vl.addLayout(foot)
        return showing_lbl, prev_btn, page_btn, next_btn

    def _build_ui(self):
        t = theme._active
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet(f"background-color: {t.background};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(t.spacing_xl, t.spacing_xl, t.spacing_xl, t.spacing_xl)
        layout.setSpacing(t.spacing_lg)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        # ── Page header ──────────────────────────────────────────────
        top_row = QHBoxLayout()
        page_title = QLabel("Reports")
        title_font = QFont(t.font_family, t.size_page_title)
        title_font.setBold(True)
        page_title.setFont(title_font)
        page_title.setStyleSheet(f"color: {t.text_primary}; background: transparent;")
        top_row.addWidget(page_title)
        top_row.addStretch()
        self.export_btn = QPushButton("⬇  Export to CSV")
        self.export_btn.setProperty("class", "primary")
        top_row.addWidget(self.export_btn)
        layout.addLayout(top_row)

        # ── Filter + Summary card ────────────────────────────────────
        filter_card = QFrame()
        filter_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        filter_card_layout = QVBoxLayout(filter_card)
        filter_card_layout.setContentsMargins(
            t.spacing_xl, t.spacing_lg, t.spacing_xl, t.spacing_lg)
        filter_card_layout.setSpacing(t.spacing_lg)

        # Filter controls row
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(t.spacing_md)
        filter_bar.setAlignment(Qt.AlignVCenter)

        def _lbl(text):
            l = QLabel(text)
            l.setStyleSheet(f"color: {t.text_secondary}; background: transparent;")
            return l

        filter_bar.addWidget(_lbl("Period:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Today", "Yesterday", "This Week", "This Month", "Custom"])
        self.filter_combo.setFixedWidth(140)
        filter_bar.addWidget(self.filter_combo)

        filter_bar.addSpacing(t.spacing_md)
        filter_bar.addWidget(_lbl("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate())
        self.from_date.setEnabled(False)
        self.from_date.setFixedWidth(120)
        filter_bar.addWidget(self.from_date)

        filter_bar.addWidget(_lbl("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setEnabled(False)
        self.to_date.setFixedWidth(120)
        filter_bar.addWidget(self.to_date)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setProperty("class", "primary")
        self.apply_btn.setEnabled(False)
        self.apply_btn.setFixedWidth(80)
        filter_bar.addWidget(self.apply_btn)
        filter_bar.addStretch()
        filter_card_layout.addLayout(filter_bar)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background-color: {t.border}; border: none;")
        div.setFixedHeight(1)
        filter_card_layout.addWidget(div)

        # Summary metrics row
        summary_bar = QHBoxLayout()
        summary_bar.setSpacing(0)

        self.total_sales_label     = QLabel("0.00")
        self.total_purchases_label = QLabel("0.00")
        self.total_expenses_label  = QLabel("0.00")
        self.total_profit_label    = QLabel("0.00")
        self.net_profit_label      = QLabel("0.00")

        kpi_font = QFont(t.font_family, t.size_heading)
        kpi_font.setBold(True)

        for i, (kpi_title, lbl, color) in enumerate([
            ("Total Sales",     self.total_sales_label,     t.text_primary),
            ("Total Purchases", self.total_purchases_label, t.text_primary),
            ("Total Expenses",  self.total_expenses_label,  t.text_primary),
            ("Gross Profit",    self.total_profit_label,    t.text_primary),
            ("Net Profit",      self.net_profit_label,      t.text_primary),
        ]):
            metric_widget = QFrame()
            border_style = (
                f"border-left: 1px solid {t.border};" if i > 0 else ""
            )
            metric_widget.setStyleSheet(
                f"QFrame {{ background: transparent; border: none; {border_style} }}")
            m_layout = QVBoxLayout(metric_widget)
            m_layout.setContentsMargins(t.spacing_xl, t.spacing_sm, t.spacing_xl, t.spacing_sm)
            m_layout.setSpacing(2)

            title_lbl = QLabel(kpi_title)
            title_lbl.setStyleSheet(
                f"font-size: {t.size_small}pt; color: {t.text_secondary};"
                f" background: transparent; border: none;")

            lbl.setFont(kpi_font)
            lbl.setStyleSheet(
                f"font-weight: bold; color: {color};"
                f" background: transparent; border: none;")

            m_layout.addWidget(title_lbl)
            m_layout.addWidget(lbl)
            summary_bar.addWidget(metric_widget, 1)

        filter_card_layout.addLayout(summary_bar)
        layout.addWidget(filter_card)

        # ── History tables: Sales | Purchases (side by side) ──────────
        top_history_splitter = QSplitter(Qt.Horizontal)
        top_history_splitter.setHandleWidth(12)
        top_history_splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        # Sales History panel
        sales_frame, sales_vl, _ = self._section_panel(
            "Sales History", "🛒", t.primary)
        self.sales_search = QLineEdit()
        self.sales_search.setPlaceholderText("Search by Invoice #, Customer, Status…")
        self.sales_search.setClearButtonEnabled(True)
        sales_vl.addWidget(self.sales_search)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(
            ["Invoice #", "Date & Time", "Customer", "Status", "Total Amount"])
        self.sales_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        for col, w in [(0, 100), (1, 130), (3, 90), (4, 100)]:
            self.sales_table.setColumnWidth(col, w)
        theme.apply_table_style(self.sales_table, max_height=300)
        self._sales_empty_lbl = theme.make_empty_label("No sales invoices yet.")
        self._sales_empty_search_lbl = theme.make_empty_label("No results match your search.")
        sales_vl.addWidget(self.sales_table)
        sales_vl.addWidget(self._sales_empty_lbl)
        sales_vl.addWidget(self._sales_empty_search_lbl)
        self._sales_empty_lbl.hide()
        self._sales_empty_search_lbl.hide()

        (self._sales_showing_lbl, self._sales_prev_btn,
         self._sales_page_btn, self._sales_next_btn) = self._add_pagination_footer(sales_vl, "sales")

        top_history_splitter.addWidget(sales_frame)

        # Purchases History panel
        purchases_frame, purchases_vl, _ = self._section_panel(
            "Purchases History", "📋", t.primary)
        self.purchases_search = QLineEdit()
        self.purchases_search.setPlaceholderText("Search by Invoice #, Supplier, Status…")
        self.purchases_search.setClearButtonEnabled(True)
        purchases_vl.addWidget(self.purchases_search)

        self.purchases_table = QTableWidget()
        self.purchases_table.setColumnCount(5)
        self.purchases_table.setHorizontalHeaderLabels(
            ["Invoice #", "Date & Time", "Supplier", "Status", "Total Amount"])
        self.purchases_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        for col, w in [(0, 100), (1, 130), (3, 90), (4, 100)]:
            self.purchases_table.setColumnWidth(col, w)
        theme.apply_table_style(self.purchases_table, max_height=300)
        self._purchases_empty_lbl = theme.make_empty_label("No purchase invoices yet.")
        self._purchases_empty_search_lbl = theme.make_empty_label("No results match your search.")
        purchases_vl.addWidget(self.purchases_table)
        purchases_vl.addWidget(self._purchases_empty_lbl)
        purchases_vl.addWidget(self._purchases_empty_search_lbl)
        self._purchases_empty_lbl.hide()
        self._purchases_empty_search_lbl.hide()

        (self._purchases_showing_lbl, self._purchases_prev_btn,
         self._purchases_page_btn, self._purchases_next_btn) = self._add_pagination_footer(purchases_vl, "purchases")

        top_history_splitter.addWidget(purchases_frame)
        layout.addWidget(top_history_splitter)

        # ── Expenses History (full width) ─────────────────────────────
        expenses_frame, expenses_vl, expenses_hdr_hbox = self._section_panel(
            "Expenses History", "📅", t.primary)

        # Add category + search to the right of the header row
        expenses_hdr_hbox.addStretch()
        cat_lbl = QLabel("Category:")
        cat_lbl.setStyleSheet(f"color: {t.text_secondary}; background: transparent; border: none;")
        expenses_hdr_hbox.addWidget(cat_lbl)
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.category_combo.setFixedWidth(150)
        self.category_combo.currentIndexChanged.connect(self._on_expense_filter_changed)
        expenses_hdr_hbox.addWidget(self.category_combo)
        self.expense_search = QLineEdit()
        self.expense_search.setPlaceholderText("Search…")
        self.expense_search.setClearButtonEnabled(True)
        self.expense_search.setFixedWidth(200)
        self.expense_search.textChanged.connect(self._on_expense_filter_changed)
        expenses_hdr_hbox.addWidget(self.expense_search)

        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(5)
        self.expenses_table.setHorizontalHeaderLabels(
            ["Invoice #", "Date & Time", "Category", "Description", "Total Amount"])
        self.expenses_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        for col, w in [(0, 110), (1, 140), (2, 130), (4, 120)]:
            self.expenses_table.setColumnWidth(col, w)
        theme.apply_table_style(self.expenses_table, max_height=300)
        self._expenses_empty_lbl = theme.make_empty_label("No expense invoices yet.")
        self._expenses_empty_search_lbl = theme.make_empty_label("No results match your search.")
        expenses_vl.addWidget(self.expenses_table)
        expenses_vl.addWidget(self._expenses_empty_lbl)
        expenses_vl.addWidget(self._expenses_empty_search_lbl)
        self._expenses_empty_lbl.hide()
        self._expenses_empty_search_lbl.hide()

        (self._expenses_showing_lbl, self._expenses_prev_btn,
         self._expenses_page_btn, self._expenses_next_btn) = self._add_pagination_footer(expenses_vl, "expenses")

        layout.addWidget(expenses_frame)

        # ── Top Performers ─────────────────────────────────────────────
        analytics_hdr = QLabel("Top Performers")
        analytics_font = QFont(t.font_family, t.size_heading)
        analytics_font.setBold(True)
        analytics_hdr.setFont(analytics_font)
        analytics_hdr.setStyleSheet(
            f"color: {t.text_primary}; background: transparent;"
            f" padding-top: {t.spacing_xs}px;")
        layout.addWidget(analytics_hdr)

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.setHandleWidth(12)
        top_splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        for group_title, icon, icon_color, col_labels, attr in [
            ("Top Selling Products",   "📊", t.success,  ["Product", "Qty Sold"],      "top_sales_table"),
            ("Top Purchased Products", "🛒", t.primary,  ["Product", "Qty Purchased"], "top_purchases_table"),
            ("Top Expense Categories", "🕐", "#D97706",  ["Category", "Total Amount"], "top_expenses_table"),
        ]:
            grp_frame, grp_vl, _ = self._section_panel(group_title, icon, icon_color)
            tbl = QTableWidget()
            tbl.setColumnCount(2)
            tbl.setHorizontalHeaderLabels(col_labels)
            tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            tbl.setColumnWidth(1, 138)
            theme.apply_table_style(tbl)
            setattr(self, attr, tbl)
            grp_vl.addWidget(tbl)
            top_splitter.addWidget(grp_frame)

        layout.addWidget(top_splitter)

        # ── Signal connections ────────────────────────────────────────
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        self.apply_btn.clicked.connect(self._apply_filter)
        self.sales_search.textChanged.connect(self._on_sales_search_changed)
        self.purchases_search.textChanged.connect(self._on_purchases_search_changed)
        self.sales_table.doubleClicked.connect(self._on_sales_row_double_clicked)
        self.purchases_table.doubleClicked.connect(self._on_purchases_row_double_clicked)
        self.expenses_table.doubleClicked.connect(self._on_expenses_row_double_clicked)
        self.sales_table.clicked.connect(
            lambda: setattr(self, '_last_active_table', 'sales'))
        self.purchases_table.clicked.connect(
            lambda: setattr(self, '_last_active_table', 'purchases'))
        self.expenses_table.clicked.connect(
            lambda: setattr(self, '_last_active_table', 'expenses'))
        self.export_btn.clicked.connect(self._on_export_csv)

        self._sales_prev_btn.clicked.connect(self._sales_prev_page)
        self._sales_next_btn.clicked.connect(self._sales_next_page)
        self._purchases_prev_btn.clicked.connect(self._purchases_prev_page)
        self._purchases_next_btn.clicked.connect(self._purchases_next_page)
        self._expenses_prev_btn.clicked.connect(self._expenses_prev_page)
        self._expenses_next_btn.clicked.connect(self._expenses_next_page)

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------

    def _sales_prev_page(self):
        if self._sales_page > 0:
            self._sales_page -= 1
            self._render_sales_page()

    def _sales_next_page(self):
        total_pages = max(1, (len(self._sales_rows) + PAGE_SIZE - 1) // PAGE_SIZE)
        if self._sales_page < total_pages - 1:
            self._sales_page += 1
            self._render_sales_page()

    def _purchases_prev_page(self):
        if self._purchases_page > 0:
            self._purchases_page -= 1
            self._render_purchases_page()

    def _purchases_next_page(self):
        total_pages = max(1, (len(self._purchases_rows) + PAGE_SIZE - 1) // PAGE_SIZE)
        if self._purchases_page < total_pages - 1:
            self._purchases_page += 1
            self._render_purchases_page()

    def _expenses_prev_page(self):
        if self._expenses_page > 0:
            self._expenses_page -= 1
            self._render_expenses_page()

    def _expenses_next_page(self):
        total_pages = max(1, (len(self._expenses_rows) + PAGE_SIZE - 1) // PAGE_SIZE)
        if self._expenses_page < total_pages - 1:
            self._expenses_page += 1
            self._render_expenses_page()

    def _update_pagination(self, showing_lbl, prev_btn, page_btn, next_btn, page, total):
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        start = page * PAGE_SIZE + 1 if total > 0 else 0
        end = min((page + 1) * PAGE_SIZE, total)
        shown = end - start + 1 if total > 0 else 0
        showing_lbl.setText(f"Showing {shown} of {total}")
        page_btn.setText(str(page + 1))
        prev_btn.setEnabled(page > 0)
        next_btn.setEnabled(page < total_pages - 1)

    # ------------------------------------------------------------------
    # Filter helpers
    # ------------------------------------------------------------------

    def _on_filter_changed(self):
        is_custom = self.filter_combo.currentText() == "Custom"
        self.from_date.setEnabled(is_custom)
        self.to_date.setEnabled(is_custom)
        self.apply_btn.setEnabled(is_custom)
        if not is_custom:
            self._apply_filter()

    def _on_sales_search_changed(self):
        date_range = self._get_date_range()
        if date_range is None:
            return
        self._populate_sales_table(*date_range)

    def _on_purchases_search_changed(self):
        date_range = self._get_date_range()
        if date_range is None:
            return
        self._populate_purchases_table(*date_range)

    def _on_expense_filter_changed(self):
        date_range = self._get_date_range()
        if date_range is None:
            return
        self._populate_expenses_table(*date_range)

    def _get_date_range(self):
        today = date.today()
        preset = self.filter_combo.currentText()
        if preset == "Today":
            return str(today), str(today)
        elif preset == "Yesterday":
            y = today - timedelta(days=1)
            return str(y), str(y)
        elif preset == "This Week":
            start = today - timedelta(days=today.weekday())
            return str(start), str(today)
        elif preset == "This Month":
            return str(today.replace(day=1)), str(today)
        elif preset == "Custom":
            start = self.from_date.date().toPython()
            end = self.to_date.date().toPython()
            if start > end:
                QMessageBox.warning(self, "Invalid Range",
                    "The From date must be on or before the To date.")
                return None
            return str(start), str(end)

    def _apply_filter(self):
        date_range = self._get_date_range()
        if date_range is None:
            return
        start, end = date_range
        try:
            self.total_sales_label.setText(
                f"{report_logic.get_total_sales(start, end):,.2f}")
            self.total_purchases_label.setText(
                f"{report_logic.get_total_purchases(start, end):,.2f}")
            self.total_expenses_label.setText(
                f"{report_logic.get_total_expenses(start, end):,.2f}")
            total_profit = report_logic.get_total_profit(start, end)
            net_profit   = report_logic.get_net_profit_for_period(start, end)
            self.total_profit_label.setText(f"{total_profit:,.2f}")
            self.total_profit_label.setStyleSheet(
                f"font-weight: bold; background: transparent; border: none;"
                f" color: {theme.color_for_value(total_profit)};")
            self.net_profit_label.setText(f"{net_profit:,.2f}")
            self.net_profit_label.setStyleSheet(
                f"font-weight: bold; background: transparent; border: none;"
                f" color: {theme.color_for_value(net_profit)};")
            self._populate_history_tables(start, end)
            self._populate_top_products(start, end)
            self._reload_category_combo()
        except Exception:
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error", "Failed to load report data.")

    def _reload_category_combo(self):
        current = self.category_combo.currentText()
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")
        for cat in expenses_logic.get_categories():
            self.category_combo.addItem(cat)
        idx = self.category_combo.findText(current)
        self.category_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.category_combo.blockSignals(False)

    # ------------------------------------------------------------------
    # Table population
    # ------------------------------------------------------------------

    def _populate_history_tables(self, start_date, end_date):
        self._populate_sales_table(start_date, end_date)
        self._populate_purchases_table(start_date, end_date)
        self._populate_expenses_table(start_date, end_date)

    def _populate_sales_table(self, start_date, end_date):
        search = self.sales_search.text().strip() or None
        self._sales_rows = list(report_logic.get_sales_for_report(start_date, end_date, search))
        self._sales_page = 0
        self._render_sales_page()

    def _render_sales_page(self):
        rows = self._sales_rows
        page = self._sales_page
        start = page * PAGE_SIZE
        page_rows = rows[start:start + PAGE_SIZE]

        self.sales_table.setRowCount(0)
        for row in page_rows:
            r = self.sales_table.rowCount()
            self.sales_table.insertRow(r)
            inv_item = QTableWidgetItem(row["invoice_number"] or "")
            inv_item.setData(Qt.UserRole, row["id"])
            inv_item.setToolTip(row["invoice_number"] or "")
            self.sales_table.setItem(r, 0, inv_item)
            self.sales_table.setItem(r, 1, QTableWidgetItem((row["created_at"] or "")[:16]))
            cust = row["customer_name"] or ""
            cust_item = QTableWidgetItem(cust)
            cust_item.setToolTip(cust)
            self.sales_table.setItem(r, 2, cust_item)
            self.sales_table.setItem(r, 3, QTableWidgetItem(row["status"] or ""))
            self.sales_table.setItem(r, 4, QTableWidgetItem(f"{row['total_amount']:,.2f}"))

        search = self.sales_search.text().strip()
        has_rows = len(rows) > 0
        self.sales_table.setVisible(has_rows)
        if not has_rows and search:
            self._sales_empty_lbl.hide(); self._sales_empty_search_lbl.show()
        elif not has_rows:
            self._sales_empty_lbl.show(); self._sales_empty_search_lbl.hide()
        else:
            self._sales_empty_lbl.hide(); self._sales_empty_search_lbl.hide()

        self._update_pagination(
            self._sales_showing_lbl, self._sales_prev_btn,
            self._sales_page_btn, self._sales_next_btn, page, len(rows))

    def _populate_purchases_table(self, start_date, end_date):
        search = self.purchases_search.text().strip() or None
        self._purchases_rows = list(report_logic.get_purchases_for_report(start_date, end_date, search))
        self._purchases_page = 0
        self._render_purchases_page()

    def _render_purchases_page(self):
        rows = self._purchases_rows
        page = self._purchases_page
        start = page * PAGE_SIZE
        page_rows = rows[start:start + PAGE_SIZE]

        self.purchases_table.setRowCount(0)
        for row in page_rows:
            r = self.purchases_table.rowCount()
            self.purchases_table.insertRow(r)
            inv_item = QTableWidgetItem(row["invoice_number"] or "")
            inv_item.setData(Qt.UserRole, row["id"])
            inv_item.setToolTip(row["invoice_number"] or "")
            self.purchases_table.setItem(r, 0, inv_item)
            self.purchases_table.setItem(r, 1, QTableWidgetItem((row["created_at"] or "")[:16]))
            sup = row["supplier_name"] or ""
            sup_item = QTableWidgetItem(sup)
            sup_item.setToolTip(sup)
            self.purchases_table.setItem(r, 2, sup_item)
            self.purchases_table.setItem(r, 3, QTableWidgetItem(row["status"] or ""))
            self.purchases_table.setItem(r, 4, QTableWidgetItem(f"{row['total_amount']:,.2f}"))

        search = self.purchases_search.text().strip()
        has_rows = len(rows) > 0
        self.purchases_table.setVisible(has_rows)
        if not has_rows and search:
            self._purchases_empty_lbl.hide(); self._purchases_empty_search_lbl.show()
        elif not has_rows:
            self._purchases_empty_lbl.show(); self._purchases_empty_search_lbl.hide()
        else:
            self._purchases_empty_lbl.hide(); self._purchases_empty_search_lbl.hide()

        self._update_pagination(
            self._purchases_showing_lbl, self._purchases_prev_btn,
            self._purchases_page_btn, self._purchases_next_btn, page, len(rows))

    def _populate_expenses_table(self, start_date, end_date):
        cat_text = self.category_combo.currentText()
        category = None if cat_text == "All Categories" else cat_text
        search   = self.expense_search.text().strip() or None
        self._expenses_rows = list(
            expenses_logic.get_expenses_for_report(start_date, end_date, category, search))
        self._expenses_page = 0
        self._render_expenses_page()

    def _render_expenses_page(self):
        rows = self._expenses_rows
        page = self._expenses_page
        start = page * PAGE_SIZE
        page_rows = rows[start:start + PAGE_SIZE]

        self.expenses_table.setRowCount(0)
        for row in page_rows:
            r = self.expenses_table.rowCount()
            self.expenses_table.insertRow(r)
            id_item = QTableWidgetItem(row["invoice_number"] or "")
            id_item.setData(Qt.UserRole, row["id"])
            self.expenses_table.setItem(r, 0, id_item)
            self.expenses_table.setItem(r, 1, QTableWidgetItem(
                (row["expense_datetime"] or "")[:16]))
            items = expenses_logic.get_expense_items_by_invoice(row["id"])
            category = items[0]["category"] if items else ""
            description = items[0]["description"] if items else "-"
            self.expenses_table.setItem(r, 2, QTableWidgetItem(category or ""))
            self.expenses_table.setItem(r, 3, QTableWidgetItem(description or "-"))
            self.expenses_table.setItem(r, 4, QTableWidgetItem(
                f"{row['total_amount']:,.2f}"))

        search = self.expense_search.text().strip()
        has_rows = len(rows) > 0
        self.expenses_table.setVisible(has_rows)
        if not has_rows and search:
            self._expenses_empty_lbl.hide(); self._expenses_empty_search_lbl.show()
        elif not has_rows:
            self._expenses_empty_lbl.show(); self._expenses_empty_search_lbl.hide()
        else:
            self._expenses_empty_lbl.hide(); self._expenses_empty_search_lbl.hide()

        self._update_pagination(
            self._expenses_showing_lbl, self._expenses_prev_btn,
            self._expenses_page_btn, self._expenses_next_btn, page, len(rows))

    def _populate_top_products(self, start_date, end_date):
        self.top_sales_table.setRowCount(0)
        for row in report_logic.get_top_selling_products(start_date, end_date):
            r = self.top_sales_table.rowCount()
            self.top_sales_table.insertRow(r)
            self.top_sales_table.setItem(r, 0, QTableWidgetItem(row["product_name"] or ""))
            self.top_sales_table.setItem(r, 1, QTableWidgetItem(str(row["total_quantity"])))

        self.top_purchases_table.setRowCount(0)
        for row in report_logic.get_top_purchased_products(start_date, end_date):
            r = self.top_purchases_table.rowCount()
            self.top_purchases_table.insertRow(r)
            self.top_purchases_table.setItem(r, 0, QTableWidgetItem(row["product_name"] or ""))
            self.top_purchases_table.setItem(r, 1, QTableWidgetItem(str(row["total_quantity"])))

        self.top_expenses_table.setRowCount(0)
        for row in report_logic.get_top_expense_categories(start_date, end_date):
            r = self.top_expenses_table.rowCount()
            self.top_expenses_table.insertRow(r)
            self.top_expenses_table.setItem(r, 0, QTableWidgetItem(row["category"] or ""))
            self.top_expenses_table.setItem(r, 1, QTableWidgetItem(f"{row['total_amount']:,.2f}"))

    # ------------------------------------------------------------------
    # Double-click detail dialogs
    # ------------------------------------------------------------------

    def _on_sales_row_double_clicked(self, index):
        item = self.sales_table.item(index.row(), 0)
        if item is None:
            return
        invoice_id = item.data(Qt.UserRole)
        if invoice_id is None:
            return
        from ui.invoice_detail_dialog import InvoiceDetailDialog
        dlg = InvoiceDetailDialog("sale", invoice_id, parent=self)
        dlg.exec()
        self._apply_filter()

    def _on_purchases_row_double_clicked(self, index):
        item = self.purchases_table.item(index.row(), 0)
        if item is None:
            return
        invoice_id = item.data(Qt.UserRole)
        if invoice_id is None:
            return
        from ui.invoice_detail_dialog import InvoiceDetailDialog
        dlg = InvoiceDetailDialog("purchase", invoice_id, parent=self)
        dlg.exec()
        self._apply_filter()

    def _on_expenses_row_double_clicked(self, index):
        item = self.expenses_table.item(index.row(), 0)
        if item is None:
            return
        invoice_id = item.data(Qt.UserRole)
        if invoice_id is None:
            return
        from ui.expense_detail_dialog import ExpenseDetailDialog
        dlg = ExpenseDetailDialog(invoice_id, parent=self)
        dlg.exec()

    # ------------------------------------------------------------------
    # CSV export
    # ------------------------------------------------------------------

    def _on_export_csv(self):
        if self._last_active_table == "sales":
            table = self.sales_table
        elif self._last_active_table == "purchases":
            table = self.purchases_table
        else:
            table = self.expenses_table

        path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            headers = [table.horizontalHeaderItem(c).text()
                       for c in range(table.columnCount())]
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for r in range(table.rowCount()):
                    row_data = [table.item(r, c).text() if table.item(r, c) else ""
                                for c in range(table.columnCount())]
                    writer.writerow(row_data)
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "Exported", f"File saved to:\n{path}")
        except Exception:
            QApplication.restoreOverrideCursor()
            print(traceback.format_exc())
            QMessageBox.critical(self, "Export Failed",
                "An error occurred while exporting. Check permissions and disk space.")

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_filter()
