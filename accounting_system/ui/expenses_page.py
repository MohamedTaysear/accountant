import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDateTimeEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QApplication, QCompleter, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont, QColor

from logic import expenses_logic
from ui import theme

_CAIRO = ZoneInfo("Africa/Cairo")


def _fmt(v: float) -> str:
    s = f"{v:.2f}"
    return s.rstrip("0").rstrip(".")


def _fmt_total(v: float) -> str:
    s = f"{v:,.2f}"
    if "." in s:
        integer_part, frac_part = s.split(".")
        frac_part = frac_part.rstrip("0")
        return integer_part if not frac_part else f"{integer_part}.{frac_part}"
    return s


def _cairo_now_qdatetime() -> QDateTime:
    now = datetime.now(_CAIRO)
    return QDateTime(now.year, now.month, now.day,
                     now.hour, now.minute, now.second)


class ExpensesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._build_ui()
        self._refresh_invoice_number()

    def _build_ui(self):
        t = theme._active
        layout = QVBoxLayout(self)
        layout.setContentsMargins(t.spacing_xl, t.spacing_xl, t.spacing_xl, t.spacing_xl)
        layout.setSpacing(t.spacing_lg)

        # ── Page header ──────────────────────────────────────────────
        page_title = QLabel("💸 New Expense Invoice")
        title_font = QFont(t.font_family, t.size_page_title)
        title_font.setBold(True)
        page_title.setFont(title_font)
        page_title.setStyleSheet(f"color: {t.text_primary}; background: transparent; font-weight: 700;")
        layout.addWidget(page_title)

        # ── Invoice header card ──────────────────────────────────────
        header_card = QFrame()
        header_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        header_card.setGraphicsEffect(theme.make_card_shadow())
        hc_layout = QHBoxLayout(header_card)
        hc_layout.setContentsMargins(t.spacing_xl, t.spacing_md, t.spacing_xl, t.spacing_md)

        header_form = QFormLayout()
        header_form.setSpacing(t.spacing_md)
        header_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.invoice_number_label = QLabel("EXP-000001")
        self.invoice_number_label.setStyleSheet(
            f"font-weight: 700; font-size: {t.size_section}pt; color: {t.primary}; background: transparent;")
        header_form.addRow("Invoice #:", self.invoice_number_label)

        self.dt_edit = QDateTimeEdit()
        self.dt_edit.setCalendarPopup(True)
        self.dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dt_edit.setDateTime(_cairo_now_qdatetime())
        self.dt_edit.setMinimumWidth(180)
        self.dt_edit.setStyleSheet(
            f"QDateTimeEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px; background: {t.background}; }}"
        )
        header_form.addRow("Date & Time:", self.dt_edit)

        hc_layout.addLayout(header_form)
        hc_layout.addStretch()
        header_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(header_card)

        # ── Add item card ────────────────────────────────────────────
        add_card = QFrame()
        add_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        add_card.setGraphicsEffect(theme.make_card_shadow())
        add_card_outer = QVBoxLayout(add_card)
        add_card_outer.setContentsMargins(t.spacing_lg, t.spacing_md, t.spacing_lg, t.spacing_md)
        add_card_outer.setSpacing(t.spacing_sm)

        def _lbl(lbl_text):
            l = QLabel(lbl_text)
            l.setStyleSheet(f"color: {t.text_secondary}; background: transparent; font-weight: 500;")
            return l

        row1 = QHBoxLayout()
        row1.setSpacing(t.spacing_md)
        row1.setAlignment(Qt.AlignVCenter)

        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setInsertPolicy(QComboBox.NoInsert)
        self.category_combo.setMinimumWidth(180)
        self.category_combo.setStyleSheet(
            f"QComboBox {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px; background: {t.background}; }}"
        )

        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("0.00")
        self.amount_edit.setFixedWidth(410)
        self.amount_edit.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px 12px; background: {t.background}; }}"
        )

        row1.addWidget(_lbl("Category:"))
        row1.addWidget(self.category_combo, 1)
        row1.addSpacing(t.spacing_sm)
        row1.addWidget(_lbl("Amount:"))
        row1.addWidget(self.amount_edit)
        add_card_outer.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(t.spacing_md)
        row2.setAlignment(Qt.AlignVCenter)

        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Optional description")
        self.description_edit.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px 12px; background: {t.background}; }}"
        )

        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional notes")
        self.notes_edit.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {t.border}; border-radius: 8px; padding: 6px 12px; background: {t.background}; }}"
        )

        self.add_line_btn = QPushButton("➕ Add Line")
        self.add_line_btn.setProperty("class", "primary")
        self.add_line_btn.setCursor(Qt.PointingHandCursor)

        row2.addWidget(_lbl("Description:"))
        row2.addWidget(self.description_edit, 3)
        row2.addWidget(_lbl("Notes:"))
        row2.addWidget(self.notes_edit, 1)
        row2.addWidget(self.add_line_btn)
        add_card_outer.addLayout(row2)

        add_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(add_card)

        # ── Line items table ─────────────────────────────────────────
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(
            ["Category", "Description", "Amount", "Notes", "Actions"])
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for col, w in [(0, 140), (2, 120), (3, 160), (4, 100)]:
            self.items_table.setColumnWidth(col, w)
        theme.apply_table_style(self.items_table)
        self._empty_table_lbl = theme.make_empty_label(
            "No expense lines added to this invoice yet.")
        layout.addWidget(self.items_table)
        layout.addWidget(self._empty_table_lbl)
        self._empty_table_lbl.hide()

        # ── Footer ──────────────────────────────────────────────────
        footer_card = QFrame()
        footer_card.setStyleSheet(
            f"QFrame {{ background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px; }}")
        footer_card.setGraphicsEffect(theme.make_card_shadow())
        footer = QHBoxLayout(footer_card)
        footer.setContentsMargins(t.spacing_lg, t.spacing_lg, t.spacing_lg, t.spacing_lg)
        footer.setSpacing(t.spacing_md)

        self.total_label = QLabel("Total: 0.00")
        total_font = QFont(t.font_family, t.size_kpi_value)
        total_font.setBold(True)
        self.total_label.setFont(total_font)
        self.total_label.setStyleSheet(
            f"color: {t.primary}; background: transparent; font-weight: 700;")

        self.clear_btn = QPushButton("🧹 Clear Invoice")
        self.clear_btn.setProperty("class", "destructive")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        
        self.save_btn  = QPushButton("💾 Save Invoice")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setMinimumWidth(150)

        footer.addStretch()
        footer.addWidget(self.total_label)
        footer.addSpacing(t.spacing_xl)
        footer.addWidget(self.clear_btn)
        footer.addWidget(self.save_btn)
        footer_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(footer_card)
        layout.addStretch()

        # ── Signals ─────────────────────────────────────────────────
        self.add_line_btn.clicked.connect(self._on_add_line)
        self.clear_btn.clicked.connect(self._on_clear)
        self.save_btn.clicked.connect(self._on_save)

    # ── Lifecycle ───────────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self._reload_categories()

    def _refresh(self):
        self._reload_categories()
        self._refresh_invoice_number()

    # ── Form helpers ────────────────────────────────────────────────

    def _refresh_invoice_number(self):
        try:
            self.invoice_number_label.setText(
                expenses_logic.get_next_invoice_number())
        except Exception:
            self.invoice_number_label.setText("EXP-??????")

    def _reload_categories(self):
        current = self.category_combo.currentText()
        categories = expenses_logic.get_categories()
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItems(categories)
        completer = QCompleter(categories, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.category_combo.setCompleter(completer)
        self.category_combo.setCurrentText(current)
        self.category_combo.blockSignals(False)

    def _update_total(self):
        total = sum(item["amount"] for item in self._items)
        self.total_label.setText(f"Total: {_fmt_total(total)}")

    def _rebuild_items_table(self):
        self.items_table.setRowCount(0)
        t = theme._active
        for idx, item in enumerate(self._items):
            r = self.items_table.rowCount()
            self.items_table.insertRow(r)

            def _item(text):
                it = QTableWidgetItem(text)
                it.setToolTip(text)
                return it
                
            cat_item = _item(item["category"])
            cat_item.setFont(QFont(t.font_family, t.size_normal, QFont.Bold))

            self.items_table.setItem(r, 0, cat_item)
            self.items_table.setItem(r, 1, _item(item["description"]))
            
            amt_item = _item(_fmt(item["amount"]))
            amt_item.setFont(QFont(t.font_family, t.size_normal, QFont.Bold))
            
            self.items_table.setItem(r, 2, amt_item)
            self.items_table.setItem(r, 3, _item(item["notes"]))
            
            cell_widget = QWidget()
            btn_layout = QHBoxLayout(cell_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            remove_btn = QPushButton("❌ Remove")
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet(
                f"QPushButton {{ background-color: {t.surface_alt}; color: {t.error};"
                f" border: 1px solid {t.border}; border-radius: 6px; padding: 4px 8px; font-weight: 500; }}"
                f"QPushButton:hover {{ background-color: {t.error}; color: white; border: none; }}"
            )
            remove_btn.clicked.connect(
                lambda checked=False, i=idx: self._on_remove_line(i))
            btn_layout.addWidget(remove_btn)
            self.items_table.setCellWidget(r, 4, cell_widget)
            
        has_rows = self.items_table.rowCount() > 0
        self.items_table.setVisible(has_rows)
        self._empty_table_lbl.setVisible(not has_rows)

    def _reset_form(self):
        self._items = []
        self.category_combo.clearEditText()
        self.description_edit.clear()
        self.amount_edit.clear()
        self.notes_edit.clear()
        self._rebuild_items_table()
        self._update_total()
        self._refresh_invoice_number()

    # ── Signal Handlers ─────────────────────────────────────────────

    def _on_add_line(self):
        category = self.category_combo.currentText().strip()
        description = self.description_edit.text().strip()
        notes = self.notes_edit.text().strip()
        raw_amount = self.amount_edit.text().strip().replace(",", "")

        errors = expenses_logic.validate_expense_item(category, raw_amount)
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        self._items.append({
            "category":    category,
            "description": description,
            "amount":      float(raw_amount),
            "notes":       notes,
        })
        self._rebuild_items_table()
        self._update_total()

        self.category_combo.clearEditText()
        self.description_edit.clear()
        self.amount_edit.clear()
        self.notes_edit.clear()
        self.category_combo.setFocus()

    def _on_remove_line(self, index: int):
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self._rebuild_items_table()
            self._update_total()

    def _on_clear(self):
        if self._items:
            answer = QMessageBox.question(
                self, "Clear Invoice",
                "Are you sure you want to clear this invoice?\n"
                "All unsaved expense lines will be lost.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return
        self._reset_form()

    def _on_save(self):
        if not self._items:
            QMessageBox.warning(self, "Empty Invoice",
                "Invoice must have at least one expense line before saving.")
            return

        expense_datetime = self.dt_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            invoice_number = expenses_logic.save_expense_invoice(
                expense_datetime, self._items)
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "Saved",
                f"Expense invoice {invoice_number} saved successfully.")
            self._reset_form()
            self._reload_categories()
            self.category_combo.setFocus()
        except ValueError as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Cannot Save", str(e))
        except Exception:
            QApplication.restoreOverrideCursor()
            print(traceback.format_exc())
            QMessageBox.critical(self, "Unexpected Error",
                "An unexpected error occurred while saving. Please try again.\n"
                "Your invoice data has been preserved.")
