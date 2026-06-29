# Customer Credit & Receivables Management

I want to add a complete **Customer Credit & Receivables Management** feature to the accounting system.

This should be treated as a **major feature**, not a small enhancement.

Please create a full Specification, Plan, and Tasks before implementing anything.

Do NOT start coding immediately.

The implementation must follow the existing project architecture and design system.

No business logic should be duplicated.

---

# Feature Overview

The system currently assumes that every sale is paid in full.

I want to support customers who pay only part of an invoice while the remaining balance becomes a customer receivable.

This feature should integrate naturally with Sales, Dashboard, Reports, and a new Customers section.

---

# Part 1 — Payment Method During Sales

The default behavior should remain exactly as it is today.

Every new invoice is considered fully paid unless the user explicitly chooses otherwise.

Under the customer information section add a payment option.

Default:

☑ Paid in Full

If the user unchecks it, the interface should expand and display:

* Invoice Total (read-only)
* Amount Paid
* Remaining Balance (calculated automatically)

The Remaining Balance must update immediately whenever the Amount Paid changes.

Validation:

* Amount Paid cannot exceed Invoice Total.
* Amount Paid cannot be negative.
* Remaining Balance cannot become negative.

Saving the invoice should store:

* Invoice Total
* Amount Paid
* Remaining Balance

---

# Part 2 — Customer Management

Add a completely new page called:

Customers

The page should list every customer.

Suggested columns:

* Customer Name
* Phone Number
* Number of Invoices
* Total Purchases
* Outstanding Balance

Customers with outstanding balances should be visually distinguishable.

Provide:

* Search
* Sorting
* Filtering

---

# Part 3 — Customer Details

Selecting a customer opens a dedicated customer profile.

Display summary cards:

* Outstanding Balance
* Total Purchases
* Total Paid
* Number of Invoices

Below that display all invoices belonging to the customer.

Columns:

* Invoice Number
* Date
* Invoice Total
* Paid
* Remaining
* Status

Status examples:

* Paid
* Partially Paid
* Outstanding

---

# Part 4 — Receive Customer Payments

If the customer has an outstanding balance, provide a button:

Receive Payment

Selecting it opens a dialog.

Display:

Outstanding Balance

Input:

Amount Received

Automatically calculate:

Remaining Balance

Support:

* Partial payment
* Full payment

Every payment must be recorded.

Payment history should remain available.

---

# Part 5 — Dashboard

Add two new KPI cards.

Card 1:

Outstanding Receivables

Displays the total money still owed by customers.

Card 2:

Customers With Outstanding Balance

Displays the number of customers who still owe money.

Selecting the Outstanding Receivables card should open a dialog listing:

Customer Name

Outstanding Balance

Selecting a customer opens the customer profile.

---

# Part 6 — Reports

Add a new report:

Customer Receivables

Include:

* Customer
* Total Sales
* Total Paid
* Outstanding Balance

Support:

* Search
* Date filtering
* Sorting

---

# Part 7 — Customer Payment History

Every payment made by a customer should be recorded.

Display:

* Date
* Amount
* Related Invoice
* Remaining Balance After Payment

Nothing should ever be deleted.

The history should provide a complete audit trail.

---

# Part 8 — Business Rules

The outstanding balance must always be calculated from invoice data.

Never store duplicate values unnecessarily.

Updating payments should immediately update:

* Customer Balance
* Dashboard KPIs
* Reports
* Customer Profile

Historical invoices must remain unchanged except for payment information.

---

# Part 9 — UI Requirements

The entire feature must follow the existing Design System.

Reuse:

* Cards
* Tables
* Dialogs
* Buttons
* Search bars
* Theme helpers

Do not introduce a different visual style.

---

# Part 10 — Future Expansion

Design the architecture so future features can be added easily, including:

* Customer statements
* Printable account statements
* Customer payment receipts
* Aging reports (30 / 60 / 90 days)
* Credit limits
* Multiple payment methods

The implementation should not require major restructuring later.

---


