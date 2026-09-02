---
title: Set number of nodes on all edges
---

Sets a uniform transfinite node count on every edge of the model.

### What it does

Use this command when you need a global and consistent edge discretization before generating the final hex mesh.

The command:

- reads `Mesh/Set number of nodes on /All edges`,
- applies the same node count on all curves,
- updates replay commands to keep one global rule,
- remeshes the CAD.

### Inputs

- **1. Node count**: integer node count applied to all edges.


### Output

- All edges use the same transfinite node count.
- Mesh is regenerated with the updated global rule.

### Notes

- This operation overrides local edge-node settings in practice.
- Use this command for a quick global reset of edge discretization.
