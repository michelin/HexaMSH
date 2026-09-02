---
title: Remove curves
---

Removes selected and orphan curve entities from the current CAD model.

### Keyboard shortcut

- `T`

### What it does

Use `Remove curves` to delete the selected curves from the model topology.

The command:

- takes a list of input curves,
- checks that the curves are orphan (not bounding any surface),
- removes the curves,
- returns the modified CAD model.

### When to use it

Use this command when:

- an orphan curve is unnecessary after partitioning or cleanup operations,
- cleanup is required before meshing,
- you need to simplify local CAD topology.

### Inputs

- **1. Curves**: curves to remove.

### Preconditions

For a successful removal, the selected curves should:

- exist in the active model,
- be orphan (no adjacent surfaces),
- not violate CAD consistency rules.

If these conditions are not met, HexaMSH can return an error or an invalid/degraded CAD result.

### Output

- The selected curves are removed from the model.

### Basic usage

Run from the GUI `Geometry/Remove/Curves`, then select the curves to remove (double-click to finish the selection).


### Notes

- Operation is local to the selected curve.
- Using this feature changes the topology of the CAD, use with caution.
