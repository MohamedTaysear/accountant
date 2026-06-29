                # Tasks: Design System & UI Modernization

                **Input**: Design documents from `specs/007-design-system/`

                **References**:
                - `specs/007-design-system/plan.md` — tech stack, file structure
                - `specs/007-design-system/spec.md` — user stories (US1–US5)
                - `specs/007-design-system/data-model.md` — ThemeDefinition token vocabulary + LightTheme values
                - `specs/007-design-system/contracts/theme_module.md` — exact function contracts for theme.py
                - `specs/007-design-system/contracts/screen_styling.md` — per-screen styling rules
                - `specs/007-design-system/quickstart.md` — manual validation guide
                - `.specify/memory/constitution.md` — architecture rules (UI layer only; no new packages)

                **No tests** — this is a visual-only phase. Validation is manual per quickstart.md.

                **Critical rule**: Screen files MUST NOT import `LightTheme`, `ThemeDefinition`, or access `theme._active`. They call only module-level functions: `theme.apply_table_style()`, `theme.color_for_value()`, `theme.make_empty_label()`, `theme.make_card_shadow()`.

                ---

                ## Phase 1: Setup

                **Purpose**: Create the two new files/directories. No screen files are touched here.

                - [ ] T001 Create `accounting_system/ui/theme.py` — define `ThemeDefinition` base class and `LightTheme(ThemeDefinition)` subclass with all token attributes. See exact token names and values in `specs/007-design-system/data-model.md` (LightTheme Values table). Structure: `class ThemeDefinition:` with all tokens as class attributes set to empty/zero defaults; `class LightTheme(ThemeDefinition):` overriding all attributes with the Light palette hex values and numeric constants. Do NOT implement the module-level functions yet — that is T003.

                - [ ] T002 [P] Create directory `accounting_system/ui/icons/` and add 6 minimal SVG icon files: `dashboard.svg`, `products.svg`, `sales.svg`, `purchases.svg`, `expenses.svg`, `reports.svg`. Each SVG should be a simple 24×24 monochrome icon representing the page (e.g. a grid for dashboard, a box for products, a receipt for sales/purchases/expenses, a chart for reports). Use basic SVG path shapes only — no external dependencies.

                ---

                ## Phase 2: Foundational (Blocking Prerequisite)

                **Purpose**: Complete `theme.py` with all helper functions, then wire the global stylesheet into `main.py`. MUST be done before any screen file is modified.

                **⚠️ CRITICAL**: No user story work can begin until this phase is complete.

                - [ ] T003 Add all module-level state and functions to `accounting_system/ui/theme.py` (after the class definitions from T001). Implement exactly these symbols — see `specs/007-design-system/contracts/theme_module.md` for the full contract:

                1. `_active: ThemeDefinition = LightTheme()` — module-level variable
                2. `def set_theme(t: ThemeDefinition) -> None:` — sets global `_active`
                3. `class ElidingDelegate(QStyledItemDelegate):` — overrides `paint()` to draw text with `Qt.ElideRight` using `option.fontMetrics.elidedText(text, Qt.ElideRight, option.rect.width() - 2 * _active.spacing_md)`. Import: `from PySide6.QtWidgets import QStyledItemDelegate, QAbstractItemView`; `from PySide6.QtCore import Qt`
                4. `def build_app_stylesheet() -> str:` — returns a multiline QSS f-string using `_active` token attributes. Must cover: `QWidget`, `QPushButton` (default, `[class="primary"]`, `[class="destructive"]`, `:disabled`), `QLineEdit` (and `:focus`), `QComboBox` (and `:focus`), `QDateTimeEdit`, `QDoubleSpinBox`, `QGroupBox`, `QDialog`, `QScrollBar:vertical`, `QTableWidget`, `QHeaderView::section`, `QTableWidget::item`, `QTableWidget::item:selected`, `QTableWidget::item:alternate`. See coverage table in `contracts/theme_module.md`.
                5. `def apply_table_style(table) -> None:` — calls: `table.setAlternatingRowColors(True)`, `table.verticalHeader().setDefaultSectionSize(_active.table_row_height)`, `table.verticalHeader().setVisible(False)`, `table.setShowGrid(True)`, `table.setSelectionBehavior(QAbstractItemView.SelectRows)`, `table.setEditTriggers(QAbstractItemView.NoEditTriggers)`, `table.horizontalHeader().setHighlightSections(False)`, `table.setItemDelegate(ElidingDelegate(table))`
                6. `def make_empty_label(message: str) -> QLabel:` — returns a `QLabel(message)` with `setAlignment(Qt.AlignCenter)`, italic font at `_active.size_normal` pt, color set via `setStyleSheet(f"color: {_active.text_secondary}; font-style: italic;")`
                7. `def make_card_shadow():` — returns `QGraphicsDropShadowEffect` with `blurRadius=_active.shadow_blur`, `offset=QPointF(0, _active.shadow_offset_y)`, `color=QColor(0, 0, 0, 26)`. Import: `from PySide6.QtWidgets import QGraphicsDropShadowEffect`; `from PySide6.QtCore import QPointF`; `from PySide6.QtGui import QColor`
                8. `def color_for_value(value: float) -> str:` — returns `_active.success` if `value > 0`, `_active.error` if `value < 0`, `_active.text_primary` otherwise

                - [ ] T004 Modify `accounting_system/main.py` — add three lines inside `main()` before `window = LoginWindow()`: `from ui import theme` (at top of file), `from ui.theme import LightTheme` (at top of file), then inside `main()`: `theme.set_theme(LightTheme())`, then `app.setFont(QFont(theme._active.font_family, theme._active.size_normal))` (add `QFont` to PySide6 imports), then `app.setStyleSheet(theme.build_app_stylesheet())`. This is the only place in the entire codebase that calls `setStyleSheet()` at the application level.

                **Checkpoint**: Launch `python main.py` from `accounting_system/`. The login window must open with a visible blue Login button and styled input fields. No console errors about stylesheet syntax.

                ---

                ## Phase 3: User Story 1 — Consistent Visual Identity (Priority: P1) 🎯 MVP

                **Goal**: Every screen uses the global stylesheet. Login window and sidebar use theme-consistent styling with nav icons.

                **Independent Test**: Launch the app. Verify: login button is blue, sidebar is dark, all 6 nav buttons show icons, active page has a highlight.

                ### Implementation

                - [ ] T005 [US1] Modify `accounting_system/ui/login_window.py` — apply the Primary button style to the Login button: `self.btn_login.setProperty("class", "primary"); self.btn_login.style().unpolish(self.btn_login); self.btn_login.style().polish(self.btn_login)`. For the error label (shown on bad credentials): add `from ui import theme` and wrap error label color in `self.lbl_error.setStyleSheet(f"color: {theme._active.error};")`. Remove any existing hardcoded `setStyleSheet` calls on the login button or input fields — the global QSS now handles those.

                - [ ] T006 [US1] Modify `accounting_system/ui/main_window.py` — add nav icons to each sidebar navigation button. At the top of the file, add: `from PySide6.QtGui import QIcon` and `import os`. For each nav button (Dashboard, Products, Sales, Purchases, Expenses, Reports), load the corresponding SVG from `ui/icons/`: `icon_path = os.path.join(os.path.dirname(__file__), "icons", "dashboard.svg")` then `btn.setIcon(QIcon(icon_path))`. Apply the active nav item highlight by setting a QSS property on the active button: `btn.setProperty("class", "nav-active")` for the currently selected page button; clear this property on previously active button. Remove any existing per-button `setStyleSheet` calls on sidebar buttons — the global QSS now handles base styling.

                **Checkpoint**: All 6 sidebar buttons show SVG icons. Active page button has visible highlight. No per-widget `setStyleSheet` calls remain on nav buttons.

                ---

                ## Phase 4: User Story 2 — Standardized Tables and Data Display (Priority: P2)

                **Goal**: Every table in the application uses `theme.apply_table_style()`. Every table has a proper empty-state label shown when it has zero rows.

                **Independent Test**: Open Products (with data), then search for "zzzz". Table disappears; "No results match your search." appears. Clear search — table returns. Works identically on Sales/Purchases/Expenses/Reports history tables.

                **Pattern to apply to every table**:

                ```python
                # After constructing each QTableWidget:
                from ui import theme
                theme.apply_table_style(self.tbl_whatever)

                # After building each table: construct and store the empty-state label:
                self._empty_lbl_whatever = theme.make_empty_label("No products added yet.")
                layout.addWidget(self._empty_lbl_whatever)
                self._empty_lbl_whatever.hide()

                # In the data-populating method, after filling the table:
                has_rows = self.tbl_whatever.rowCount() > 0
                self.tbl_whatever.setVisible(has_rows)
                self._empty_lbl_whatever.setVisible(not has_rows)

                # For all QTableWidgetItem cells containing text:
                item = QTableWidgetItem(display_text)
                item.setToolTip(full_value)  # same as display_text if short; full untruncated value always
                self.tbl_whatever.setItem(row, col, item)
                ```

                For search-result empty states, use a second label: `self._empty_search_lbl = theme.make_empty_label("No results match your search.")` — show this one (and hide the no-data label) when a search is active and returns 0 rows.

                - [ ] T007 [US2] Modify `accounting_system/ui/products_page.py` — apply `theme.apply_table_style(self.tbl_products)` after table construction. Add two empty-state labels: `self._empty_lbl` ("No products added yet.") for no-data state; `self._empty_search_lbl` ("No results match your search.") for empty search state. In `_load_products()`: after populating, show/hide correctly based on row count and whether search text is present. Add `item.setToolTip(full_value)` for all text columns (name, description, category). Remove any existing `setAlternatingRowColors`, `setShowGrid`, or per-table `setStyleSheet` calls — `apply_table_style` handles these.

                - [ ] T008 [US2] Modify `accounting_system/ui/sales_page.py` — apply `theme.apply_table_style()` to the in-progress line-items table. Add one empty-state label: `theme.make_empty_label("No items added to this invoice yet.")`. Show it when `self._items` is empty; hide it when items are present. Add `item.setToolTip(full_value)` for Description and Product columns. Remove any existing per-table `setStyleSheet` or alternating row calls.

                - [ ] T009 [US2] Modify `accounting_system/ui/purchases_page.py` — same pattern as T008. Empty state message: `"No items added to this invoice yet."`. Apply `theme.apply_table_style()` to the in-progress items table.

                - [ ] T010 [US2] Modify `accounting_system/ui/expenses_page.py` — same pattern as T008. Empty state message: `"No expense lines added to this invoice yet."`. Apply `theme.apply_table_style()` to the in-progress items table.

                - [ ] T011 [US2] Modify `accounting_system/ui/reports_page.py` — apply `theme.apply_table_style()` to all three history tables (Sales, Purchases, Expenses). Add two empty-state labels per table (no-data and search-empty), correctly shown/hidden when the table is populated. Add `item.setToolTip(full_value)` for all text columns. Apply `theme.color_for_value(net_profit)` to profit/net-profit summary labels: `lbl.setStyleSheet(f"color: {theme.color_for_value(value)}; font-weight: bold;")`.

                - [ ] T012 [US2] Modify `accounting_system/ui/invoice_detail_dialog.py` — apply `theme.apply_table_style()` to the line-items table inside the dialog. Add `item.setToolTip(full_value)` for all text columns. Apply `theme.color_for_value()` to the net total label.

                - [ ] T013 [US2] Modify `accounting_system/ui/expense_detail_dialog.py` — apply `theme.apply_table_style()` to the items table. Add `item.setToolTip(full_value)` for all text columns.

                - [ ] T014 [US2] Modify `accounting_system/ui/dashboard_page.py` (low-stock table only) — apply `theme.apply_table_style()` to the low-stock table. Add one empty-state label: `theme.make_empty_label("No products are currently low on stock.")`. Show it when low-stock table has 0 rows. Add `item.setToolTip(full_value)` for the product name column.

                **Checkpoint**: Open Products page. The table header is bold, rows alternate colors, row height is uniform. Add a very long product name → it truncates with "…" → hover shows full name. Search for nonsense → "No results match your search." appears. Clear search → table returns.

                ---

                ## Phase 5: User Story 3 — Consistent Buttons and Interactive Controls (Priority: P3)

                **Goal**: Every primary-action button is blue; every destructive-action button is red; every input field shows a blue focus ring when clicked. No per-button `setStyleSheet` calls for colors.

                **Independent Test**: Click Save Invoice on Sales page, Purchases page, and Expenses page — all three buttons must be visually identical. Click Delete on Products page — red button. Tab through form fields — focus ring visible on each.

                **Pattern to apply to all buttons**:

                ```python
                # Primary action (Save, Add, Confirm, Login):
                btn.setProperty("class", "primary")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

                # Destructive action (Delete, Void, Clear Invoice):
                btn.setProperty("class", "destructive")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

                # Secondary/neutral (Cancel, Close, Export CSV) — no property needed:
                # default QSS handles these
                ```

                - [ ] T015 [US3] Modify `accounting_system/ui/products_page.py` — set `class="primary"` on Add Product button; `class="destructive"` on Delete and Deactivate buttons. Remove any per-button color `setStyleSheet` calls on these buttons.

                - [ ] T016 [US3] [P] Modify `accounting_system/ui/product_dialog.py` — set `class="primary"` on Save button. Remove per-button `setStyleSheet` on Save if present.

                - [ ] T017 [US3] [P] Modify `accounting_system/ui/sales_page.py` — set `class="primary"` on "Add to Invoice" and "Save Invoice" buttons; `class="destructive"` on "Clear Invoice" button. Remove any per-button color `setStyleSheet` calls.

                - [ ] T018 [US3] [P] Modify `accounting_system/ui/purchases_page.py` — same as T017: primary on "Add to Invoice" and "Save Invoice"; destructive on "Clear Invoice".

                - [ ] T019 [US3] [P] Modify `accounting_system/ui/expenses_page.py` — same as T017: primary on "Add to Invoice" and "Save Invoice"; destructive on "Clear Invoice".

                - [ ] T020 [US3] [P] Modify `accounting_system/ui/reports_page.py` — set `class="primary"` on Apply/filter buttons if any; Export CSV button uses no class (secondary/neutral). For any profit/loss colored labels not yet handled in T011, apply `theme.color_for_value()`.

                - [ ] T021 [US3] [P] Modify `accounting_system/ui/invoice_detail_dialog.py` — set `class="destructive"` on Void button. Close/Print buttons: no class (secondary/neutral). Remove per-button `setStyleSheet` color calls.

                - [ ] T022 [US3] [P] Modify `accounting_system/ui/expense_detail_dialog.py` — Close button: no class. Remove per-button `setStyleSheet` color calls.

                - [ ] T023 [US3] [P] Modify `accounting_system/ui/change_password_dialog.py` — set `class="primary"` on Save button. Error label (mismatched passwords): `lbl_error.setStyleSheet(f"color: {theme._active.error};")`. Remove per-button color `setStyleSheet` calls.

                **Checkpoint**: Launch app. Navigate to Sales page. "Save Invoice" is blue. "Clear Invoice" is red. Tab through Category, Description, Amount, Notes fields — each shows a blue border when focused. Same blue border appears on all inputs across all pages.

                ---

                ## Phase 6: User Story 4 — Modernized Dashboard Cards (Priority: P4)

                **Goal**: All KPI cards share identical padding, border radius, drop shadow, and typography. Profit/loss values are color-coded using the theme.

                **Independent Test**: Open Dashboard. All cards look identical in structure. Any profit card with a positive value shows green text; if negative, red text.

                - [ ] T024 [US4] Modify `accounting_system/ui/dashboard_page.py` — rewrite the `_make_card()` helper function to use theme values and drop shadow:

                ```python
                def _make_card(title: str, value_label: QLabel) -> QFrame:
                    from ui import theme
                    frame = QFrame()
                    frame.setFrameShape(QFrame.StyledPanel)
                    frame.setGraphicsEffect(theme.make_card_shadow())
                    frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    frame.setStyleSheet(
                        f"QFrame {{ background-color: {theme._active.surface};"
                        f" border: 1px solid {theme._active.border};"
                        f" border-radius: {theme._active.card_border_radius}px; }}"
                    )
                    layout = QVBoxLayout(frame)
                    layout.setContentsMargins(theme._active.spacing_lg, theme._active.spacing_md,
                                                theme._active.spacing_lg, theme._active.spacing_md)
                    title_lbl = QLabel(title)
                    title_lbl.setAlignment(Qt.AlignCenter)
                    title_lbl.setStyleSheet(
                        f"font-size: {theme._active.size_kpi_label}pt;"
                        f" color: {theme._active.text_secondary};"
                        f" border: none;"
                    )
                    value_label.setAlignment(Qt.AlignCenter)
                    value_label.setStyleSheet(
                        f"font-size: {theme._active.size_kpi_value}pt;"
                        f" font-weight: bold; border: none;"
                    )
                    layout.addWidget(title_lbl)
                    layout.addWidget(value_label)
                    return frame
                ```

                - [ ] T025 [US4] Modify `accounting_system/ui/dashboard_page.py` `_refresh()` method — apply `theme.color_for_value()` to all profit and net-profit KPI labels after their values are set. Identify which labels are profit-related (today_profit, this_month_profit, total_profit, net_profit, today_net_profit, this_month_net_profit, potential_profit) and call: `lbl.setStyleSheet(f"font-size: {theme._active.size_kpi_value}pt; font-weight: bold; border: none; color: {theme.color_for_value(numeric_value)};")` for each. For neutral metric labels (total_products, active_products, etc.), no color override is needed — the global QSS handles them.

                **Checkpoint**: Open Dashboard. All cards have equal padding and a visible drop shadow. Profit card: if sales > purchases, text is green; if expenses exceed profit, text may be red.

                ---

                ## Phase 7: User Story 5 — Accessible and Comfortable (Priority: P5)

                **Goal**: Spacing scale applied, WCAG contrast verified, focus indicators working, all screens pass quickstart.md validation.

                **Independent Test**: Run through the full Section 8 regression checklist in `specs/007-design-system/quickstart.md`.

                - [ ] T026 [US5] Verify and fix spacing consistency across all form layouts — in any page or dialog where `setContentsMargins` or `setSpacing` takes hardcoded integers, replace with `theme._active.spacing_*` values. Specifically: form layout margins should use `spacing_lg` (16px); inner layout spacing should use `spacing_sm` (8px); card interior should use `spacing_md/spacing_lg` per the contract. In `accounting_system/ui/`: check `login_window.py`, `product_dialog.py`, `change_password_dialog.py`, `invoice_detail_dialog.py`, `expense_detail_dialog.py`. Replace hardcoded pixel values with `theme._active.spacing_lg` etc.

                - [ ] T027 [US5] Audit all remaining `setStyleSheet()` calls across all UI files — search for any hardcoded hex color strings (e.g. `"#"`) remaining in UI files outside of `theme.py`. For each found: replace with the corresponding `theme._active.*` attribute or move the styling into `build_app_stylesheet()`. The only acceptable per-widget `setStyleSheet` calls remaining after this audit are: profit/loss colored labels (which use `theme.color_for_value()`), the sidebar card frame border (which uses `theme._active.surface`), and the KPI card `QFrame` stylesheet (which uses `theme._active.*` tokens). Any hardcoded color literal remaining in a screen file is a bug.

                - [ ] T028 [US5] Verify WCAG AA contrast is maintained — the `LightTheme` palette was selected to meet 4.5:1 for normal text. This task is a verification step: check that no screen overrides text color with a value that would fail contrast. Specifically look for any `color: #` in remaining per-widget stylesheets and verify the color is from the theme palette (which is WCAG compliant). No code changes needed if audit passes; fix any found violations by using the correct theme color.

                ---

                ## Phase 8: Polish & Cross-Cutting Concerns

                - [ ] T029 [P] Remove `expenses_report_page.py` and `expense_dialog.py` from the UI if these files are unused dead code (check that they are not imported anywhere in the codebase). If imported, apply theme styling to them. If orphaned, delete them to reduce maintenance burden. Run a grep for their import in all `*.py` files first.

                - [ ] T030 Run the manual validation guide — work through all 8 sections of `specs/007-design-system/quickstart.md` and confirm every section passes. Record any visual regression discovered. Fix any regressions before marking this phase complete.

                - [ ] T031 [P] Clean up remaining dead code — search for `from PySide6.QtGui import QColor` in screen files; if `QColor` is only used for old hardcoded color calls that were replaced by the theme, remove the import. Same for `from PySide6.QtGui import QFont` where the font was replaced by the global stylesheet. Keep only imports that are still actively used.

                ---

                ## Dependencies & Execution Order

                ### Phase Dependencies

                - **Phase 1 (Setup)**: No dependencies — start immediately. T001 and T002 can run in parallel.
                - **Phase 2 (Foundational)**: T003 depends on T001. T004 depends on T003. BLOCKS all user story phases.
                - **Phase 3 (US1)**: T005 and T006 can run in parallel after Phase 2.
                - **Phase 4 (US2)**: T007–T014 can all run in parallel after Phase 2 (different files). T011 (reports_page) is the most complex; do it last within the phase.
                - **Phase 5 (US3)**: T015–T023 can all run in parallel after Phase 2. Several touch the same files as Phase 4; if working sequentially, combine Phase 4 and Phase 5 edits per-file to avoid re-opening files.
                - **Phase 6 (US4)**: T024 and T025 are in the same file (dashboard_page.py) — run sequentially.
                - **Phase 7 (US5)**: T026–T028 depend on all screen files being updated (run after Phases 3–6).
                - **Phase 8 (Polish)**: Run last.

                ### Within Each Phase

                - Models before services before UI is not applicable here — this is visual-only. The order within each phase is: theme.py functions first, then screen files.
                - When editing a screen file that has BOTH table styling (Phase 4) and button styling (Phase 5) work, do both edits in one pass rather than opening the file twice.

                ### Recommended Single-Developer Execution Order

                1. T001 → T002 (parallel)
                2. T003 → T004
                3. **Checkpoint**: App launches with styled login window
                4. T005, T006 (parallel)
                5. T007, T008, T009, T010 (parallel — different files)
                6. T011, T012, T013, T014 (parallel — different files)
                7. **Checkpoint**: All tables styled; empty states working
                8. T015 through T023 (parallel — different files)
                9. **Checkpoint**: All buttons primary/destructive; focus rings visible
                10. T024 → T025
                11. **Checkpoint**: Dashboard cards have shadow + profit color
                12. T026, T027, T028
                13. T029, T030, T031
                14. **Final Checkpoint**: All 8 quickstart.md sections pass

                ---

                ## Parallel Execution Example: Phase 4 (Tables)

                All of these can run simultaneously since they modify different files:

                ```
                Task A: products_page.py   → apply_table_style + empty labels + tooltips
                Task B: sales_page.py      → apply_table_style + empty label + tooltips
                Task C: purchases_page.py  → apply_table_style + empty label + tooltips
                Task D: expenses_page.py   → apply_table_style + empty label + tooltips
                Task E: reports_page.py    → apply_table_style × 3 + empty labels + color_for_value
                Task F: invoice_detail_dialog.py → apply_table_style + color_for_value
                Task G: expense_detail_dialog.py → apply_table_style
                Task H: dashboard_page.py  → apply_table_style (low-stock table only)
                ```

                ---

                ## Implementation Strategy

                ### MVP (Phase 1 + 2 + 3 only)

                1. Complete Phase 1 (theme.py skeleton)
                2. Complete Phase 2 (all functions + main.py wiring)
                3. Complete Phase 3 (login + sidebar)
                4. **STOP and VALIDATE**: Global stylesheet applies; login and sidebar look professional
                5. Proceed to Phase 4 if MVP checkpoint passes

                ### Incremental Delivery

                Each phase produces a demoable increment:
                - After Phase 2: App launches with consistent fonts, button colors, input borders
                - After Phase 3: Professional login and sidebar with icons
                - After Phase 4: Every table identical, truncation and tooltips working
                - After Phase 5: Every button type consistent; keyboard navigation has focus rings
                - After Phase 6: Dashboard cards modern and color-coded
                - After Phase 7+8: Full design system applied and validated

                ---

                ## Notes for the Implementing Agent

                - **Do not add new packages**. `QIcon`, `QGraphicsDropShadowEffect`, `QStyledItemDelegate`, and `QFont` are all from the existing PySide6 dependency.
                - **Do not modify any `logic/` or `*_db.py` files** — this is a UI-only phase.
                - **Do not modify `database.py`** — no schema changes.
                - **The only place `setStyleSheet()` is called at app level is `main.py`**. Screen files may only call `setStyleSheet()` on individual labels (for profit/loss coloring) and the card `QFrame` border.
                - **`apply_table_style()` replaces all of these** — if you see `setAlternatingRowColors`, `setShowGrid`, `setSelectionBehavior`, `setEditTriggers`, `verticalHeader().setVisible` in a screen file, those calls are eliminated because `apply_table_style()` sets all of them.
                - **Task completion**: Mark each task `[x]` as soon as it is complete. Do not batch.
                - **Verify after each phase checkpoint** that `python main.py` runs without errors before continuing.
