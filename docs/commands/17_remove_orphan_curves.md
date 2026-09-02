---
title: Remove orphan curves
---

Removes orphan curve entities from the current CAD model.

### Keyboard shortcut

- `shift + T`

### What it does

Use `Remove orphan curves` to delete all the orphan curves from the model topology.

The command:

- takes a list of curves,
- checks the curves are orphan (not bounding any surface),
- removes that orphan curves,
- returns the modified CAD model.

### When to use it

Use this command when:

- an orphan curve is unnecessary after partitioning or cleanup operations,
- cleanup is required before meshing,
- you need to simplify local CAD topology.

### Inputs

- None.

### Output

- The orphan curves are removed from the model.

### Notes

- Operation is local to the selected curve.
- Using this feature changes the topology of the CAD, use with caution.
