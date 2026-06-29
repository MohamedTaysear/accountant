# Quickstart Validation Guide: Dashboard & Reports

**Phase**: 005-dashboard-reports
**Date**: 2026-06-27
**Prerequisites**: Phases 1–4 complete and passing all their manual testing checkpoints. The database contains at least: 2 active products, 1 inactive product, 1 active sale invoice (with a known customer name), 1 active purchase invoice (with a known supplier name). At least one product should be at or below its reorder level.

---

## Setup

```powershell
cd C:\accountant\accounting_system
python main.py
```

Log in with the default Admin credentials.

---

## Validation Scenarios

### S1 — Dashboard Summary Cards

1. Navigate to **Dashboard**.
2. Confirm **10 cards** are visible: Total Products, Active Products, Inactive Products, Inventory Value, Potential Stock Profit, Today's Sales, Today's Purchases, Today's Profit, Total Profit, Low Stock Count.
3. Cross-check manually:
   - Total Products = active count + inactive count
   - Inventory Value = manually sum `stock_quantity × purchase_price` for all products (open Products page)
   - Potential Stock Profit = manually sum `(selling_price − purchase_price) × stock_quantity` for all products
   - Today's Sales = sum of `total_amount` for active sales created today
4. Confirm **Today's Profit and Total Profit** cards are displayed in a **green/success color**.
5. Confirm **Low Stock Count** card is displayed in an **amber/warning color**.

### S2 — Profit Isolation from Purchase Price Changes

1. Note the current **Total Profit** value on the Dashboard.
2. Go to **Purchases**, create a new purchase for a product already in an existing sale, at a **different price** (higher or lower).
3. Return to **Dashboard**.
4. Confirm **Total Profit is unchanged** — the new purchase price must not affect historical profit.
5. Confirm **Inventory Value has changed** (it uses the current WAC).

### S3 — Low Stock List and Navigation

1. Confirm the **Low Stock list** shows only active products at or below their reorder level, with columns: Name, Category, Current Stock, Reorder Level.
2. Confirm an **inactive product** does not appear in the list even if its stock is below the reorder level.
3. **Click** a product row in the Low Stock list.
4. Confirm the app navigates to the **Products page** with that product highlighted or pre-filtered.

### S4 — Recent Activity

1. On the Dashboard, confirm the **Recent Activity** section shows up to 10 rows, newest first.
2. Each row shows: Invoice Number, Type (Sale or Purchase), Date, Customer/Supplier Name (blank if not set), Total Amount.
3. Save a new sale invoice. Return to Dashboard. Confirm the new sale appears at the top of Recent Activity.

### S5 — Reports Date Presets (no Apply needed)

1. Navigate to **Reports**.
2. Select **Today** — confirm summary totals and history tables update **immediately** without clicking Apply.
3. Select **Yesterday** — confirm results change accordingly.
4. Select **This Week** — confirm results span Monday to today.
5. Select **This Month** — confirm results span the 1st to today.
6. Select **Custom Range** — confirm the date pickers become enabled and the Apply button activates.
7. Set From > To, click Apply — confirm a validation error is shown and results do not change.
8. Set a valid Custom Range and click Apply — confirm results update correctly.

### S6 — Invoice History and Detail Dialog (Sale)

1. In Reports (All Time via any preset covering the test data), double-click a **Sales** history row.
2. Confirm the **Invoice Detail Dialog** opens showing:
   - Invoice Number, Date, Status, Customer Name
   - Line-items table with columns: Product, Qty, Unit Price, **Historical Cost Price**, **Profit / Line**, Subtotal
   - Footer: Subtotal → Discount → Grand Total
3. Manually verify Historical Cost Price matches `purchase_price_at_sale` for that sale (cross-check against when the sale was made).
4. Manually verify Profit / Line = `(unit_price − historical_cost_price) × quantity`.

### S7 — Invoice Detail Dialog (Purchase)

1. Double-click a **Purchases** history row.
2. Confirm the dialog shows: Invoice Number, Date, Status, Supplier Name, line-items (Product, Qty, Unit Price, Subtotal), Grand Total.
3. Confirm **no Historical Cost Price or Profit / Line columns** appear for purchases.

### S8 — Void a Sale from Invoice Detail

1. Open a **Sale** invoice in the Invoice Detail Dialog.
2. Note the product stock quantities on the Products page first.
3. Click **Void Invoice** — confirm a confirmation prompt appears.
4. Confirm → confirm status changes to "Voided" in the dialog header; Void button disabled.
5. Close the dialog. Confirm Reports summary totals decrease accordingly (the voided sale is excluded).
6. Confirm the relevant products' stock quantities have been restored on the Products page.

### S9 — Void a Purchase (blocked case)

1. Create a purchase for a product, then create a sale that uses all of that product's stock.
2. Open the original purchase in the Invoice Detail Dialog and attempt to Void it.
3. Confirm the void is **blocked** with a message identifying the product with insufficient stock.
4. Confirm the purchase status remains "active".

### S10 — Void a Purchase (success case)

1. Create a purchase for a product that has not been sold.
2. Open that purchase in the Invoice Detail Dialog and Void it.
3. Confirm status changes to "Voided"; stock quantity for the product decreases by the purchased amount.

### S11 — Top Products Panels

1. On the Reports page, select a date range that includes known sales and purchases.
2. Confirm **Top Selling Products** shows products ranked by total quantity sold (descending).
3. Confirm **Top Purchased Products** shows products ranked by total quantity purchased (descending).
4. Change the date filter — confirm both panels update.

### S12 — CSV Export

1. On the Reports page, click a row in the **Sales History** table (making Sales the active table).
2. Click **Export to CSV**.
3. Confirm a Save File dialog appears. Save the file.
4. Open the file — confirm it contains only **Sales** rows with correct columns and values, matching what was visible on screen.
5. Repeat: click a row in **Purchases History**, export, and confirm the CSV contains only Purchases rows.

### S13 — Print Invoice

1. Open any invoice in the Invoice Detail Dialog.
2. Click **Print** — confirm the OS print dialog opens without error.
3. Cancel the print dialog — confirm the Invoice Detail Dialog remains open.

### S14 — Regression: Phases 1–4 Features

1. Log out and log back in — confirm login still works.
2. Add and edit a product — confirm Products page is unchanged.
3. Save a new purchase invoice — confirm stock increases correctly.
4. Save a new sale invoice — confirm stock decreases correctly; discount works.
5. Confirm Backup Now still creates a timestamped backup file.
6. Confirm Change Password still works.

---

## References

- Data model: [data-model.md](data-model.md)
- Logic contracts: [contracts/report_logic.md](contracts/report_logic.md)
- UI contracts: [contracts/dashboard_page.md](contracts/dashboard_page.md), [contracts/reports_page.md](contracts/reports_page.md), [contracts/invoice_detail_dialog.md](contracts/invoice_detail_dialog.md)
- Spec: [spec.md](spec.md)
