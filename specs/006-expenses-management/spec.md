# Feature Specification: Expenses Management

**Feature Branch**: `006-expenses-management`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "read expenses.md and create specification for phase 6 expenses"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a New Expense (Priority: P1)

The accountant needs to log an operating expense (e.g., rent, electricity, salaries) that is separate from inventory purchases. They open the Expenses page, click Add Expense, fill in the category, description, amount, and optional notes, and save.

**Why this priority**: Core data-entry capability — without it no other expense feature has data to work with.

**Independent Test**: Navigate to the Expenses page, add a single expense, and verify it appears in the table with the correct expense number (EXP-000001), date/time, category, description, and amount.

**Acceptance Scenarios**:

1. **Given** the Expenses page is open, **When** the user clicks "Add Expense", fills in Category = "Rent", Description = "June office rent", Amount = 1500, and saves, **Then** a new row appears in the table with an auto-generated expense number (EXP-000001), the current date and time, and the entered values.
2. **Given** the Add Expense dialog is open, **When** the user leaves Category blank and clicks Save, **Then** the system shows a validation error and does not save.
3. **Given** the Add Expense dialog is open, **When** the user enters Amount = 0 or a negative number and clicks Save, **Then** the system shows a validation error and does not save.
4. **Given** the Add Expense dialog is open, **When** the user leaves Notes blank and fills all other required fields, **Then** the expense is saved successfully (Notes is optional).

---

### User Story 2 - Smart Category Autocomplete (Priority: P2)

When adding or editing an expense, the Category field behaves like an editable combo box: it suggests previously used categories and also accepts free-text new categories. Once a new category is saved, it is available in future suggestions automatically.

**Why this priority**: Speeds up data entry dramatically and prevents duplicate category names caused by typos; critical to usability.

**Independent Test**: Add two expenses with Category = "Fuel". Then add a third expense and verify "Fuel" appears in the category dropdown suggestions without any separate category management screen.

**Acceptance Scenarios**:

1. **Given** existing categories include "Rent" and "Electricity", **When** the user opens the Add Expense dialog and clicks the Category field, **Then** a dropdown shows "Rent" and "Electricity" as suggestions.
2. **Given** the user types "Fuel" (a new category) and saves the expense, **When** they open the Add Expense dialog again, **Then** "Fuel" appears in the category suggestions.
3. **Given** the user types "Sal" in the Category field, **When** existing categories include "Salaries", **Then** the dropdown filters to show "Salaries" as a suggestion.

---

### User Story 3 - Edit and Delete an Expense (Priority: P2)

The accountant can correct a previously recorded expense by editing it, or remove it entirely if entered by mistake.

**Why this priority**: Data correction is necessary for accuracy; unlike invoices, individual expenses are correctable records, not audit-trail documents.

**Independent Test**: Add an expense, edit its amount, verify the change persists. Then delete a different expense and verify it is removed from the table.

**Acceptance Scenarios**:

1. **Given** an existing expense in the table, **When** the user clicks Edit, changes the amount, and saves, **Then** the table reflects the updated amount immediately.
2. **Given** an existing expense in the table, **When** the user clicks Delete and confirms the confirmation dialog, **Then** the expense is removed from the table.
3. **Given** the user clicks Delete on an expense, **When** the confirmation dialog appears and they cancel, **Then** the expense remains in the table unchanged.

---

### User Story 4 - Search Expenses (Priority: P3)

The accountant can quickly find a specific expense by typing in a search box that filters by expense number, category, description, or notes.

**Why this priority**: Useful once the expenses list grows but not blocking for initial use.

**Independent Test**: Add several expenses with varied categories and descriptions. Type a partial category name into the search box and verify only matching rows are shown.

**Acceptance Scenarios**:

1. **Given** the Expenses page shows multiple expenses, **When** the user types "EXP-000003" in the search box, **Then** only that expense row is displayed.
2. **Given** expenses with categories "Rent" and "Salaries", **When** the user types "sal" in the search box, **Then** only the "Salaries" expense is shown.
3. **Given** the user clears the search box, **When** all text is removed, **Then** the full expenses list is restored.

---

### User Story 5 - Dashboard Expense KPIs (Priority: P2)

The Dashboard gains three new cards: Today's Expenses, This Month Expenses, and Net Profit. These refresh automatically whenever an expense is added, edited, or deleted.

**Why this priority**: Gives the business owner immediate visibility into operating costs and true business profitability.

**Independent Test**: Record an expense today. Open the Dashboard and verify "Today's Expenses" reflects the recorded amount and "Net Profit" equals Total Profit minus Total Expenses.

**Acceptance Scenarios**:

1. **Given** no expenses have been recorded today, **When** the Dashboard is viewed, **Then** "Today's Expenses" shows 0.
2. **Given** an expense of 200 is saved today, **When** the Dashboard is refreshed, **Then** "Today's Expenses" increases by 200.
3. **Given** Total Profit is 5000 and Total Expenses (all-time) is 1200, **When** the Dashboard is viewed, **Then** "Net Profit" shows 3800.
4. **Given** an expense is deleted, **When** the Dashboard is viewed, **Then** all three new KPI cards update to reflect the deletion.
5. **Given** the existing Today's Profit, This Month Profit, and Total Profit cards, **When** expenses are added or deleted, **Then** those existing cards are unchanged (they continue to reflect sales profit only).

---

### User Story 6 - Expenses History Report (Priority: P3)

A dedicated Expenses History report page allows the accountant to view all expenses, filter by date range and category, search by keyword, open a detail view, and export to CSV.

**Why this priority**: Required for month-end and year-end accounting reviews; follows the same pattern as Sales and Purchases History.

**Independent Test**: Add several expenses across different dates and categories. Open the Expenses History report, apply a date filter for the current month, and verify only this month's expenses appear. Export to CSV and verify the file contains the filtered rows.

**Acceptance Scenarios**:

1. **Given** the Expenses History report is open, **When** the user sets a date range filter, **Then** only expenses within that date range are shown.
2. **Given** the Expenses History report is open, **When** the user filters by category "Rent", **Then** only "Rent" expenses are shown.
3. **Given** the Expenses History report is open, **When** the user clicks on an expense row, **Then** an Expense Detail dialog opens showing all fields.
4. **Given** filtered results are shown, **When** the user clicks "Export CSV", **Then** a CSV file is downloaded containing only the filtered rows with all expense fields.

---

### Edge Cases

- What happens when the user tries to save an expense with Amount = 0.00?  → Validation blocks save with a clear error message.
- What happens when the expense table is empty and the user searches? → The table remains empty; no error is shown.
- What happens if the user types a very long category name (e.g., 500 characters)? → Category is trimmed or rejected with a friendly message.
- How does Net Profit behave if Total Expenses exceed Total Profit? → Net Profit displays as a negative value.
- What happens if the user restarts the application? → All expenses, categories, and dashboard values persist correctly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an Expenses page accessible from the sidebar navigation.
- **FR-002**: System MUST display expenses in a table with columns: Expense Number, Date & Time, Category, Description, Amount, Notes, and Actions (Edit / Delete). The default sort order is Date & Time descending (most recent expense first).
- **FR-003**: System MUST auto-generate sequential expense numbers in the format EXP-000001, EXP-000002, etc.
- **FR-004**: System MUST store the exact date and time for every expense at the time of creation.
- **FR-005**: System MUST provide an Add Expense dialog with fields: Date & Time (defaulting to current date/time), Category, Description, Amount, Notes.
- **FR-006**: System MUST validate that Category is not empty before saving an expense.
- **FR-007**: System MUST validate that Description is not empty before saving an expense.
- **FR-008**: System MUST validate that Amount is a positive number greater than zero before saving.
- **FR-009**: System MUST allow Notes to be empty (optional field).
- **FR-010**: The Category field MUST behave as an editable combo box that shows previously used expense categories as suggestions; matching MUST be case-insensitive (e.g., typing "rent" suggests "Rent"). The category is stored and displayed exactly as it was first entered.
- **FR-011**: When a new category is used and saved for the first time, it MUST automatically appear in future category suggestions without any separate management screen. Duplicate detection is case-insensitive so "Rent" and "rent" resolve to the same category.
- **FR-012**: System MUST allow editing any field of an existing expense.
- **FR-013**: System MUST ask for confirmation before deleting an expense.
- **FR-014**: System MUST permanently delete the expense record upon confirmed deletion.
- **FR-015**: The search box MUST filter the expenses table in real time by Expense Number, Category, Description, and Notes.
- **FR-016**: Dashboard MUST include a "Today's Expenses" card showing total operating expenses recorded on the current calendar day.
- **FR-017**: Dashboard MUST include a "This Month Expenses" card showing total operating expenses recorded during the current calendar month.
- **FR-018**: Dashboard MUST include a "Net Profit" card calculated as Total Profit (sales profit only) minus all-time Total Expenses.
- **FR-019**: All three new Dashboard cards MUST refresh automatically whenever an expense is created, edited, or deleted.
- **FR-020**: The existing Today's Profit, This Month Profit, and Total Profit dashboard cards MUST NOT be affected by expenses data.
- **FR-021**: System MUST provide an Expenses History report page with date range filtering, category filtering, keyword search, an Expense Detail dialog, and CSV export.
- **FR-022**: CSV export MUST reflect the currently active filters at the time of export.
- **FR-023**: Expenses data MUST be stored in a dedicated Expenses table, completely separate from Purchases tables.
- **FR-024**: All validation errors MUST be shown to the user via friendly dialogs; raw exceptions must never be displayed.
- **FR-025**: The Expenses module MUST follow the existing UI/UX patterns and visual style of the other pages.
- **FR-026**: Business rules for expenses (validation, numbering, dashboard calculations) MUST reside in the Logic layer; no SQL in UI files.

### Key Entities

- **Expense**: A single operating cost record. Key attributes: unique sequential expense number, exact date and time, category (free-text, reusable), description, monetary amount, optional notes.
- **Expense Category**: A distinct category name derived from saved expenses. Not stored in a separate table — inferred dynamically from existing expense records.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new expense can be recorded from opening the dialog to saving in under 30 seconds.
- **SC-002**: All expense records and categories survive application restart without data loss.
- **SC-003**: The Dashboard's three new cards (Today's Expenses, This Month Expenses, Net Profit) update within 1 second of any expense change.
- **SC-004**: The existing Today's Profit, This Month Profit, and Total Profit dashboard values are identical before and after expenses are recorded.
- **SC-005**: Searching or filtering expenses returns correct results for 100% of test cases covering expense number, category, description, and notes.
- **SC-006**: CSV export from the Expenses History report contains exactly the rows visible on screen at export time.
- **SC-007**: All validation rules (required fields, positive amount) are enforced 100% of the time — no invalid expense record can reach the database.
- **SC-008**: The full manual testing checklist (add, edit, delete, search, smart category, dashboard updates, reports, CSV, date filters, restart persistence, regression) passes without failures.

## Assumptions

- The Expenses module stores expenses as individual records (not grouped by invoice); each expense is a standalone entry.
- Net Profit is calculated as all-time Total Profit (from sales) minus all-time Total Expenses; no time-bounded Net Profit is required.
- Expense categories are inferred from existing expense records; no separate Category table or management screen is needed.
- Date & Time for an expense defaults to the current timestamp but can be overridden by the user in the Add/Edit dialog.
- Expenses are fully editable and deletable (unlike invoices, they do not follow void-only audit semantics).
- The Expenses History report follows the same UI patterns as Sales History and Purchases History reports (same date filter, category filter, search, detail dialog, and CSV export behaviors).
- The application remains single-user; no concurrency or multi-user considerations apply.
- Printed reports (if applicable) should display expense date and time consistently with the screen display.

## Clarifications

### Session 2026-06-28

- Q: Should category matching and deduplication be case-insensitive? → A: Case-insensitive suggestions; store and display category as first entered (e.g., "Rent" and "rent" resolve to the same category, displayed as "Rent").
- Q: What should the default sort order be for the expenses table? → A: Date & Time descending — most recent expense first.
