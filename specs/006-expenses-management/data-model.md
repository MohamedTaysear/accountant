# Data Model: Expenses Management

**Feature**: 006-expenses-management
**Date**: 2026-06-28

---

## New Table: Expenses

```sql
CREATE TABLE IF NOT EXISTS Expenses (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_number   TEXT    UNIQUE NOT NULL,         -- e.g. EXP-000001
    expense_datetime TEXT    NOT NULL,                -- 'YYYY-MM-DD HH:MM:SS' (Cairo time, user-editable)
    category         TEXT    NOT NULL,                -- free-text, case-preserved as first entered
    description      TEXT    NOT NULL,
    amount           REAL    NOT NULL,                -- must be > 0
    notes            TEXT    NOT NULL DEFAULT '',     -- optional
    created_at       TEXT    NOT NULL                 -- 'YYYY-MM-DD HH:MM:SS' (Cairo time, immutable audit stamp)
);
```

### Field Notes

| Field | Constraint | Notes |
|-------|-----------|-------|
| `expense_number` | UNIQUE, NOT NULL | Format `EXP-{id:06d}`. Generated at insert: row inserted with `'PENDING'`, then updated to real number within the same transaction. |
| `expense_datetime` | NOT NULL | Defaults to `database.now_cairo()` in the dialog but user can override. Stored as TEXT `'YYYY-MM-DD HH:MM:SS'`. |
| `category` | NOT NULL | Free-text. No FK to a category table. Suggestions derived via `SELECT DISTINCT category FROM Expenses COLLATE NOCASE`. |
| `amount` | NOT NULL, > 0 | Validated in logic layer before any DB write. |
| `notes` | NOT NULL DEFAULT '' | Empty string when user leaves blank; never NULL. |
| `created_at` | NOT NULL | Set once at insert via `database.now_cairo()`; never updated on edit. |

---

## Derived Concept: Expense Category

- **Not a table** — inferred dynamically from `Expenses.category`.
- Fetched as `SELECT DISTINCT category FROM Expenses COLLATE NOCASE ORDER BY category`.
- Case-insensitive deduplication: "Rent" and "rent" yield one suggestion row.
- Display casing reflects whichever value SQLite returns (NOCASE collation returns the row as stored).
- No separate management screen.

---

## Changes to Existing Tables

**None.** The `Expenses` table is entirely independent. No columns are added to any existing table.

---

## Changes to `database.py`

`initialize_database()` must include the `CREATE TABLE IF NOT EXISTS Expenses` DDL above. No other changes to `database.py`.

---

## Key Queries

### Insert expense (within transaction)

```sql
INSERT INTO Expenses (expense_number, expense_datetime, category, description, amount, notes, created_at)
VALUES ('PENDING', ?, ?, ?, ?, ?, ?);
-- get last_insert_rowid() → id
-- UPDATE Expenses SET expense_number = 'EXP-{id:06d}' WHERE id = ?;
```

### Get all expenses (main page, sorted newest first)

```sql
SELECT * FROM Expenses ORDER BY expense_datetime DESC, id DESC;
```

### Search expenses (real-time filter)

```sql
SELECT * FROM Expenses
WHERE expense_number  LIKE ? COLLATE NOCASE
   OR category        LIKE ? COLLATE NOCASE
   OR description     LIKE ? COLLATE NOCASE
   OR notes           LIKE ? COLLATE NOCASE
ORDER BY expense_datetime DESC, id DESC;
-- bind '%{term}%' for each placeholder
```

### Get expenses for report (with date + category + search filters)

```sql
SELECT * FROM Expenses
WHERE DATE(expense_datetime) BETWEEN ? AND ?
  AND (? IS NULL OR category = ? COLLATE NOCASE)
  AND (? IS NULL OR (
        expense_number  LIKE ? COLLATE NOCASE OR
        category        LIKE ? COLLATE NOCASE OR
        description     LIKE ? COLLATE NOCASE OR
        notes           LIKE ? COLLATE NOCASE
      ))
ORDER BY expense_datetime DESC, id DESC;
```

### Dashboard — today's expenses

```sql
SELECT COALESCE(SUM(amount), 0.0) FROM Expenses
WHERE DATE(expense_datetime) = DATE('now', 'localtime');
-- Use Python date string for consistency: WHERE DATE(expense_datetime) = ?
```

### Dashboard — this month's expenses

```sql
SELECT COALESCE(SUM(amount), 0.0) FROM Expenses
WHERE DATE(expense_datetime) BETWEEN ? AND ?;
-- bind (first_of_month, today)
```

### Dashboard — total all-time expenses (for Net Profit)

```sql
SELECT COALESCE(SUM(amount), 0.0) FROM Expenses;
```

### Distinct categories

```sql
SELECT DISTINCT category FROM Expenses COLLATE NOCASE ORDER BY category;
```
