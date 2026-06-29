# Data Model: Foundation, Shell & Auth

**Feature**: 001-foundation-shell-auth
**Date**: 2026-06-27

Phase 1 creates all six database tables in a single `initialize_database()` call so
that later phases can immediately insert data without schema migrations. Only the
`Users` table is written to in this phase; the other five tables are created empty and
remain unused until their respective phases.

---

## Tables Created in Phase 1

### Users *(active in Phase 1)*

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `username` | TEXT | UNIQUE NOT NULL | Single value: `"admin"` |
| `password_hash` | TEXT | NOT NULL | Format: `salt_hex:pbkdf2_hash_hex` |

**Lifecycle**:
- Created by `initialize_database()` on first run.
- Seeded by `seed_default_admin()` — exactly one row, idempotent (no insert if row count > 0).
- `username` never changes after seeding.
- `password_hash` is the only column updated in production (via `change_password()`).

**Validation rules**:
- `username`: non-empty, trimmed before storage.
- `password_hash`: never stored as plaintext; always the `salt:hash` compound string
  produced by `hash_password()`.
- New password minimum length: 4 characters (validated in `auth.py` before hashing).

---

### Products *(created empty; used from Phase 2)*

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `name` | TEXT | NOT NULL | |
| `sku` | TEXT | UNIQUE, NULLABLE | Multiple NULLs permitted by SQLite UNIQUE |
| `unit` | TEXT | NOT NULL DEFAULT `'pcs'` | Free text; e.g. pcs, kg, box, liter |
| `purchase_price` | REAL | NOT NULL DEFAULT `0` | ≥ 0 |
| `selling_price` | REAL | NOT NULL DEFAULT `0` | ≥ 0 |
| `stock_quantity` | REAL | NOT NULL DEFAULT `0` | ≥ 0; REAL to support decimal quantities |
| `reorder_level` | REAL | NOT NULL DEFAULT `5` | ≥ 0; triggers Low Stock when stock_quantity ≤ this |
| `is_active` | INTEGER | NOT NULL DEFAULT `1` | 1 = active, 0 = deactivated/archived |

---

### Sales *(created empty; used from Phase 4)*

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `invoice_number` | TEXT | UNIQUE NOT NULL | Format: `SAL-000001` |
| `customer_name` | TEXT | NULLABLE | Optional plain text |
| `discount_amount` | REAL | NOT NULL DEFAULT `0` | Invoice-level discount |
| `total_amount` | REAL | NOT NULL DEFAULT `0` | Grand total after discount |
| `status` | TEXT | NOT NULL DEFAULT `'active'` | `'active'` or `'voided'` |
| `created_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | ISO 8601 |

---

### SaleItems *(created empty; used from Phase 4)*

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `sale_id` | INTEGER | NOT NULL, FK → Sales(id) | |
| `product_id` | INTEGER | NOT NULL, FK → Products(id) | |
| `quantity` | REAL | NOT NULL | > 0; REAL for decimal support |
| `unit_price` | REAL | NOT NULL | Selling price at time of sale |
| `purchase_price_at_sale` | REAL | NOT NULL | Purchase price at time of sale (for profit) |
| `subtotal` | REAL | NOT NULL | quantity × unit_price (pre-discount) |

---

### Purchases *(created empty; used from Phase 3)*

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `invoice_number` | TEXT | UNIQUE NOT NULL | Format: `PUR-000001` |
| `supplier_name` | TEXT | NULLABLE | Optional plain text |
| `total_amount` | REAL | NOT NULL DEFAULT `0` | |
| `status` | TEXT | NOT NULL DEFAULT `'active'` | `'active'` or `'voided'` |
| `created_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | ISO 8601 |

---

### PurchaseItems *(created empty; used from Phase 3)*

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `purchase_id` | INTEGER | NOT NULL, FK → Purchases(id) | |
| `product_id` | INTEGER | NOT NULL, FK → Products(id) | |
| `quantity` | REAL | NOT NULL | > 0; REAL for decimal support |
| `unit_price` | REAL | NOT NULL | Purchase price entered on this invoice |
| `subtotal` | REAL | NOT NULL | quantity × unit_price |

---

## Relationships

```
Users               — standalone (no FK relationships)
Sales (1) ──────► (many) SaleItems
                          └──► Products(id)
Purchases (1) ───► (many) PurchaseItems
                          └──► Products(id)
```

---

## `auth.py` Function Signatures

These are the logical contracts the auth module must honour (implementation belongs in
tasks.md):

```
hash_password(password: str) -> str
    Returns "salt_hex:hash_hex" string. Uses PBKDF2-HMAC-SHA256.

verify_password(password: str, stored_hash: str) -> bool
    Splits stored_hash on ':', re-derives hash, compares with hmac.compare_digest().

seed_default_admin() -> None
    If Users table is empty, inserts one row with DEFAULT_ADMIN_USERNAME and
    hash_password(DEFAULT_ADMIN_PASSWORD). Idempotent: no-op if row exists.

check_login(username: str, password: str) -> bool
    Fetches user row by username via auth_db.get_user(); returns
    verify_password(password, row['password_hash']) or False if not found.

change_password(username: str, current_password: str,
                new_password: str, confirm_password: str) -> tuple[bool, str]
    Returns (True, "") on success; (False, error_message) on any failure.
    Validates: current password correct, new != empty, len(new) >= MIN_PASSWORD_LENGTH,
    new == confirm.
```

---

## `database.py` Function Signatures

```
get_connection() -> sqlite3.Connection
    Opens and returns a new short-lived connection to config.DB_PATH.
    Caller is responsible for commit/close (or use as context manager).

initialize_database() -> None
    Calls get_connection(), runs CREATE TABLE IF NOT EXISTS for all 6 tables,
    commits and closes. Safe to call on every startup.

backup_database() -> str
    Copies config.DB_PATH to config.BACKUPS_DIR/store_backup_YYYYMMDD_HHMMSS.db.
    Creates BACKUPS_DIR if absent. Returns the backup file path on success.
    Raises an exception (caught by caller) on failure.
```
