# Data Model: Dashboard & Reports

**Phase**: 005-dashboard-reports
**Date**: 2026-06-27

> No schema changes are introduced in this phase. All entities below are read from the existing database schema established in Phases 1–4.

---

## Existing Tables Used (read-only in this phase)

### Sales
| Column | Type | Role in this phase |
|---|---|---|
| id | INTEGER PK | Join key |
| invoice_number | TEXT | Displayed in history table, Invoice Detail Dialog, Recent Activity |
| customer_name | TEXT (nullable) | Displayed in history table, Invoice Detail Dialog, Recent Activity |
| discount_amount | REAL | Used in profit formula; displayed in Sales Invoice Detail footer |
| total_amount | REAL | Displayed in summary cards, history tables, Recent Activity |
| status | TEXT | Filter: `'active'` for totals/Top Products; both for history tables |
| created_at | TEXT | Date filtering; sort order for Recent Activity |

### SaleItems
| Column | Type | Role in this phase |
|---|---|---|
| id | INTEGER PK | — |
| sale_id | INTEGER FK → Sales | Join key |
| product_id | INTEGER FK → Products | Join key for Top Selling, product name lookup |
| quantity | REAL | Top Selling Products (SUM); Profit per Line calculation |
| unit_price | REAL | Displayed in Invoice Detail line-items; Profit per Line base |
| purchase_price_at_sale | REAL NOT NULL | **Canonical profit cost basis** — Historical Cost Price column; Profit per Line; Total Profit formula |
| subtotal | REAL | Displayed in Invoice Detail; used in profit formula as revenue component |

### Purchases
| Column | Type | Role in this phase |
|---|---|---|
| id | INTEGER PK | Join key |
| invoice_number | TEXT | Displayed in history table, Invoice Detail Dialog, Recent Activity |
| supplier_name | TEXT (nullable) | Displayed in history table, Invoice Detail Dialog, Recent Activity |
| total_amount | REAL | Total Purchases summary; history table; Recent Activity |
| status | TEXT | Filter: `'active'` for totals/Top Products; both for history tables |
| created_at | TEXT | Date filtering; sort order for Recent Activity |

### PurchaseItems
| Column | Type | Role in this phase |
|---|---|---|
| id | INTEGER PK | — |
| purchase_id | INTEGER FK → Purchases | Join key |
| product_id | INTEGER FK → Products | Join key for Top Purchased, product name lookup |
| quantity | REAL | Top Purchased Products (SUM) |
| unit_price | REAL | Displayed in Purchase Invoice Detail line-items |
| subtotal | REAL | Displayed in Purchase Invoice Detail |

### Products
| Column | Type | Role in this phase |
|---|---|---|
| id | INTEGER PK | Join key; Low Stock navigation target |
| name | TEXT | Low Stock list; Top Products panels; Invoice Detail line-items |
| category | TEXT | Low Stock list |
| purchase_price | REAL | Inventory Value; Potential Stock Profit (current WAC — display-only, NOT used in historical profit) |
| selling_price | REAL | Potential Stock Profit |
| stock_quantity | REAL | Inventory Value; Potential Stock Profit; Low Stock detection; void stock check |
| reorder_level | REAL | Low Stock detection (`stock_quantity ≤ reorder_level`) |
| is_active | INTEGER | Low Stock list/count: active only; Inventory Value/Potential Stock Profit: all products |

---

## Computed / Derived Values (never stored)

| Value | Formula | Scope |
|---|---|---|
| **Inventory Value** | `SUM(stock_quantity × purchase_price)` | All products (active + inactive) |
| **Potential Stock Profit** | `SUM((selling_price − purchase_price) × stock_quantity)` | All products (active + inactive) |
| **Total Profit** (date-ranged) | `SUM(si.subtotal) − SUM(si.quantity × si.purchase_price_at_sale) − SUM(s.discount_amount)` | Active sales within date range |
| **Today's Profit** | Same formula, date range = today only | Active sales today |
| **Profit per Line** | `(unit_price − purchase_price_at_sale) × quantity` | Per SaleItems row; Sales Invoice Detail only |
| **Low Stock Count** | `COUNT(*) WHERE is_active=1 AND stock_quantity ≤ reorder_level` | Active products only |

---

## State Transitions (relevant to this phase)

```
Invoice status:  'active'  ──(Void action)──►  'voided'
                 'voided'  ──(no transition)──  (disabled; cannot re-void)
```

- Voiding a **Sale**: sets `Sales.status = 'voided'`, restores `Products.stock_quantity` for each line — single transaction.
- Voiding a **Purchase**: pre-checks all line quantities against current stock; if any fail → void blocked. If all pass: sets `Purchases.status = 'voided'`, reduces `Products.stock_quantity` — single transaction.

---

## Key Relationships (used in queries)

```
Sales (1) ──► (many) SaleItems ──► Products
Purchases (1) ──► (many) PurchaseItems ──► Products
```

- Recent Activity: `Sales UNION ALL Purchases` (no join needed; uses header columns only)
- Top Selling: `SaleItems → Sales (status filter) → Products (name)`
- Top Purchased: `PurchaseItems → Purchases (status filter) → Products (name)`
- Invoice Detail (Sale): `Sales + SaleItems → Products (name)`
- Invoice Detail (Purchase): `Purchases + PurchaseItems → Products (name)`
