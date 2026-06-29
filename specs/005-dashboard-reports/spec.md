# Feature Specification: Dashboard & Reports

**Feature Branch**: `005-dashboard-reports`

**Created**: 2026-06-27

**Status**: Updated

**Input**: User description: "read BLUEPRINT.md, IMPLEMENTATION_PLAN.md and create a specification for Phase 5 — Dashboard & Reports"

## Clarifications

### Session 2026-06-27

- Q: When the user clicks "Export to CSV", which table is exported — the Sales History table, the Purchases History table, or both? → A: Export the table the user last interacted with / selected (the active/focused table).
- Q: Does selecting a date preset auto-apply the filter, or does the user always need to click Apply? → A: Preset selections auto-apply immediately; the Apply button is only active and required for Custom Range.
- Q: Should "Total Stock Value" on the Dashboard include inactive (deactivated) products or active products only? → A: All products, active and inactive — inactive products still have physical stock with real monetary value that must not be excluded.
- Q: Should the "Total Products" Dashboard card count all products or active only? → A: Display all three metrics separately: Total Products (all), Active Products, and Inactive Products.

### Session 2026-06-27 (Enhancement)

- Enhancement: Dashboard summary cards expanded to ten; "Total Stock Value" renamed to "Inventory Value"; "Potential Stock Profit" and "Low Stock Count" cards added.
- Enhancement: Clicking a product in the Low Stock list navigates to the Products page and highlights/pre-filters that product.
- Enhancement: Recent Activity section added to Dashboard, showing the latest invoices across Sales and Purchases.
- Enhancement: Date preset "All Time" replaced by "Yesterday"; preset list is now Today, Yesterday, This Week, This Month, Custom Range.
- Enhancement: Top Selling Products and Top Purchased Products reports added to the Reports page.
- Enhancement: Invoice Detail Dialog for Sales must show Historical Cost Price and Profit per Line, always calculated from `SaleItems.purchase_price_at_sale`.
- Enhancement: Dashboard visual behavior defined — warning color for Low Stock, success color for profit values, consistent card styling.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Business Performance at a Glance (Priority: P1)

The store owner opens the Dashboard page immediately after logging in. They see ten summary cards giving an instant snapshot of the business: total products in the catalog broken down by active and inactive counts, the current inventory value of all stock on hand, the potential profit if all current stock were sold, how much was sold today, how much was spent on purchases today, today's profit, the all-time profit, and a count of products currently at or below their reorder level. Below the cards, a low-stock alert list highlights every active product that has reached or fallen below its reorder level. Profit cards are shown in a positive/success color; the Low Stock Count card and the Low Stock list use a warning color to draw attention to restocking needs.

**Why this priority**: The Dashboard is the first screen seen after login and is the most important view for daily decision-making. Without it, the owner cannot quickly know whether the business is profitable, whether stock is running low, or what activity happened today.

**Independent Test**: Log in → Dashboard shows all ten cards with values verifiable by hand against data from Phases 3–4. Low Stock list appears for any active product at or below its reorder level; profit cards appear in a success color; Low Stock Count card and Low Stock list appear in a warning color.

**Acceptance Scenarios**:

1. **Given** the owner is logged in, **When** they navigate to the Dashboard, **Then** they see ten labeled cards: Total Products, Active Products, Inactive Products, Inventory Value, Potential Stock Profit, Today's Sales, Today's Purchases, Today's Profit, Total Profit, and Low Stock Count.
2. **Given** the owner is logged in, **When** they view the Dashboard, **Then** Today's Profit and Total Profit values are calculated using `SaleItems.purchase_price_at_sale` (the historical cost frozen at time of sale), not the current `Products.purchase_price`.
3. **Given** the owner is logged in, **When** they view the Dashboard, **Then** Inventory Value equals the sum of `stock_quantity × purchase_price` across all products (active and inactive); Potential Stock Profit equals the sum of `(selling_price − purchase_price) × stock_quantity` across all products — neither value is stored in the database.
4. **Given** at least one active product has `stock_quantity ≤ reorder_level`, **When** the owner views the Dashboard, **Then** the Low Stock Count card shows the correct count, and a Low Stock list below the cards shows each such product's Name, Category, Current Stock, and Reorder Level — both displayed in a warning color.
5. **Given** a product is deactivated (`is_active = 0`), **When** the Dashboard is shown, **Then** that product does NOT appear in the Low Stock list and is NOT counted in Low Stock Count, regardless of its stock level.
6. **Given** no active products are at or below their reorder level, **When** the Dashboard is shown, **Then** Low Stock Count shows zero and the Low Stock list is empty or hidden.
7. **Given** Today's Profit and Total Profit are positive, **When** the Dashboard is shown, **Then** those cards are displayed in a positive/success color.
8. **Given** the owner navigates away and back to the Dashboard, **When** the page becomes visible again, **Then** all values refresh to reflect any changes (e.g. a new sale just saved).

---

### User Story 2 - Navigate to a Low Stock Product from the Dashboard (Priority: P2)

From the Low Stock list on the Dashboard, the owner can click any product row. The application navigates directly to the Products page and automatically selects, highlights, or pre-filters that product so the owner can immediately take action — such as reactivating, editing the reorder level, or verifying the current stock.

**Why this priority**: Without this navigation shortcut, the owner must manually find the product on the Products page after noting its name from the Low Stock list — a friction point that slows down the restocking workflow.

**Independent Test**: Create a product below its reorder level, open the Dashboard, click that product in the Low Stock list, and confirm the Products page opens with that product visible and identifiable.

**Acceptance Scenarios**:

1. **Given** the Low Stock list shows at least one product, **When** the owner clicks a product row, **Then** the application navigates to the Products page.
2. **Given** the Products page is shown after a Low Stock click, **When** the page loads, **Then** the clicked product is automatically highlighted, selected, or pre-filtered so it is immediately visible and distinguishable from other products.
3. **Given** the Products page is reached via Low Stock navigation, **When** the owner views it, **Then** it behaves exactly as if opened normally — all existing Products page functionality (edit, deactivate, search) remains available.

---

### User Story 3 - View Recent Activity on the Dashboard (Priority: P2)

Below the Low Stock section, the owner sees a "Recent Activity" panel showing the latest invoices created across both Sales and Purchases, in a single unified list ordered by date (newest first). Each entry shows the invoice number, invoice type (Sale or Purchase), date, and total amount. This gives the owner a quick overview of the most recent transactions without navigating to the Reports page.

**Why this priority**: Recent Activity provides immediate context after login about what transactions have just occurred, helping the owner spot missing or incorrect entries quickly.

**Independent Test**: Save a sale and a purchase, then open the Dashboard. Both should appear in Recent Activity, newest first, with correct invoice type labels.

**Acceptance Scenarios**:

1. **Given** at least one invoice (sale or purchase) has been saved, **When** the owner views the Dashboard, **Then** the Recent Activity section shows a list of recent invoices with columns: Invoice Number, Type (Sale / Purchase), Date, Customer/Supplier Name (blank if not set), Total Amount.
2. **Given** multiple invoices exist, **When** the Recent Activity section is shown, **Then** invoices are ordered newest first, mixing Sales and Purchases in a single list.
3. **Given** no invoices have been saved yet, **When** the owner views the Dashboard, **Then** the Recent Activity section is empty or shows a "No recent activity" placeholder — no error.
4. **Given** the Dashboard refreshes (on each page-show event), **When** new invoices have been saved since the last view, **Then** Recent Activity updates to include them.

---

### User Story 4 - Review Financial Summaries by Date Range (Priority: P2)

The owner opens the Reports page to check financial performance over a specific period. They select a date range from a dropdown — Today, Yesterday, This Week, This Month, or a custom From/To date range — and see three summary totals update immediately: Total Sales revenue, Total Purchases cost, and Total Profit. Only active (non-voided) invoices are included in these figures. Selecting a preset applies the filter immediately; the Apply button is only required when a Custom Range is entered.

**Why this priority**: Date-range financial summaries are the core business intelligence feature of the app. Without them, the owner cannot assess period performance, identify trends, or close out a day, week, or month.

**Independent Test**: Select each preset date range in turn (Today, Yesterday, This Week, This Month) and confirm the totals change accordingly without needing to click Apply. Use Custom Range to pick a specific date span matching known test data.

**Acceptance Scenarios**:

1. **Given** the Reports page is open, **When** the owner selects a preset (Today / Yesterday / This Week / This Month), **Then** Total Sales, Total Purchases, and Total Profit update immediately to reflect only active invoices within that period — no Apply click is required.
2. **Given** the owner selects "Custom Range", **When** they set a From date and a To date and click Apply, **Then** the three summary totals and both history tables update to include only records within that date span (inclusive).
3. **Given** the owner sets a From date later than the To date, **When** they attempt to apply the range, **Then** the system rejects the input with a clear error message and does not update the results.
4. **Given** voided invoices exist within the selected range, **When** totals are computed, **Then** voided invoices are excluded from Total Sales, Total Purchases, and Total Profit — but remain visible in the history tables with a "Voided" status label.
5. **Given** Total Profit is computed, **When** the calculation runs, **Then** it equals: sum of active SaleItems subtotals minus the sum of (quantity × `purchase_price_at_sale`) for each active SaleItems row, minus the sum of `discount_amount` for each active Sales invoice — all within the selected range.

---

### User Story 5 - Browse Invoice History and Open Invoice Details (Priority: P2)

Below the date-range summary, the owner sees two read-only history tables: Sales History and Purchases History, both filtered by the active date range. Double-clicking any row opens the Invoice Detail Dialog. For Sales invoices, the dialog displays each line item with its Historical Cost Price (the purchase cost frozen at time of sale) and the Profit per Line calculated from it, in addition to the standard line-item columns. These values are always computed from the stored historical data and remain accurate even if the product's current purchase price has since changed.

**Why this priority**: The history tables and detail view are essential for auditing past transactions and verifying that data was recorded correctly. Showing per-line profitability gives the owner immediate insight into which items were most profitable on a given invoice.

**Independent Test**: Save a sale, change the product's purchase price via a new purchase, then open the original sale in the Invoice Detail Dialog. Confirm Historical Cost Price and Profit per Line still reflect the original cost at time of sale, not the new price.

**Acceptance Scenarios**:

1. **Given** the Reports page is open with a date range selected, **When** the owner views the Sales History table, **Then** it shows all sales invoices (active and voided) within the range, sorted newest first, with columns: Invoice Number, Date, Customer, Total Amount, Status.
2. **Given** the Reports page is open with a date range selected, **When** the owner views the Purchases History table, **Then** it shows all purchase invoices (active and voided) within the range, sorted newest first, with columns: Invoice Number, Date, Supplier, Total Amount, Status.
3. **Given** a sales invoice row is shown in the history table, **When** the owner double-clicks it, **Then** the Invoice Detail Dialog opens showing: Invoice Number, Date, Status, Customer Name (if any), all line items with columns Product / Quantity / Unit Price / Historical Cost Price / Profit per Line / Subtotal, and a footer showing Subtotal → Discount → Grand Total.
4. **Given** a sales invoice line item is displayed in the Invoice Detail Dialog, **When** the owner views Historical Cost Price and Profit per Line, **Then** both values are computed from `SaleItems.purchase_price_at_sale` — not from the current `Products.purchase_price`.
5. **Given** a purchases invoice row is shown in the history table, **When** the owner double-clicks it, **Then** the Invoice Detail Dialog opens showing: Invoice Number, Date, Status, Supplier Name (if any), all line items (Product, Quantity, Unit Price, Subtotal), and Grand Total (no discount section; no cost/profit columns, since purchase invoices have no sale-side margin).
6. **Given** the Invoice Detail Dialog is closed after viewing, **When** the dialog closes, **Then** the Reports page history tables and summary totals refresh to reflect the current state.

---

### User Story 6 - View Top Selling and Top Purchased Products (Priority: P3)

On the Reports page, below the history tables, the owner can view two additional read-only summary panels: Top Selling Products (ranked by total quantity sold) and Top Purchased Products (ranked by total quantity purchased). Both panels respect the currently active date filter.

**Why this priority**: These summaries highlight which products drive the most activity, helping the owner make restocking and pricing decisions. They are additive insight, not required for daily operation.

**Independent Test**: Create sales and purchases for multiple products, open Reports, and verify the top-selling and top-purchased lists rank products by quantity in descending order and respond to date filter changes.

**Acceptance Scenarios**:

1. **Given** the Reports page is open with a date range selected, **When** the owner views the Top Selling Products panel, **Then** it shows products ranked by total quantity sold (descending) within the active date range, from active invoices only.
2. **Given** the Reports page is open with a date range selected, **When** the owner views the Top Purchased Products panel, **Then** it shows products ranked by total quantity purchased (descending) within the active date range, from active invoices only.
3. **Given** the owner changes the date filter, **When** the filter is applied, **Then** both Top Products panels update alongside the summary totals and history tables.
4. **Given** no sales or purchases exist for the selected range, **When** the owner views the top-products panels, **Then** they are empty — no error is shown.

---

### User Story 7 - Void an Invoice from the Detail Dialog (Priority: P2)

From the Invoice Detail Dialog, the owner can void a sale or purchase entered in error. For sales, voiding always succeeds and restores sold quantities to stock. For purchases, voiding first checks that none of the purchased stock has already been sold onward; if it has, the void is blocked. A confirmation prompt is always shown before any void is applied.

**Why this priority**: Voiding is the only correction mechanism for saved invoices. Without it, there is no way to undo a mistake without corrupting financial history.

**Independent Test**: Save a sale, open it from Reports, void it, and confirm stock is restored and the sale no longer appears in active totals. Attempt to void a purchase whose stock has been partially sold and confirm the system blocks it.

**Acceptance Scenarios**:

1. **Given** an active sale is open in the Invoice Detail Dialog, **When** the owner clicks "Void Invoice", **Then** a confirmation prompt appears.
2. **Given** the owner confirms the void of an active sale, **When** the void is processed, **Then** the sale's status changes to "Voided" and each sold product's stock quantity is restored by the sold amount — as a single atomic operation.
3. **Given** an active purchase is open in the Invoice Detail Dialog, **When** the owner attempts to void it, **Then** the system checks that every product's current stock is sufficient to reverse the purchase quantities; if all checks pass, the void proceeds.
4. **Given** at least one purchased product's stock has already been sold, **When** the owner attempts to void the purchase, **Then** the void is blocked entirely with a message identifying which product(s) have insufficient stock.
5. **Given** an invoice has already been voided, **When** it is opened in the Invoice Detail Dialog, **Then** the Void Invoice button is disabled and the status header clearly reads "Voided".

---

### User Story 8 - Print an Invoice (Priority: P3)

From the Invoice Detail Dialog, the owner can print the currently displayed invoice via the operating system's standard print dialog, allowing output to a physical printer or to PDF.

**Why this priority**: Printing provides a paper trail for customers and suppliers but does not block the daily workflow.

**Independent Test**: Open any invoice in the Invoice Detail Dialog and click Print — confirm the OS print dialog opens without error.

**Acceptance Scenarios**:

1. **Given** an invoice is open in the Invoice Detail Dialog, **When** the owner clicks "Print", **Then** the operating system's standard print dialog opens pre-populated with the invoice content visible on screen.
2. **Given** the print dialog is cancelled, **When** the owner dismisses it, **Then** the Invoice Detail Dialog remains open unchanged.

---

### User Story 9 - Export Filtered History to CSV (Priority: P3)

From the Reports page, the owner can export the currently filtered, last-interacted-with history table (Sales or Purchases) to a CSV file via a Save File dialog.

**Why this priority**: CSV export supports offline analysis and sharing with an accountant. It is additive convenience, not a core daily action.

**Independent Test**: Filter the Reports page to a date range, interact with the Sales History table, click Export to CSV, save the file, and confirm it contains the correct rows and columns for Sales only.

**Acceptance Scenarios**:

1. **Given** the owner has interacted with one of the history tables, **When** they click "Export to CSV", **Then** a Save File dialog appears.
2. **Given** the owner confirms the save location, **When** the file is written, **Then** the CSV contains exactly the rows currently visible in the last-interacted-with history table (Sales or Purchases), with appropriate column headers, respecting the active date filter.
3. **Given** the export completes, **When** the owner opens the file in a spreadsheet application, **Then** the data is correctly formatted and readable.
4. **Given** the owner cancels the Save File dialog, **When** they dismiss it, **Then** no file is written and the Reports page remains unchanged.

---

### Edge Cases

- What happens when the Dashboard is opened and no invoices have ever been saved? → All summary cards display zero values; the Low Stock list and Recent Activity section are empty or show placeholder text — no errors.
- What happens when Today's Sales or Today's Purchases total is zero? → The corresponding card shows zero — no error or placeholder text.
- What happens when Inventory Value or Potential Stock Profit is zero (no products or all stock is zero)? → The corresponding card shows zero — no error.
- What happens when Potential Stock Profit is negative (selling price below purchase price for some products)? → The card shows the actual computed value (which may be negative); the success color is not applied if the value is not positive.
- What happens when a product's reorder level is set to 0? → It only appears in the Low Stock list and Low Stock Count when stock also reaches 0.
- What happens when the Custom Range "From" and "To" dates are the same? → Treated as a single-day filter; all invoices from that date are included.
- What happens when a history table has no rows for the selected date range? → The table is empty; summary totals show zero; no error message.
- What happens when the Top Products panels have no data for the selected range? → Both panels are empty — no error.
- What happens if a void operation encounters a database error mid-transaction? → The transaction is rolled back entirely; no partial state is written; a friendly error message is shown.
- What happens if the CSV export fails (e.g. disk full, permission denied)? → A friendly error message is shown; no partial file is left behind.
- What happens when an invoice has no customer/supplier name? → The Name field in the history table and detail dialog is blank — no error or placeholder.
- What happens if Historical Cost Price or Profit per Line cannot be computed (missing `purchase_price_at_sale`)? → This cannot occur for correctly saved invoices; the field is `NOT NULL` in the schema.

## Requirements *(mandatory)*

### Functional Requirements

**Report Logic**

- **FR-001**: The system MUST compute Total Sales as the sum of `total_amount` across all active Sales invoices within the selected date range.
- **FR-002**: The system MUST compute Total Purchases as the sum of `total_amount` across all active Purchases invoices within the selected date range.
- **FR-003**: The system MUST compute Total Profit as: (sum of `SaleItems.subtotal` for active sales) minus (sum of `SaleItems.quantity × SaleItems.purchase_price_at_sale` for active sales) minus (sum of `Sales.discount_amount` for active sales) — all within the selected date range. The current `Products.purchase_price` MUST NOT be used in this calculation.
- **FR-004**: All three aggregate values MUST exclude voided invoices entirely.
- **FR-005**: All aggregation functions MUST accept an optional date range; omitting it returns All Time results.

**Dashboard — Summary Cards**

- **FR-006**: The Dashboard MUST display ten summary cards in the following order: Total Products (count of all products), Active Products (count where `is_active = 1`), Inactive Products (count where `is_active = 0`), Inventory Value, Potential Stock Profit, Today's Sales, Today's Purchases, Today's Profit, Total Profit, Low Stock Count.
- **FR-007**: **Inventory Value** MUST equal the sum of `stock_quantity × purchase_price` across all products (active and inactive). This value MUST be calculated at display time and MUST NOT be stored in the database.
- **FR-008**: **Potential Stock Profit** MUST equal the sum of `(selling_price − purchase_price) × stock_quantity` across all products (active and inactive). This value MUST be calculated at display time and MUST NOT be stored in the database.
- **FR-009**: **Today's Profit** and **Total Profit** MUST be computed using `SaleItems.purchase_price_at_sale` (historical cost frozen at time of sale), not from the current `Products.purchase_price`. Both MUST reuse the same `report_logic.py` profit function — Today's Profit passes today's date as both start and end; Total Profit passes no date range.
- **FR-010**: **Low Stock Count** MUST equal the count of active products where `stock_quantity ≤ reorder_level`.
- **FR-011**: Today's Sales and Today's Purchases MUST be computed by calling the same aggregation logic used for date-ranged reports, with today's date as both start and end — no separate logic path.

**Dashboard — Visual Behavior**

- **FR-012**: Today's Profit and Total Profit cards MUST be displayed in a positive/success color when their value is greater than zero.
- **FR-013**: The Low Stock Count card MUST be displayed in a warning color at all times (not conditional on value), to draw attention to the restocking status.
- **FR-014**: The Low Stock list rows MUST use a warning color or highlight to distinguish them visually.
- **FR-015**: All Dashboard summary cards MUST be visually consistent with each other and with the rest of the application's styling — no card may use a unique layout or font size that breaks visual cohesion.

**Dashboard — Low Stock List**

- **FR-016**: The Dashboard MUST display a Low Stock list below the summary cards showing every active product where `stock_quantity ≤ reorder_level`, with columns: Name, Category, Current Stock, Reorder Level.
- **FR-017**: The Low Stock list MUST exclude inactive (deactivated) products.
- **FR-018**: If no active products are at or below their reorder level, the Low Stock list MUST be empty or hidden — no error state.
- **FR-019**: Clicking a row in the Low Stock list MUST navigate to the Products page and automatically highlight, select, or pre-filter to that specific product.

**Dashboard — Recent Activity**

- **FR-020**: The Dashboard MUST display a "Recent Activity" section showing the **10 most recent invoices** across both Sales and Purchases, ordered newest first, as a single unified list.
- **FR-021**: Each Recent Activity row MUST show: Invoice Number, Type (Sale or Purchase), Date, Customer/Supplier Name (blank if not set), Total Amount.
- **FR-022**: The Recent Activity section MUST refresh each time the Dashboard page becomes visible.
- **FR-023**: If no invoices exist, the Recent Activity section MUST display an empty state (empty list or placeholder text) without error.

**Dashboard — General**

- **FR-024**: The Dashboard MUST refresh all values (cards, Low Stock list, Recent Activity) each time the page becomes visible.

**Reports Page — Date Filter**

- **FR-025**: The Reports page MUST provide a date-range filter with preset options: Today, Yesterday, This Week, This Month, and Custom Range.
- **FR-026**: Selecting a preset (Today, Yesterday, This Week, This Month) MUST immediately apply the filter and update all summary totals, both history tables, and both Top Products panels — no Apply button click is required for presets.
- **FR-027**: When "Custom Range" is selected, two date picker controls MUST be enabled; they MUST be disabled for all other preset options.
- **FR-028**: The Apply button MUST only be active when "Custom Range" is selected.
- **FR-029**: The system MUST reject a Custom Range where the From date is later than the To date, displaying a clear validation message.
- **FR-030**: "This Week" means the Monday-to-Sunday calendar week that contains today. "This Month" means the calendar month that contains today. Both are inclusive of today.

**Reports Page — Summaries and History**

- **FR-031**: The Reports page MUST display three summary blocks (Total Sales, Total Purchases, Total Profit) that update to reflect the selected date range.
- **FR-032**: The Reports page MUST display a Sales History table and a Purchases History table, both filtered by the active date range, both showing all invoices regardless of status (active and voided), sorted newest first.
- **FR-033**: Each Sales History row MUST show: Invoice Number, Date, Customer Name, Total Amount, Status.
- **FR-034**: Each Purchases History row MUST show: Invoice Number, Date, Supplier Name, Total Amount, Status.
- **FR-035**: Double-clicking a row in either history table MUST open the Invoice Detail Dialog for that invoice.

**Reports Page — Top Products**

- **FR-036**: The Reports page MUST display a Top Selling Products panel showing products ranked by total quantity sold (descending) within the active date range, from active invoices only.
- **FR-037**: The Reports page MUST display a Top Purchased Products panel showing products ranked by total quantity purchased (descending) within the active date range, from active invoices only.
- **FR-038**: Both Top Products panels MUST update whenever the date filter changes.
- **FR-039**: If no data exists for the selected range, the Top Products panels MUST display an empty state — no error.

**Reports Page — CSV Export**

- **FR-040**: The Reports page MUST provide an "Export to CSV" button that opens a Save File dialog and writes the currently filtered rows from the last-interacted-with history table (Sales History or Purchases History) to a CSV file using the standard CSV format. No external libraries are required.
- **FR-041**: Each history table MUST track which was most recently interacted with (row click or focus) so the export target is always deterministic.
- **FR-042**: A wait cursor MUST be displayed during CSV export.

**Invoice Detail Dialog**

- **FR-043**: The Invoice Detail Dialog MUST be a single reusable modal that works for both Sales and Purchases invoices, driven by invoice type and ID.
- **FR-044**: For a Sales invoice, the dialog MUST display: Invoice Number, Date, Status, Customer Name (if set), all line items with columns Product / Quantity / Unit Price / Historical Cost Price / Profit per Line / Subtotal, and a footer showing Subtotal → Discount → Grand Total.
- **FR-045**: **Historical Cost Price** per line MUST be read from `SaleItems.purchase_price_at_sale` — the current `Products.purchase_price` MUST NOT be used.
- **FR-046**: **Profit per Line** MUST equal `(unit_price − purchase_price_at_sale) × quantity` for each SaleItems row — computed at display time, never stored.
- **FR-047**: For a Purchases invoice, the dialog MUST display: Invoice Number, Date, Status, Supplier Name (if set), all line items (Product, Quantity, Unit Price, Subtotal), and Grand Total only (no discount section; no Historical Cost Price or Profit per Line columns).
- **FR-048**: The dialog MUST include a "Void Invoice" button that is enabled only when the invoice's status is `active`.
- **FR-049**: Clicking "Void Invoice" MUST show a confirmation prompt before any action is taken.
- **FR-050**: Voiding a Sale MUST set its status to `voided` and restore each sold product's stock quantity — as a single atomic transaction.
- **FR-051**: Voiding a Purchase MUST first verify that each line item's quantity does not exceed the product's current stock; if any check fails, the void MUST be blocked entirely with a message identifying the affected product(s) — no partial void is applied.
- **FR-052**: If a Purchase void passes all stock checks, it MUST set the purchase status to `voided` and reduce each product's stock quantity — as a single atomic transaction.
- **FR-053**: Once voided, the Void Invoice button MUST be disabled; re-voiding is not permitted.
- **FR-054**: The dialog MUST include a "Print" button that opens the operating system's standard print dialog populated with the invoice content visible on screen.
- **FR-055**: A wait cursor MUST be displayed during Void and Print operations.
- **FR-056**: Closing the Invoice Detail Dialog MUST cause the Reports page to refresh its history tables, summary totals, and Top Products panels.

### Key Entities

- **Sale**: A saved sales invoice with header fields (invoice number, date, customer name, discount amount, total amount, status) and one or more line items (product, quantity, unit price, `purchase_price_at_sale`, subtotal).
- **Purchase**: A saved purchase invoice with header fields (invoice number, date, supplier name, total amount, status) and one or more line items (product, quantity, unit price, subtotal).
- **Report Aggregate**: A computed summary (Total Sales, Total Purchases, Total Profit) for a given date range, derived from active invoices only. Profit always uses `SaleItems.purchase_price_at_sale`.
- **Low Stock Product**: An active product whose `stock_quantity ≤ reorder_level`.
- **Inventory Value**: A calculated display value — sum of `stock_quantity × purchase_price` across all products. Never stored.
- **Potential Stock Profit**: A calculated display value — sum of `(selling_price − purchase_price) × stock_quantity` across all products. Never stored.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All ten Dashboard summary cards display correct values, verifiable by hand against known test data, within one second of the page becoming visible.
- **SC-002**: Inventory Value and Potential Stock Profit on the Dashboard match values calculated manually from the Products table — confirmed before and after a purchase price change, with no database write of these values.
- **SC-003**: Today's Profit and Total Profit remain unchanged after a product's purchase price is updated via a new purchase — confirming that only `SaleItems.purchase_price_at_sale` is used in the calculation, not the current `Products.purchase_price`.
- **SC-004**: Selecting any preset date filter (Today, Yesterday, This Week, This Month) on the Reports page updates all summary totals, history tables, and Top Products panels within one second — without requiring an Apply button click.
- **SC-005**: Every active and voided invoice created in Phases 3–4 is reachable via the history tables and opens correctly in the Invoice Detail Dialog, with all line items and totals matching the original saved data.
- **SC-006**: Historical Cost Price and Profit per Line in the Invoice Detail Dialog match the values calculated from `SaleItems.purchase_price_at_sale` — verified by updating the product's purchase price after the sale and confirming the dialog values are unchanged.
- **SC-007**: Voiding a sale successfully restores stock to the correct quantity as a single atomic operation — verified by checking stock before and after the void.
- **SC-008**: An attempted void of a purchase whose stock has been sold onward is blocked 100% of the time with a message that identifies the affected product(s) — it never partially voids.
- **SC-009**: Clicking a Low Stock product on the Dashboard navigates to the Products page with that product visible and identifiable within one second.
- **SC-010**: A CSV export of a filtered history table produces a valid, complete, correctly formatted file that opens without error in a standard spreadsheet application, containing only the rows from the last-interacted-with table (Sales or Purchases).
- **SC-011**: The Low Stock Count card and Low Stock list are consistently displayed in a warning color; Profit cards (Today's Profit, Total Profit) are displayed in a success color when positive.
- **SC-012**: No raw Python traceback reaches the user under any failure condition (database error, failed export, failed print, void conflict) — every failure surfaces as a friendly message.
- **SC-013**: All features from Phases 1–4 continue to work correctly after Phase 5 is complete — no regressions.

## Assumptions

- All data required for Dashboard and Reports summaries (Sales, Purchases, SaleItems with `purchase_price_at_sale`) has been correctly saved by the Phase 3 and Phase 4 implementations. Phase 5 reads this data; it does not modify the save logic.
- The `report_logic.py` profit formula is the canonical calculation for all profit figures — Dashboard's Today's Profit and Total Profit reuse this function with different date parameters, not a separately coded formula.
- Inventory Value and Potential Stock Profit are computed across all products (active and inactive), consistent with the decision that inactive products still hold physical stock with real monetary value.
- The Invoice Detail Dialog is a single dialog class that handles both Sales and Purchases invoice types; it determines which columns and sections to show based on the invoice type passed to it.
- CSV export uses Python's built-in `csv` module — no third-party library is introduced.
- Printing uses Qt's built-in `QPrinter`/`QPrintDialog` — no custom invoice template or rendering engine is required; the output reflects what is displayed on screen.
- "This Week" means the Monday-to-Sunday week containing today's date; "This Month" means the calendar month containing today's date. Both are inclusive of today.
- The Apply button is only active and required when "Custom Range" is selected. All preset options (Today, Yesterday, This Week, This Month) trigger the filter update immediately on selection.
- Recent Activity displays the 10 most recent invoices (across Sales and Purchases combined). This limit is fixed by FR-020.
- No new database schema changes are required for this phase. All data needed (including `SaleItems.purchase_price_at_sale`) is already present in the schema established in earlier phases.
- Q: How many invoices should Recent Activity display? → A: The 10 most recent invoices (Sales and Purchases combined).
- Q: Should Recent Activity show the Customer/Supplier Name alongside each invoice? → A: Yes — display Customer Name for Sales and Supplier Name for Purchases; leave blank if not set.
- "Yesterday" in the date filter means the calendar day immediately before today, inclusive of the full day.
