# Feature Specification: Design System & UI Modernization

**Feature Branch**: `007-design-system`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "read designsystem.md and create a specification"

## Clarifications

### Session 2026-06-28

- Q: Should empty tables show two distinct messages (no data exists vs. search returned no results), or one generic message? → A: Two distinct messages — "no records yet" for empty data, "no results match your search" when a filter or search returns nothing.
- Q: How should long text values be handled in table cells? → A: Truncate with ellipsis (…) and show full value as a tooltip on hover; rule applies to all text columns in all tables.
- Q: What minimum contrast ratio should the color palette target for text on background colors? → A: WCAG AA — 4.5:1 for normal text, 3:1 for large text and headings.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Consistent Visual Identity Across All Screens (Priority: P1)

A business operator who uses the application daily opens every screen — Dashboard, Products, Sales, Purchases, Expenses, Reports — and immediately recognizes a single, unified visual language. Fonts, spacing, colors, button styles, and table layouts are indistinguishable in their consistency. No screen looks like it was built separately.

**Why this priority**: This is the foundational goal of the entire phase. Without a shared visual language, every subsequent user story cannot be measured. All other improvements depend on the design system being defined and applied first.

**Independent Test**: Can be validated by opening each of the six main screens and confirming that typography, color usage, spacing, and button styles match the defined design system without any screen-specific overrides.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** a user navigates between Dashboard, Products, Sales, Purchases, Expenses, and Reports, **Then** every screen uses the same font family, the same heading size hierarchy, the same background and surface colors, and the same button styles for equivalent actions.
2. **Given** a profit value is displayed anywhere in the application, **When** the user views it, **Then** it is always rendered in the designated Success color.
3. **Given** an error or negative value is displayed anywhere in the application, **When** the user views it, **Then** it is always rendered in the designated Error color.

---

### User Story 2 — Standardized Tables and Data Display (Priority: P2)

A user who works with large transaction lists every day finds that every table in the application — Sales history, Purchase history, Expense history, Products list, Reports — looks and behaves identically. Row height, alternating row colors, selection highlighting, header styling, column spacing, and empty-state messages are uniform.

**Why this priority**: Tables are the most used UI element in the application. A consistent table experience directly reduces visual fatigue and cognitive load during long working sessions.

**Independent Test**: Can be validated by comparing the Products table, Sales history table, and Reports expenses table side by side and confirming all visual properties are identical.

**Acceptance Scenarios**:

1. **Given** any table in the application contains data, **When** the user views it, **Then** it displays with consistent row height, alternating row background colors, and a clearly styled header row.
2. **Given** any table in the application contains no data, **When** the user views it, **Then** it shows a clear, friendly empty-state message explaining why no data is shown.
3. **Given** the user clicks a row in any table, **When** the row is selected, **Then** it highlights using the same selection color across all tables.

---

### User Story 3 — Consistent Buttons and Interactive Controls (Priority: P3)

A user performing similar actions across different screens — saving an invoice in Sales, saving an invoice in Purchases, saving an expense invoice — sees identically styled "Save Invoice" buttons. Destructive actions like Delete always look the same. Secondary actions like Cancel always look the same. The user never has to search for the right button.

**Why this priority**: Button consistency is essential for predictable interaction. Users build muscle memory from visual cues; inconsistent button styling breaks that trust and increases errors.

**Independent Test**: Can be validated by comparing the Save, Cancel, and Delete buttons on the Sales page, Purchases page, and Expenses page and confirming they are visually identical for equivalent action types.

**Acceptance Scenarios**:

1. **Given** a primary action button (Save Invoice, Add Product) exists on any screen, **When** the user views it, **Then** it uses the Primary action style defined in the design system.
2. **Given** a destructive action button (Delete, Void) exists on any screen, **When** the user views it, **Then** it uses the Destructive action style defined in the design system.
3. **Given** any interactive control (text input, combo box, date field) exists on any screen, **When** the user focuses it, **Then** it shows a clear, consistent focus indicator.

---

### User Story 4 — Modernized Dashboard Cards (Priority: P4)

A user opening the Dashboard each morning sees a clean row of KPI cards that feel part of one unified design. Padding, border radius, shadow depth, value alignment, and title placement are uniform across all cards regardless of the metric displayed.

**Why this priority**: The Dashboard is the first screen users see. Consistent, professional cards create a strong first impression and make numbers easier to scan quickly.

**Independent Test**: Can be validated by inspecting all Dashboard KPI cards and confirming equal padding, consistent label/value alignment, and uniform visual weight.

**Acceptance Scenarios**:

1. **Given** the Dashboard is displayed, **When** the user views the KPI cards, **Then** all cards share identical padding, border radius, and shadow styling.
2. **Given** a KPI card displays a monetary value, **When** the value is a profit, **Then** it uses the Success color; when it represents an expense or cost, it uses the appropriate color designation from the design system.

---

### User Story 5 — Accessible and Comfortable for Long Daily Use (Priority: P5)

A user who works in the application for 6–8 hours per day reports no eye strain from poor contrast, no confusion from missing focus indicators, and no discomfort from tight or inconsistent spacing. The application meets readability and accessibility standards appropriate for a business desktop tool.

**Why this priority**: The constitution specifies the application must be comfortable during long working hours. Accessibility improvements directly support daily operator well-being and reduce errors caused by visual fatigue.

**Independent Test**: Can be validated by reviewing each screen against the defined contrast, spacing, and keyboard navigation requirements.

**Acceptance Scenarios**:

1. **Given** any text label or value in the application, **When** displayed on its background color, **Then** the contrast ratio is at least 4.5:1 for normal text and at least 3:1 for large text and headings (WCAG AA).
2. **Given** the user navigates entirely by keyboard, **When** focus moves between controls, **Then** every focused element displays a clearly visible focus indicator.
3. **Given** all screens, **When** the user inspects spacing between form labels, inputs, and table rows, **Then** a single consistent spacing scale is applied throughout with no outliers.

---

### Edge Cases

- What happens when a theme color is applied to a widget that does not support stylesheet overrides? The design system must define a fallback strategy.
- How does the empty-state message differ when a table is empty because no data exists versus because a search returned no results? **Resolved: two distinct messages — "no records yet" for empty data, "no results match your search" when a filter or search returns nothing.**
- What happens to the application appearance if the system OS theme changes while the application is running? The design system should define whether it responds to OS theme changes or maintains a fixed palette.
- How are very long text values (product names, customer names) handled in table cells? **Resolved: truncate with ellipsis (…) and display the full value as a tooltip on hover. Rule applies consistently to all text columns in all tables.**

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST define a centralized design system that specifies the complete color palette, typography scale, spacing scale, and component visual standards.
- **FR-002**: The design system MUST be implemented as a shared resource that every page and dialog references, rather than duplicating styles per screen.
- **FR-003**: Every button performing a primary action (Save, Add, Confirm) MUST use an identical visual style throughout the application.
- **FR-004**: Every button performing a destructive action (Delete, Void, Clear) MUST use an identical visual style throughout the application, visually distinct from primary actions.
- **FR-005**: Every table in the application MUST share the same visual rules: header style, row height, alternating row colors, selection color, column spacing, and grid visibility. Text that overflows a cell MUST be truncated with an ellipsis (…) and the full value MUST be displayed as a tooltip on hover.
- **FR-006**: Every table MUST display a meaningful empty-state message when no rows are present. Two distinct messages are required: one for the case where no records exist yet (e.g., "No products added yet"), and a separate message for the case where a search or filter returned no results (e.g., "No results match your search").
- **FR-007**: Profit-related values MUST always be rendered using the designated Success color throughout the application.
- **FR-008**: Error conditions and negative values MUST always be rendered using the designated Error color throughout the application.
- **FR-009**: All Dashboard KPI cards MUST share identical layout rules: padding, border radius, shadow, value alignment, and title placement.
- **FR-010**: All dialogs (detail dialogs, confirmation dialogs, input dialogs) MUST share identical layout, spacing, button placement, and typography.
- **FR-011**: A single icon family MUST be adopted and used consistently across navigation, buttons, status indicators, dashboard cards, and dialogs.
- **FR-012**: The application MUST provide sufficient color contrast between text and background throughout all screens. The color palette MUST achieve a minimum contrast ratio of 4.5:1 for normal-sized text and 3:1 for large text and headings (WCAG AA standard).
- **FR-013**: Every interactive control MUST display a clearly visible focus indicator when focused via keyboard.
- **FR-014**: A single spacing scale MUST be adopted and applied consistently across all pages, forms, and tables.
- **FR-018**: All visual styling MUST be centralized in shared design resources. Widget-specific inline styling MUST be avoided wherever reasonably possible. Common visual elements — buttons, tables, cards, dialogs, search fields — MUST share reusable style definitions rather than duplicating appearance logic across individual screens. Changing the color palette, typography, spacing, border radius, or button appearance MUST require updating only the centralized design resources, not individual pages or dialogs.
- **FR-019**: The design system architecture MUST support future theme expansion (e.g., Dark theme, High Contrast theme) without requiring modifications to individual screens or dialogs. Screen code MUST depend only on the theme API — not on hardcoded color values or style definitions. Only the Light theme is implemented in this phase; the architecture must make adding additional themes a self-contained change to the design system module alone.
- **FR-015**: No business logic, calculations, or workflows MUST be altered during this phase — the scope is visual only.
- **FR-016**: No database schema changes MUST be made during this phase.
- **FR-017**: All existing functionality MUST remain fully operational after design system application.

### Key Entities

- **Design System**: The centralized definition of color palette, typography, spacing scale, and component standards. Acts as the single source of truth for all visual decisions.
- **Color Palette**: Named semantic colors (Primary, Secondary, Success, Warning, Error, Background, Surface, Border, Primary Text, Secondary Text) used consistently across the application.
- **Typography Scale**: Defined font family and size hierarchy covering headings, section titles, labels, table text, and KPI numbers.
- **Spacing Scale**: Named spacing values (Small, Medium, Large) applied to margins, padding, and gaps throughout all screens.
- **Component Standard**: Per-component visual rules (e.g., button states, table row height, card padding) that define a consistent appearance for each reusable UI element.
- **Centralized Design Resources**: The small set of shared files or modules that own all visual styling definitions. Every screen and dialog derives its appearance from these resources; no screen owns its own independent style definitions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user navigating all six main screens can identify no visual inconsistency in font family, button style for equivalent actions, or table layout between any two screens.
- **SC-002**: Every table in the application displays a non-empty, explanatory message when no rows are present — zero tables show a blank, unexplained empty area. Tables that are empty because no data exists show a "no records yet" message; tables empty due to a search or filter show a "no results" message.
- **SC-003**: Profit values appear in the Success color and error/negative values appear in the Error color on 100% of screens where they are displayed.
- **SC-004**: All Dashboard KPI cards pass a visual inspection for equal padding, consistent value alignment, and uniform card size under the same window dimensions.
- **SC-005**: Every interactive control (text field, combo box, date field, button) displays a visible focus indicator when navigated to by keyboard.
- **SC-006**: No functional regression is introduced: all existing Save, Delete, Void, Search, Filter, Export, and Backup operations continue to work correctly after the design system is applied.
- **SC-007**: A single spacing scale is verifiable across all form layouts, table rows, and card interiors — no screen uses ad-hoc spacing values outside the defined scale.
- **SC-008**: All color combinations used for text on background in the application achieve a minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text and headings, verifiable using a standard contrast-checking tool.
- **SC-009**: Changing any single design token (color, font size, spacing value, border radius) in the centralized design resources produces the corresponding visual change across all screens without requiring edits to individual page files.
- **SC-010**: A future Dark theme can be added by creating a new theme definition that overrides the token values defined in the Light theme — without modifying any screen, dialog, or widget file.

## Assumptions

- The design system targets a Windows desktop environment; platform-specific widget theming quirks are handled via the application's stylesheet override mechanism rather than OS-native controls.
- A fixed, application-defined color palette is used regardless of the OS dark/light mode setting; the application does not dynamically respond to OS theme changes in this phase.
- Icon integration is in scope for this specification but the specific icon library will be selected during the planning phase based on compatibility with the existing PySide6 technology stack.
- The application font will be a system-available font chosen for readability at standard desktop DPI; custom font embedding is not required.
- "No business logic changes" means all existing calculations, validation rules, workflows, and database interactions remain untouched; only visual presentation code is modified.
- Keyboard accessibility improvements are limited to visible focus indicators and comfortable spacing; full WCAG compliance and screen-reader support are out of scope.
- This phase defines the design system and applies it across all screens; no screen is left partially styled at the end of this phase.
