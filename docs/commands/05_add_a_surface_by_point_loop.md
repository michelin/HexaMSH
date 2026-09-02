---
title: Add a surface by point loop
---

Creates a new surface from a selected closed loop of points.

### Keyboard shortcut

- `E`

### What it does

Use this command to create a surface from ordered points.
Missing boundary curves between successive points are created when needed.

### Inputs

- **1. Point loop**: a closed sequence of connected points.

### Output

- A new surface is created from the point loop.
- Required boundary curves can be created automatically.
- If a common surface already exists for that point loop, creation is rejected.

### Basic usage

Run from the GUI `Geometry/Add/A surface by point loop`, then select points to form a closed loop.

### Notes

- The point loop must be geometrically valid and closed.
- This command is useful when curves do not exist yet but point topology is available.
- This command does not fragment any existing entity. It juste creates a new surface between curves, creating new curves if needed. If you need to fragment a surface by new curves, use [split volume by a point loop](../10_split_volume_by_point_loop/) instead.