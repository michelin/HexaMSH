---
title: Add a surface by curve loop
---

Creates a new surface from a selected closed loop of curves.

### Keyboard shortcut

- `Z`

### What it does

Use this command to create a surface filling bounded by existing curves.
The selected curves must define a valid closed loop.

### Inputs

- **1. Curve loop**: a closed sequence of connected curves.

### Output

- A new surface is created from the selected curve loop.
- If a common surface already exists for that loop, creation is rejected.

### Basic usage

Run from the GUI `Geometry/Add/A surface by curve loop`, then select curves until the loop is closed.

### Notes

- Curves must form a closed loop with consistent connectivity.
- This command is useful to cap openings and prepare split operations.
- This command does not fragment any existing entity. It juste creates a new surface between existing curves.
