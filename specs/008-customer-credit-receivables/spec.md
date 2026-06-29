# Feature Specification: Customer Credit & Receivables Management

**Feature Branch**: `008-customer-credit-receivables`

**Created**: 2026-06-29

**Status**: Draft

**Input**: User description: "from customers.md create a specification"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Partial Payment on Invoice (Priority: P1)

An accountant creates a new sale. The customer pays only part of the invoice total. The accountant unchecks "Paid in Full", enters the amount received, and the remaining balance is calculated and saved automatically.

**Why this priority**: This is the core capability that unlocks the entire feature. Without it, no receivable is ever created. All other stories depend on receivables existing.

**Independent Test**: Create an invoice for 1000, uncheck Paid in Full, enter 400 as Amount Paid. Verify Remaining Balance shows 600 and the invoice saves with the correct split. Delivers immediate value by tracking partial payments.

**Acceptance Scenarios**:

1. **Given** a new invoice is open, **When** the "Paid in Full" checkbox is checked (default), **Then** no additional payment fields are shown and the full invoice total is recorded as paid.
2. **Given** a new invoice is open, **When** the user unchecks "Paid in Full", **Then** Invoice Total (read-only), Amount Paid (editable), and Remaining Balance (calculated) are displayed.
3. **Given** the partial payment fields are visible, **When** the user types an Amount Paid, **Then** Remaining Balance updates immediately without requiring any additional action.
4. **Given** the partial payment fields are visible, **When** the user enters an Amount Paid greater than Invoice Total, **Then** the system blocks saving and shows a clear validation error.
5. **Given** the partial payment fields are visible, **When** the user enters a negative Amount Paid, **Then** the system blocks saving and shows a clear validation error.
6. **Given** a valid partial amount is entered, **When** the invoice is saved, **Then** Invoice Total, Amount Paid, and Remaining Balance are all persisted correctly.

---

### User Story 2 - Customer List Page (Priority: P2)

An accountant navigates to a new Customers section and sees every customer with their purchase history and outstanding balance at a glance.

**Why this priority**: This is the primary place from which the accountant manages receivables. It must exist before payment collection or customer drill-down can be useful.

**Independent Test**: Navigate to the Customers page. Verify that customers who have unpaid balances are visually distinct from fully-paid customers, and that the list can be searched, sorted, and filtered. Delivers value independently as a customer overview.

**Acceptance Scenarios**:

1. **Given** the user opens the Customers page, **When** the page loads, **Then** all customers are listed with: Customer Name, Phone Number, Number of Invoices, Total Purchases, Outstanding Balance.
2. **Given** some customers have outstanding balances, **When** the list is displayed, **Then** those customers are visually distinguished from customers with zero balance.
3. **Given** the Customers page is open, **When** the user types in the search box, **Then** the list filters in real time to matching customers.
4. **Given** the Customers page is open, **When** the user clicks a column header, **Then** the list sorts by that column (ascending / descending toggle).
5. **Given** the Customers page is open, **When** the user applies the "Has Balance" filter, **Then** only customers with outstanding balances are shown.

---

### User Story 3 - Customer Profile & Invoice History (Priority: P3)

The accountant selects a customer and sees a full profile: summary cards for their financial position and a table listing every invoice with its payment status.

**Why this priority**: Provides the detail needed to understand a customer's history before collecting a payment. Depends on the customer list (P2).

**Independent Test**: Open any customer's profile. Verify that the four summary cards show correct totals and that the invoice table lists every invoice with accurate Status labels (Paid / Partially Paid / Outstanding).

**Acceptance Scenarios**:

1. **Given** the user clicks a customer on the Customers page, **When** the profile opens, **Then** four summary cards are shown: Outstanding Balance, Total Purchases, Total Paid, Number of Invoices.
2. **Given** the customer profile is open, **When** the invoice table renders, **Then** each row shows: Invoice Number, Date, Invoice Total, Paid, Remaining, Status.
3. **Given** an invoice was paid in full, **When** it appears in the table, **Then** its Status is "Paid".
4. **Given** an invoice was partially paid, **When** it appears in the table, **Then** its Status is "Partially Paid".
5. **Given** an invoice has never been paid, **When** it appears in the table, **Then** its Status is "Unpaid".
6. **Given** an invoice was voided, **When** it appears in the table, **Then** its Status is "Voided" and it is excluded from all balance calculations.

---

### User Story 4 - Receive Payment Against Outstanding Balance (Priority: P4)

The accountant opens a customer profile and collects a payment. The system supports partial or full settlement and records the transaction permanently.

**Why this priority**: Closes the receivables loop. Without this, balances can only grow — they can never be reduced outside of the original sale.

**Independent Test**: Open a customer who has an outstanding balance. Click "Receive Payment", enter an amount, confirm. Verify the outstanding balance decreases, the payment appears in payment history, and no data is lost.

**Acceptance Scenarios**:

1. **Given** a customer has an outstanding balance, **When** the profile is open, **Then** a "Receive Payment" button is visible.
2. **Given** the user clicks "Receive Payment", **When** the dialog opens, **Then** it lists the customer's outstanding invoices, shows the total Outstanding Balance, and provides an invoice selector and an Amount Received input.
3. **Given** the dialog is open and an invoice is selected, **When** the user enters an amount, **Then** Remaining Balance on that specific invoice after payment is calculated and displayed immediately.
4. **Given** a valid amount is entered, **When** the user confirms, **Then** the payment is recorded, the customer's outstanding balance is updated, and all related views (dashboard, reports, customer profile) reflect the new totals.
5. **Given** a payment fully settles the balance, **When** confirmed, **Then** the customer's outstanding balance becomes zero and the "Receive Payment" button is hidden or disabled.
6. **Given** the dialog is open, **When** the user enters an amount exceeding the outstanding balance, **Then** the system blocks submission and shows a validation error.
7. **Given** any payment has been recorded, **When** the user views payment history, **Then** the payment appears with Date, Amount, Related Invoice, and Remaining Balance After Payment.

---

### User Story 5 - Dashboard Receivables KPIs (Priority: P5)

The accountant glances at the Dashboard and immediately sees total outstanding receivables and how many customers owe money. Clicking the receivables card reveals a breakdown by customer.

**Why this priority**: Provides a management-level view without navigating the full customer list. Depends on receivables data being stored (P1).

**Independent Test**: With at least two customers having outstanding balances, open the Dashboard. Verify both new KPI cards show correct totals. Click the Outstanding Receivables card and verify the customer list appears with correct per-customer balances.

**Acceptance Scenarios**:

1. **Given** the Dashboard is open, **When** it renders, **Then** two new KPI cards are visible: "Outstanding Receivables" (total amount owed) and "Customers With Outstanding Balance" (count).
2. **Given** the user clicks the "Outstanding Receivables" card, **When** the dialog opens, **Then** it lists every customer with an outstanding balance, showing Customer Name and Outstanding Balance.
3. **Given** the dialog is open, **When** the user clicks a customer name, **Then** the customer's profile page opens.

---

### User Story 6 - Customer Receivables Report (Priority: P6)

The accountant runs a report to get a period-filtered, sortable breakdown of every customer's sales, payments, and remaining balance.

**Why this priority**: Supports business reporting and reconciliation. Depends on receivables data (P1) and payment recording (P4).

**Independent Test**: Open the Reports section, select "Customer Receivables", filter by a date range. Verify the report lists every customer with correct Total Sales, Total Paid, and Outstanding Balance within the period, and that search, sort, and date filter all work correctly.

**Acceptance Scenarios**:

1. **Given** the user opens Reports and selects "Customer Receivables", **When** the report loads, **Then** every customer is listed with: Customer Name, Total Sales, Total Paid, Outstanding Balance.
2. **Given** the report is visible, **When** the user types in the search box, **Then** the report filters to matching customers in real time.
3. **Given** the report is visible, **When** the user applies a date range filter, **Then** only invoices and payments within that range contribute to the totals.
4. **Given** the report is visible, **When** the user clicks a column header, **Then** rows are sorted by that column.

---

### Edge Cases

- What happens when a customer's Amount Paid equals Invoice Total exactly after unchecking "Paid in Full"? The system treats it as fully paid (zero remaining).
- What if a customer has zero invoices? They may not appear on the Customers page, or they appear with zero totals — the system must never crash on empty state.
- What happens if a customer has multiple partially-paid invoices? The "Receive Payment" dialog displays each outstanding invoice and the user explicitly selects which invoice the payment applies to. There is no automatic distribution — each payment links to exactly one invoice.
- What if the database write for a payment partially succeeds? The operation is wrapped in a transaction and rolled back entirely on any failure; the user sees a friendly error message.
- What happens when the user opens the "Receive Payment" dialog and then clicks away without submitting? No payment is recorded and no data changes.
- What if an invoice is voided after a partial payment has already been recorded? The void reverses the sale's stock effect; the payment history is preserved for audit purposes and the outstanding balance is recalculated from remaining active invoices.

## Requirements *(mandatory)*

### Functional Requirements

**Sales Integration**

- **FR-000**: The Sales invoice screen MUST include a customer selector: a searchable dropdown of existing customers with an inline "Add New Customer" option. Selecting "Add New" opens a minimal dialog (name, optional phone) that creates the customer record and immediately selects it in the dropdown. An invoice MUST NOT be saved without a customer assigned.
- **FR-001**: The Sales invoice screen MUST display a payment status selector (dropdown/combo) with three options: "Paid in Full" (default), "Partial Payment", and "Unpaid".
- **FR-002**: When "Partial Payment" is selected, the system MUST reveal two fields: Amount Paid (editable) and Remaining Balance (auto-calculated, read-only). When "Unpaid" is selected, Amount Paid is set to zero automatically. When "Paid in Full" is selected, Amount Paid equals Invoice Total automatically.
- **FR-003**: Remaining Balance MUST update immediately whenever Amount Paid changes, without requiring any form submission.
- **FR-004**: The system MUST block invoice submission if Amount Paid exceeds Invoice Total.
- **FR-005**: The system MUST block invoice submission if Amount Paid is negative.
- **FR-006**: On save, the system MUST persist Invoice Total and Amount Paid on the invoice record. Remaining Balance is always derived (never stored) as `Invoice Total − Amount Paid − SUM(post-sale payments for this invoice)`.
- **FR-007**: When "Paid in Full" is selected, the system MUST record Amount Paid equal to Invoice Total.

**Customer Management**

- **FR-008**: The application MUST include a new "Customers" navigation page listing all customers.
- **FR-009**: The Customers page MUST display per-customer: Customer Name, Phone Number, Number of Invoices, Total Purchases, Outstanding Balance.
- **FR-010**: Customers with an Outstanding Balance greater than zero MUST be visually distinguished from customers with zero balance.
- **FR-011**: The Customers page MUST support real-time search by customer name.
- **FR-012**: The Customers page MUST support sorting by any displayed column.
- **FR-013**: The Customers page MUST support filtering to show only customers with outstanding balances.

**Customer Profile**

- **FR-014**: Selecting a customer MUST open a dedicated customer profile page.
- **FR-015**: The customer profile MUST display four summary cards: Outstanding Balance, Total Purchases, Total Paid, Number of Invoices.
- **FR-016**: The customer profile MUST display a table of all the customer's invoices with columns: Invoice Number, Date, Invoice Total, Paid, Remaining, Status.
- **FR-017**: Invoice payment status MUST be one of four values, always derived — never stored:
  - **"Paid"**: total payments equal invoice total (remaining = 0)
  - **"Partially Paid"**: some payment exists but balance remains (0 < remaining < total)
  - **"Unpaid"**: no payment has been made (remaining = total)
  - **"Voided"**: the invoice has been voided (excluded from all balance calculations)

**Payment Collection**

- **FR-018**: The customer profile MUST display a "Receive Payment" button when Outstanding Balance > 0.
- **FR-019**: Clicking "Receive Payment" MUST open a dialog that lists the customer's outstanding invoices (invoice number, date, outstanding amount per invoice), allows the user to select one invoice to pay against, and provides an Amount Received input with a live-calculated Remaining Balance for that specific invoice.
- **FR-020**: The system MUST support both partial and full payment collection.
- **FR-021**: The system MUST block payment submission if Amount Received exceeds the outstanding balance of the selected invoice.
- **FR-022**: Every confirmed payment MUST be persisted immediately as a payment record.
- **FR-023**: After a payment is confirmed, Outstanding Balance on the customer profile, Dashboard KPIs, Reports, and all related views MUST reflect the updated totals without requiring a manual refresh.

**Payment History**

- **FR-024**: Every payment record MUST store: Date, Amount, Related Invoice reference, Remaining Balance After Payment.
- **FR-025**: Payment records MUST never be deleted.
- **FR-026**: Payment history MUST be viewable from the customer profile.

**Dashboard**

- **FR-027**: The Dashboard MUST include a new "Outstanding Receivables" KPI card showing the sum of all outstanding balances across all customers.
- **FR-028**: The Dashboard MUST include a new "Customers With Outstanding Balance" KPI card showing the count of customers with Outstanding Balance > 0.
- **FR-029**: Clicking the "Outstanding Receivables" card MUST open a dialog listing all customers with outstanding balances (Customer Name, Outstanding Balance).
- **FR-030**: Clicking a customer name in that dialog MUST navigate to that customer's profile page.

**Reports**

- **FR-031**: The Reports section MUST include a new "Customer Receivables" report.
- **FR-032**: The Customer Receivables report MUST list each customer with: Customer Name, Total Sales, Total Paid, Outstanding Balance.
- **FR-033**: The report MUST support real-time search by customer name.
- **FR-034**: The report MUST support date-range filtering that scopes invoice and payment totals to the selected period.
- **FR-035**: The report MUST support sorting by any displayed column.

**Business Rules & Data Integrity**

- **FR-036**: Outstanding Balance per invoice MUST always be derived as `invoice.total_amount − invoice.amount_paid − SUM(payments.amount WHERE payments.sale_id = invoice.id)`. Customer-level Outstanding Balance = SUM of per-invoice outstanding for all active invoices. Neither value is stored as a standalone column.
- **FR-037**: All dashboard KPIs and report totals MUST exclude voided invoices.
- **FR-038**: Payment operations MUST be wrapped in a database transaction; partial writes are not permitted.
- **FR-039**: Historical invoice records MUST remain unchanged after saving. Only `amount_paid` is stored on the invoice at creation time. Post-sale payments are stored in the `Payments` table and linked to the specific invoice via `sale_id`; invoice records are never updated after the initial save.
- **FR-040**: Each payment record MUST be linked to exactly one invoice (`sale_id` FK). A payment applied to the wrong invoice cannot be moved — it is an immutable audit record. The `Receive Payment` dialog MUST present the outstanding invoices list so the user selects the correct one explicitly.

### Key Entities *(include if feature involves data)*

- **Customer**: A dedicated stored entity (own database table). Key attributes: customer_id (primary key), name, phone number (optional). Invoices reference a customer by `customer_id` foreign key. Derived aggregates (number of invoices, total purchases, total paid, outstanding balance) are computed from related invoice and payment records. Editing a customer's name or phone does not alter historical invoice records.
- **Invoice (extended)**: Existing invoice entity extended with one new column: `amount_paid` (stored at invoice creation time only). Remaining balance is always derived — never stored. Still subject to existing void/audit rules.
- **Payment**: A record of money received from a customer after invoice creation. Linked to `customer_id` (not to a specific invoice). Attributes: date, amount received, customer reference, running remaining balance after payment. Immutable once recorded. Per-invoice paid/remaining amounts shown in the UI are derived by aggregating all payments against that customer's invoices (FIFO) — the invoice record itself is never mutated by post-save payments.
- **Customer Receivables Summary**: A derived, read-only view aggregated from Invoice and Payment records — never stored independently.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An accountant can record a partial payment on a new invoice in under 30 seconds from opening the invoice screen.
- **SC-002**: The Customers page loads and displays all customers with correct outstanding balances in under 2 seconds for a dataset of up to 1,000 customers.
- **SC-003**: Receiving a payment updates all related views (customer profile, dashboard, reports) within the same user action — no manual refresh required.
- **SC-004**: 100% of payment records are preserved permanently; zero records are lost or deleted through normal application use.
- **SC-005**: The Outstanding Receivables KPI on the Dashboard always matches the sum of individual customer outstanding balances — zero discrepancy.
- **SC-006**: All new UI elements are visually indistinguishable in style from existing screens — no new visual patterns are introduced.
- **SC-007**: Every payment and invoice state change produces an accurate audit trail that a third party could follow to reconstruct the full financial history.

## Clarifications

### Session 2026-06-29

- Q: Is "Customer" a dedicated stored entity (own table with invoices referencing it by ID), or derived on-the-fly by grouping invoices by name+phone? → A: Dedicated `Customers` table; invoices store a `customer_id` foreign key.
- Q: When a payment is received, is it stored linked to the customer and a specific invoice, or only to the customer? -> A: Dedicated `Payments` table linked to both `customer_id` and `sale_id`; each payment targets one invoice explicitly; remaining balance per invoice is derived, never stored.
- Q: How does the user associate a customer with a new invoice on the sales screen? → A: Searchable dropdown of existing customers with an inline "Add New Customer" option that creates the record and selects it immediately.

## Assumptions

- A dedicated `Customers` table stores each customer record; invoices reference customers via `customer_id` foreign key. Customer name/phone edits do not retroactively change invoice history.
- The sales screen customer selector is a searchable dropdown; "Add New Customer" inline creates a minimal record (name + optional phone) without leaving the invoice screen.
- Each payment is explicitly linked to a specific invoice (`sale_id` FK). The user selects which invoice to pay against in the Receive Payment dialog. There is no automatic distribution or FIFO logic.
- The "Customers" page is a new top-level navigation entry in the main window sidebar, placed after Sales and before or after Reports — exact position to be confirmed during UI design.
- Phone number is optional on a customer record; customers may exist with name only.
- Voiding an invoice that has associated payments does not delete those payments; it preserves them in history and recalculates the customer balance from remaining active invoices.
- Multi-currency is out of scope; all amounts are in the single currency already used by the system.
- Printing or exporting customer statements is out of scope for this release (listed as a future extension point in the feature description).
- Aging buckets (30/60/90 days), credit limits, and multiple payment method tracking are out of scope for this release.
- The feature must fully comply with the Layered Architecture, Fixed Technology Stack, and Financial Data Integrity rules defined in the project Constitution.
