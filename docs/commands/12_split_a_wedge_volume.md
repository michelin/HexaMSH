---
title: Split a wedge volume
---

Splits an existing wedge (5 faces) volume into smaller hexa volumes

### Keyboard shortcut

- `I`

### What it does

Use this command to split a wedge volume (5 faces) into smaller hexa volumes by splitting one of its triangular end faces.

The operation inserts:
- a split point at the midpoint of each edge of the selected triangular face,
- a central point at the barycenter of these split points,
- and propagates the split through the wedge to create connected hexa sub-volumes.

The original wedge topology is replaced by a refined, fully connected hexa-compatible topology.

### Inputs

- **1. Triangle surface 1 of the wedge**: the triangular start face used to drive the split.
- **2. Triangle surface 2 of the wedge**: the triangular end face used to drive the split.

### Output

- The selected wedge volume is split into multiple hexa volumes.
- Required internal points, curves, surfaces, and volume interfaces are created automatically.
- Topology is updated so all generated hexa volumes remain connected to neighboring entities.
- Invalid split attempts are rejected (for example, non-wedge targets or invalid triangular face selection).

### Basic usage

Run the split wedge volume command from the GUI, then select the wedge triangular surfaces (start and end).

### Notes

- Only wedge volumes are supported by this command.
- The driving face must be one of the wedge triangular faces.
- The intermediate points will be built, they must not be built before.
- This operation is useful for converting wedge regions into a hexa-friendly blocking configuration.
