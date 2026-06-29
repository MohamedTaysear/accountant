import os
import shutil
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

import config

_CAIRO = ZoneInfo("Africa/Cairo")


def now_cairo() -> str:
    """Return the current Egypt local time as 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now(_CAIRO).strftime("%Y-%m-%d %H:%M:%S")


def get_connection() -> sqlite3.Connection:
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS Users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Products (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT    NOT NULL,
                category       TEXT    NOT NULL DEFAULT '',
                purchase_price REAL    NOT NULL DEFAULT 0,
                selling_price  REAL    NOT NULL DEFAULT 0,
                stock_quantity REAL    NOT NULL DEFAULT 0,
                reorder_level  REAL    NOT NULL DEFAULT 5,
                is_active      INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS Sales (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT    UNIQUE NOT NULL,
                customer_name  TEXT,
                discount_amount REAL   NOT NULL DEFAULT 0,
                total_amount   REAL    NOT NULL DEFAULT 0,
                status         TEXT    NOT NULL DEFAULT 'active',
                created_at     TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS SaleItems (
                id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id               INTEGER NOT NULL,
                product_id            INTEGER NOT NULL,
                quantity              REAL    NOT NULL,
                unit_price            REAL    NOT NULL,
                purchase_price_at_sale REAL   NOT NULL,
                subtotal              REAL    NOT NULL,
                FOREIGN KEY (sale_id)     REFERENCES Sales(id),
                FOREIGN KEY (product_id)  REFERENCES Products(id)
            );

            CREATE TABLE IF NOT EXISTS Purchases (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT    UNIQUE NOT NULL,
                supplier_name  TEXT,
                total_amount   REAL    NOT NULL DEFAULT 0,
                status         TEXT    NOT NULL DEFAULT 'active',
                created_at     TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS PurchaseItems (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL,
                product_id  INTEGER NOT NULL,
                quantity    REAL    NOT NULL,
                unit_price  REAL    NOT NULL,
                subtotal    REAL    NOT NULL,
                FOREIGN KEY (purchase_id) REFERENCES Purchases(id),
                FOREIGN KEY (product_id)  REFERENCES Products(id)
            );

            CREATE TABLE IF NOT EXISTS Expenses (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_number   TEXT    UNIQUE NOT NULL,
                expense_datetime TEXT    NOT NULL,
                category         TEXT    NOT NULL,
                description      TEXT    NOT NULL,
                amount           REAL    NOT NULL,
                notes            TEXT    NOT NULL DEFAULT '',
                created_at       TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ExpenseInvoices (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number   TEXT    UNIQUE NOT NULL,
                expense_datetime TEXT    NOT NULL,
                total_amount     REAL    NOT NULL DEFAULT 0,
                created_at       TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ExpenseItems (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id  INTEGER NOT NULL,
                category    TEXT    NOT NULL,
                description TEXT    NOT NULL DEFAULT '',
                amount      REAL    NOT NULL,
                notes       TEXT    NOT NULL DEFAULT '',
                FOREIGN KEY (invoice_id) REFERENCES ExpenseInvoices(id)
            );

            CREATE TABLE IF NOT EXISTS Customers (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                phone      TEXT    NOT NULL DEFAULT '',
                created_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Payments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id     INTEGER NOT NULL,
                sale_id         INTEGER NOT NULL,
                amount          REAL    NOT NULL,
                notes           TEXT    NOT NULL DEFAULT '',
                remaining_after REAL    NOT NULL DEFAULT 0,
                payment_date    TEXT    NOT NULL,
                created_at      TEXT    NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES Customers(id),
                FOREIGN KEY (sale_id)     REFERENCES Sales(id)
            );
        """)
        conn.commit()

        for ddl in [
            "ALTER TABLE Sales ADD COLUMN customer_id INTEGER REFERENCES Customers(id)",
            "ALTER TABLE Sales ADD COLUMN amount_paid REAL NOT NULL DEFAULT 0",
        ]:
            try:
                conn.execute(ddl)
            except Exception:
                pass
        conn.commit()
    finally:
        conn.close()


def backup_database() -> str:
    os.makedirs(config.BACKUPS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"store_backup_{timestamp}.db"
    dst       = os.path.join(config.BACKUPS_DIR, filename)
    shutil.copy2(config.DB_PATH, dst)
    return dst


def backup_to(dst_path: str) -> None:
    """Copy the live database to dst_path using SQLite's safe backup API."""
    src = get_connection()
    try:
        dst = sqlite3.connect(dst_path)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()


def restore_from(src_path: str) -> None:
    """Replace the live database with src_path using SQLite's safe backup API."""
    src = sqlite3.connect(src_path)
    try:
        dst = get_connection()
        try:
            src.backup(dst)
            dst.commit()
        finally:
            dst.close()
    finally:
        src.close()
