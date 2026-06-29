<!--
SYNC IMPACT REPORT
==================
Version change: [template] → 1.0.0
New constitution — initial ratification, replacing the blank template.

Modified principles: N/A (first fill)
Added sections:
  - Core Principles (I–V)
  - Development Workflow (Phase Completion Rule, Confirmation Dialog Policy, UI Behavior Constraints)
  - Governance

Removed template sections:
  - [SECTION_2_NAME] / [SECTION_3_NAME] generic placeholders replaced with
    concrete "Development Workflow" section.

Templates checked:
  ✅ .specify/templates/plan-template.md — Constitution Check gate is generic; no update needed.
  ✅ .specify/templates/spec-template.md — No constitution-specific references; no update needed.
  ✅ .specify/templates/tasks-template.md — No constitution-specific references; no update needed.

Deferred TODOs: none.
-->

# Store Accounting System Constitution

## Core Principles

### I. Layered Architecture (NON-NEGOTIABLE)

The application is strictly divided into four layers, with dependencies flowing in one
direction only: **UI → Logic → Data Access → Foundation**.

- UI files (`ui/`) display data and collect input only. They MUST NOT import `sqlite3`
  or call `database.py` directly, and MUST NOT contain business rules (calculations,
  validation, stock logic). The one documented exception is `main_window.py` calling
  `database.backup_database()` directly for the Backup Now action, since that is a
  connection/file-level operation, not a business-logic one.
- Logic files (`auth.py`, `logic/sales_logic.py`, `logic/purchase_logic.py`,
  `logic/report_logic.py`) contain validation, calculations, and stock/voiding rules.
  They MUST NOT contain raw SQL and MUST NOT import PySide6.
- Data Access files (`auth_db.py`, `products_db.py`, `sales_db.py`, `purchases_db.py`)
  contain only parameterized SQL queries. They MUST NOT contain business rules and
  MUST NOT be imported by UI files directly.
- Foundation files (`database.py`, `config.py`) provide the SQLite connection, table
  creation, and constants only.
- No circular imports are permitted: a file in a lower layer never imports a file from
  a higher layer.

### II. Fixed Technology Stack (NON-NEGOTIABLE)

Python, PySide6, and SQLite are the only technologies used.

- No ORM (e.g. SQLAlchemy), no dependency-injection framework, and no formal
  repository-pattern abstraction beyond the plain per-table `*_db.py` files already
  defined.
- No networking, no server component, no cloud synchronization, and no external API
  integration of any kind.
- Each database action opens its own short-lived `sqlite3` connection and closes it
  when done; no connection pooling.
- All SQL MUST be parameterized; string-formatted or concatenated SQL is never
  permitted.
- Multi-step operations that touch more than one table or row (e.g. saving an invoice
  header + line items + stock update) MUST be wrapped in a single transaction — commit
  only after every step succeeds, rollback on any failure.

### III. Single-User, Single-Release Scope (NON-NEGOTIABLE)

- The application has exactly one local Admin account, stored as the single row in
  `Users`. There is no user registration, no roles, and no permissions system.
- This is a single, final release with no planned v2. The full feature set defined in
  the Blueprint MUST be built now; no feature may be deferred on the assumption that a
  future version will add it.
- Features explicitly placed in the Blueprint's "Future Extension Points" (multi-user
  accounts/roles, Tax/VAT, PDF export beyond OS print-to-PDF, in-place invoice
  editing, partial returns, advanced Reports search/filter/sort, purchase-price
  history, a dedicated Customer/Supplier database, in-app restore-from-backup, barcode
  scanners, multi-branch/warehouse tracking, cloud sync, any networked or multi-user
  feature) MUST NOT be implemented. Reintroducing any of them requires first amending
  the Blueprint, not adding them directly during implementation.

### IV. Financial Data Integrity & Audit Trail (NON-NEGOTIABLE)

- Sales and Purchase invoices are never deleted once saved. Mistakes are corrected by
  **voiding**, which sets the invoice's `status` to `'voided'`, reverses its stock
  effect, and keeps it visible in history for audit purposes.
- Voiding a Sale always succeeds and restores the sold quantities to stock. Voiding a
  Purchase first validates that sufficient stock remains for every line (i.e. it hasn't
  already been sold onward); if not, the void is blocked entirely rather than partially
  applied.
- An invoice can only be voided once; an already-voided invoice's Void action is
  disabled.
- A Product can be hard-deleted only if it has never appeared in any
  `SaleItems`/`PurchaseItems` row. Otherwise, deletion is replaced by **deactivation**
  (`is_active = 0`), which is reversible (Reactivate) and never destroys historical
  invoice data.
- `is_active` is a single global rule, not a per-screen one: an inactive product is
  hidden from both the Sales and Purchases product pickers identically, and from search
  results by default. There MUST be exactly one shared function for fetching active
  products, reused by both screens.
- Reports/Dashboard totals (Total Sales, Total Purchases, Total Profit) are computed
  over `active` invoices only; voided invoices remain visible in history tables but are
  excluded from these sums.

### V. Fail Safely, Never Silently

- Input MUST be validated before any database call is made; invalid data never reaches
  the database.
- Every database error, validation failure, and business-rule violation (insufficient
  stock, deleting a referenced product, voiding a purchase whose stock is already sold,
  etc.) MUST be surfaced to the user via a clear, friendly message (e.g. a
  `QMessageBox`). A raw Python traceback must never reach the user.
- A top-level safeguard MUST wrap critical actions (login, save invoice, void invoice,
  backup) so that any unexpected exception is caught, logged for the developer, and
  shown to the user as a generic friendly message rather than crashing the application.

## Development Workflow

### Phase Completion Rule (NON-NEGOTIABLE)

Implementation proceeds in the phases defined in the Implementation Plan
(Foundation/Shell/Auth → Products → Purchases → Sales → Dashboard/Reports → Final
Polish), strictly bottom-up within each phase (data access → business logic → UI).
For every phase:

- The application MUST remain fully runnable at the end of the phase.
- Every feature completed in that phase MUST be manually testable end-to-end.
- No phase may be considered complete while leaving the project in a broken or
  partially integrated state — a phase is either finished and demoable, or not yet
  merged.
- A phase's defined manual testing checkpoints must all pass before the next phase
  begins.

### Confirmation Dialog Policy

A confirmation prompt is required only for actions that are destructive or could
silently discard unsaved work: Delete Product, Deactivate Product, Void Invoice, and
Clear/Reset Invoice (only when at least one line item exists). Logout and Backup Now
never require a pre-action confirmation, since neither is destructive — a post-action
result message is sufficient for Backup Now.

### UI Behavior Constraints

- The Login window is fixed-size. The Main Window is resizable with a minimum size of
  900×600.
- Operations involving disk I/O or a noticeable delay (Save Invoice, Void Invoice, CSV
  Export, Print, Backup Now) MUST display a busy/wait cursor for their duration — no
  progress bars or modal progress dialogs are used.
- Specified keyboard-focus behaviors (Login auto-focuses Username; Sales/Purchases
  auto-focus Quantity after product selection and return focus to the product picker
  after a line is added) are part of the required behavior of their respective screens,
  not optional polish.

## Governance

This Constitution is derived entirely from the approved `BLUEPRINT.md` and
`IMPLEMENTATION_PLAN.md` and supersedes any conflicting assumption made during
Spec-Kit specification or implementation. Every `/speckit-specify`, `/speckit-plan`,
and `/speckit-tasks` artifact, and every `/speckit-analyze` check, must comply with
the principles above; any apparent conflict must be resolved by adjusting the spec,
plan, or tasks — never by diluting this Constitution.

Any change to a principle in this document requires first amending `BLUEPRINT.md`
(and `IMPLEMENTATION_PLAN.md` if the change affects build order or phase scope),
since this Constitution introduces no decision that does not already exist in those
two documents. Amendments use semantic versioning: MAJOR for principle removals or
redefinitions, MINOR for new principles, PATCH for wording clarifications that change
no behavior.

**Version**: 1.0.0 | **Ratified**: 2026-06-27 | **Last Amended**: 2026-06-27
