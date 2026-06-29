# Quickstart Validation Guide: Customer Credit & Receivables

**Feature**: 008-customer-credit-receivables | **Date**: 2026-06-29

## Prerequisites

- Application runs without errors from `accounting_system/main.py`
- At least one Product exists in the system
- No prior data required for Customers or Payments tables

## Scenario 1 — Full Payment (Default Behavior Unchanged)

1. Navigate to **Sales**.
2. Select a customer from the customer dropdown (or add a new one: "Test Customer", phone "01000000000").
3. Add one product line item.
4. Verify "Paid in Full" checkbox is checked by default. No extra payment fields visible.
5. Save the invoice.
6. Navigate to **Customers**. Verify "Test Customer" appears with Outstanding Balance = 0.

**Expected**: Existing full-payment workflow unchanged. Customer created and linked to invoice.

---

## Scenario 2 — Partial Payment on New Invoice

1. Navigate to **Sales**. Select "Test Customer".
2. Add a product. Note the invoice total (e.g., 1000).
3. Uncheck "Paid in Full". Verify three fields appear: Invoice Total (read-only), Amount Paid (editable), Remaining Balance (calculated).
4. Enter Amount Paid = 400. Verify Remaining Balance = 600 (updates immediately).
5. Try entering Amount Paid = 1500 → verify save is blocked with a validation error.
6. Try entering Amount Paid = -100 → verify save is blocked.
7. Enter Amount Paid = 400 again. Save the invoice.

**Expected**: Invoice saves. Navigate to Customers → "Test Customer" shows Outstanding Balance = 600.

---

## Scenario 3 — Customer Profile

1. Navigate to **Customers**. Click on "Test Customer".
2. Verify four summary cards: Outstanding Balance = 600, Total Purchases = 1000, Total Paid = 400, Number of Invoices = 1 (or more from Scenario 1).
3. In the Invoices tab, verify the partial invoice shows Status = "Partially Paid", Paid = 400, Remaining = 600.
4. Verify the full-payment invoice from Scenario 1 shows Status = "Paid".

**Expected**: Profile reflects correct per-invoice FIFO-derived values.

---

## Scenario 4 — Receive Payment (Partial Settlement)

1. On "Test Customer" profile, click **Receive Payment**.
2. Dialog shows Outstanding Balance = 600. Enter Amount = 200. Verify "Remaining After Payment" = 400.
3. Try entering Amount = 700 → verify blocked with validation error.
4. Enter Amount = 200. Confirm.
5. Verify Outstanding Balance on profile updates to 400 without navigating away.
6. Click Payment History tab → verify entry: today's date, Amount = 200.

**Expected**: Payment recorded. Balance reduced to 400.

---

## Scenario 5 — Receive Payment (Full Settlement)

1. On "Test Customer" profile (Outstanding Balance = 400), click **Receive Payment**.
2. Enter Amount = 400. Confirm.
3. Verify Outstanding Balance = 0. "Receive Payment" button hidden or disabled.
4. In Invoices tab, verify partial invoice now shows Status = "Paid" (FIFO fully absorbed).

**Expected**: Customer fully settled; all invoices show Paid status.

---

## Scenario 6 — Dashboard KPIs

1. Create a second customer "Customer B" with a partial invoice (e.g., remaining = 300).
2. Navigate to **Dashboard**.
3. Verify "Outstanding Receivables" card shows ≥ 300 (whatever the sum of outstanding balances is).
4. Verify "Customers With Balance" card shows count ≥ 1.
5. Click the "Outstanding Receivables" card → dialog lists Customer B with Outstanding Balance 300.
6. Click Customer B in the dialog → navigates to Customer B's profile.

**Expected**: KPIs accurate; clickable card navigation works.

---

## Scenario 7 — Customer Receivables Report

1. Navigate to **Reports** → **Customer Receivables** tab.
2. Verify all customers appear with correct Total Sales, Total Paid, Outstanding Balance.
3. Type "Customer B" in the search box → list filters to Customer B only.
4. Apply a date range that excludes today → verify Customer B's invoice is excluded from totals.
5. Click a column header → verify rows sort correctly.

**Expected**: Report data matches values shown in customer profiles.

---

## Scenario 8 — Void Invoice With Existing Payments

1. Create a new customer "Customer C" with a partial invoice (total 500, paid 100, remaining 400).
2. Record a payment of 200 (outstanding now 200).
3. Void the invoice from the Sales history.
4. Navigate to Customer C's profile. Verify: outstanding balance = 0 (voided invoice excluded from balance calculation), payment history still shows the 200 payment.

**Expected**: Void excludes the invoice from balance; payment history preserved for audit.

---

## Failure Cases to Verify

| Scenario | Action | Expected |
|----------|--------|----------|
| Empty customer name | Add New Customer with blank name | Error message, dialog stays open |
| Negative payment | Enter -50 in Receive Payment | Blocked by QDoubleSpinBox minimum; validation error on confirm |
| Payment > outstanding | Enter amount > balance | Validation error; payment not recorded |
| Save invoice without customer | Try to save with "(No customer selected)" | Error message, save blocked |
