---
title: Remove surfaces
---

Removes surface entities from the current CAD model.

### Keyboard shortcut

- `R`

### What it does

Use `Remove surfaces` to delete selected surfaces from the model topology.

The command:

- takes a list of input surfaces,
- removes that surface entities,
- returns the modified CAD model.

### When to use it

Use this command when:

- a surface is unnecessary after partitioning or imprint operations,
- cleanup is required before meshing,
- you need to simplify local CAD topology.

### Inputs

- **1. Surfaces**: list of surfaces to remove.

### Preconditions

For a successful removal, the selected surfaces should:

- exist in the active model,
- be removable under current topology/body constraints,

### Output

- The selected surfaces are removed from the model.
- Neighbor entities are updated according to CAD kernel rules.

### Basic usage

Run from the GUI `Geometry/Remove/Surfaces`, then select the surfaces to remove (double-click to finish the selection).


### Notes

- Operation is local to the selected surfaces.
- Using this feature changes the topology of the CAD, use with caution.
