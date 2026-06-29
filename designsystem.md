# Phase 7 — Design System & UI Modernization

This is **not** a new feature phase.

This phase focuses on creating a unified design system and modernizing the entire application's user interface while preserving all existing functionality.

The objective is to make every screen feel like part of one professional desktop application.

No business logic should change during this phase.

---

# Goal

Create a consistent, modern desktop UI suitable for long daily use in a business/accounting environment.

The application should feel:

* Clean
* Professional
* Fast
* Consistent
* Easy to scan
* Comfortable during long working hours

The visual style should resemble a modern Windows business application rather than a colorful consumer application.

---

# Design Principles

The UI should follow these principles:

* Consistency over creativity.
* Simplicity over decoration.
* Readability over visual effects.
* Information hierarchy must always be obvious.
* Similar actions must always look the same.
* Similar screens must always behave the same.

---

# Design System

Create a shared design system that will be reused by every page.

It should define:

## Color Palette

Standard application colors including:

* Primary
* Secondary
* Success
* Warning
* Error
* Background
* Surface
* Border
* Primary Text
* Secondary Text

Profit-related values should always use the Success color.

Warnings should always use the Warning color.

Errors and negative values should always use the Error color.

---

## Typography

Define:

* Application font
* Heading sizes
* Section titles
* Labels
* Table text
* KPI numbers

Text sizes should remain consistent across the application.

---

## Spacing System

Adopt one spacing scale throughout the application.

For example:

* Small
* Medium
* Large

All pages should use the same spacing rules.

---

## Component Library

Create a visual standard for:

* Buttons
* Text boxes
* Combo boxes
* Spin boxes
* Date fields
* Search fields
* Tables
* Cards
* Group boxes
* Dialogs
* Message boxes

Each component should have one consistent appearance throughout the application.

---

## Button Styles

Define consistent styles for:

* Primary actions
* Secondary actions
* Destructive actions
* Disabled state
* Hover state
* Focus state

Buttons performing the same type of action should always look identical.

---

## Table Standards

All tables must follow the same visual rules.

Standardize:

* Header style
* Row height
* Alternate row colors
* Selection color
* Hover effect
* Grid visibility
* Empty state appearance
* Column spacing

Every table in the application should immediately feel related.

---

## Cards

Dashboard cards must share one common design language.

Standardize:

* Padding
* Border radius
* Shadows
* Value alignment
* Title placement
* Icon placement

All KPI cards should appear visually balanced.

---

## Icons

Adopt a single icon family throughout the application.

Icons should be used consistently for:

* Navigation
* Buttons
* Status indicators
* Dashboard cards
* Dialogs

---

## Dialog Standards

All dialogs should share:

* Layout
* Spacing
* Buttons
* Header style
* Typography

Confirmation dialogs should feel identical regardless of which feature opens them.

---

## Empty States

Replace empty-looking tables with consistent empty-state messaging.

Each empty state should clearly explain why no data is displayed.

---

## Accessibility

Improve usability by ensuring:

* Strong color contrast
* Clear focus indicators
* Comfortable spacing
* Readable font sizes
* Keyboard-friendly navigation

---

# Scope

This phase defines the visual system only.

It should not:

* Add new business features.
* Modify calculations.
* Change workflows.
* Introduce database changes.

Subsequent UI modernization work will implement this design system across each page.

---

# Deliverables

Update the existing specification to include:

* The complete Design System.
* UI standards.
* Component standards.
* Accessibility guidelines.
* Consistency rules.
* Visual language.

Do not begin implementation yet.

This phase establishes the visual foundation that every subsequent UI modernization task must follow.
