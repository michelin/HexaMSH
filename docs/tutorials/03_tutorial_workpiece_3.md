---
title: Tutorial 3 - Workpiece 3
---


## Goal

The goal of this tutorial is to partition `workpiece3` into meshable blocks and generate a structured hexahedral mesh.

You will use HexaMSH to partition the CAD model and generate the mesh.


## Before you begin

Download the CAD file [here](https://gitlab.michelin.com/dord/simulation/cadmesh/hexamsh/-/blob/main/hexamsh/tests/workpiece3/workpiece3.brep?ref_type=heads).

Open it from a prompt in a Python environment that contains HexaMSH:

```console
hexamsh workpiece3.brep
```

Gmsh opens with the CAD model:

<figure markdown="span">
![tuto_3_intro](../images/tuto_3_intro.png){width="700"}
</figure>

The aim is to partition the CAD model into meshable sub-volumes:

<figure markdown="span">
![tuto_3_intro_end](../images/tuto_3_intro_end.png){width="700"}
</figure>

## CAD partitioning

There are several ways to obtain this partitioning. This tutorial presents one possible workflow.

### Create the first blocks

Use [Project a surface on a surface](../../commands/02_project_surface_on_surface/) (`S`) twice, projecting each of the following surfaces down to the base of the model:

<figure markdown="span">
![tuto_3_project_surface](../images/tuto_3_project_surface.png){width="700"}
</figure>

This creates the first blocks:

<figure markdown="span">
![tuto_3_project_surface_done](../images/tuto_3_project_surface_done.png){width="700"}
</figure>


### Split the first wedge and propagate the partitioning

Partition the wedge using [Split a wedge volume](../../commands/12_split_a_wedge_volume/) (`I`):

<figure markdown="span">
![tuto_3_split_wedge](../images/tuto_3_split_wedge.png){width="700"}
</figure>

Resulting in:

<figure markdown="span">
![tuto_3_split_wedge_done](../images/tuto_3_split_wedge_done.png){width="700"}
</figure>

Propagate the partitioning created by the wedge split:

- First use [Project a point on a curve](../../commands/01_project_point_on_curve/) (`P`) and then [Split a volume by a point loop](../../commands/10_split_volume_by_point_loop/) (`L`):

<figure markdown="span">
![tuto_3_propagate_wedge](../images/tuto_3_propagate_wedge.png){width="700"}
</figure>

Repeat the same two commands to continue the partitioning:

<figure markdown="span">
![tuto_3_propagate_wedge_1](../images/tuto_3_propagate_wedge_1.png){width="700"}
</figure>

!!! tip "Play with views and geometry display"
    Use the view options in the left panel to show or hide the green and orange volumes:
    <figure markdown="span">
    ![view_pannel](../images/view_pannel.png){width="200"}
    </figure>

    For a clearer view, use the Gmsh shortcuts to show or hide surfaces (`Alt+S`), curves (`Alt+L`), and points (`Alt+P`).
    

### Partitioning around the pocket

Create the following partition around the pocket:

<figure markdown="span">
![tuto_3_pocket_split_proposition](../images/tuto_3_pocket_split_proposition.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_3_pocket_split_proposition_done](../images/tuto_3_pocket_split_proposition_done.png){width="700"}
</figure>

Use [Project a surface on a surface](../../commands/02_project_surface_on_surface/) to extend the pocket partition to the back of the model:

<figure markdown="span">
![tuto_3_pocket_till_background](../images/tuto_3_pocket_till_background.png){width="700"}
</figure>

!!! tip "Why project a surface?"
    Use [Project a surface on a surface](../../commands/02_project_surface_on_surface/) instead of [Add a volume between two surfaces](../../commands/06_add_a_volume_between_two_surfaces/), because some connecting surfaces already exist. The projection command removes duplicate geometry with `occ.removeAllDuplicates()`. The volume command does not; remove duplicates manually afterward with [Remove a surface](../../commands/16_remove_surface/) when necessary.

Propagate the partition at the back of the pocket:

<figure markdown="span">
![tuto_3_pocket_background_split_proposition](../images/tuto_3_pocket_background_split_proposition.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_3_pocket_background_split_proposition_done](../images/tuto_3_pocket_background_split_proposition_done.png){width="700"}
</figure>




### Partitioning around the fillet

Create a wedge to partition the fillet:

<figure markdown="span">
![tuto_3_wedge_fillet_proposition](../images/tuto_3_wedge_fillet_proposition.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_3_wedge_fillet_proposition_done](../images/tuto_3_wedge_fillet_proposition_done.png){width="700"}
</figure>

Split the wedge with [Split a wedge volume](../../commands/12_split_a_wedge_volume/) (`I`):

<figure markdown="span">
![tuto_3_partition_wedge](../images/tuto_3_partition_wedge.png){width="700"}
</figure>


Propagate the new partition downward:

<figure markdown="span">
![tuto_3_partition_wedge_1](../images/tuto_3_partition_wedge_1.png){width="700"}
</figure>


Link the fillet and pocket partitions with [Split a volume by a point loop](../../commands/10_split_volume_by_point_loop/) (`L`):

<figure markdown="span">
![tuto_3_link_pocket_fillet](../images/tuto_3_link_pocket_fillet.png){width="700"}
</figure>

Project the two points shown below:

<figure markdown="span">
![tuto_3_pocket_propagation](../images/tuto_3_pocket_propagation.png){width="700"}
</figure>

Then use [Split all volumes by a surface (4 points)](../../commands/08_split_all_volumes_by_surface_4_points/) (`K`) with these four points:

<figure markdown="span">
![tuto_3_4_points_split_proposition](../images/tuto_3_4_points_split_proposition.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_3_4_points_split_proposition_done](../images/tuto_3_4_points_split_proposition_done.png){width="700"}
</figure>


### Partitioning around the hole

Create the following partition around the hole:

<figure markdown="span">
![tuto_3_hole_split_proposition](../images/tuto_3_hole_split_proposition.png){width="700"}
</figure>

Use [Project a point on a curve](../../commands/01_project_point_on_curve/) (`P`) and [Split a volume by a point loop](../../commands/10_split_volume_by_point_loop/) (`L`) to create this partition:

<figure markdown="span">
![tuto_3_hole_split_done](../images/tuto_3_hole_split_done.png){width="700"}
</figure>


Split the two indicated volumes:
<figure markdown="span">
![tuto_3_hole_split_2](../images/tuto_3_hole_split_2.png){width="700"}
</figure>

The result is:
<figure markdown="span">
![tuto_3_hole_split_2_done](../images/tuto_3_hole_split_2_done.png){width="700"}
</figure>

### Final transverse splits

Finish the partition by splitting the complete model in the transverse direction:

<figure markdown="span">
![tuto_3_transverse_partitioning](../images/tuto_3_transverse_partitioning.png){width="700"}
</figure>

Complete this in three steps.

First, use [Split all volumes by a plane (3 points)](../../commands/07_split_all_volumes_by_plane_3_points/) (`M`) with three points such as these:

<figure markdown="span">
![tuto_3_split_3points](../images/tuto_3_split_3points.png){width="700"}
</figure>

The result is:
<figure markdown="span">
![tuto_3_split_3points_done](../images/tuto_3_split_3points_done.png){width="700"}
</figure>

Next, split the volume with a finite surface defined by four points:
<figure markdown="span">
![tuto_3_split_4points](../images/tuto_3_split_4points.png){width="700"}
</figure>

The result is:
<figure markdown="span">
![tuto_3_split_4points_done](../images/tuto_3_split_4points_done.png){width="700"}
</figure>


Remove the surface created inside the hole with [Remove surfaces](../../commands/16_remove_surface/) (`R`), double-click to finish the selection:

<figure markdown="span">
![tuto_3_remove_surface](../images/tuto_3_remove_surface.png){width="700"}
</figure>

Remove the associated curve with [Remove Curves](../../commands/15_remove_curve/) (`T`), double-click to finish the selection.

Project the points around the fillet:

<figure markdown="span">
![tuto_3_projection_points](../images/tuto_3_projection_points.png){width="700"}
</figure>

Then split the volumes with a point loop:
<figure markdown="span">
![tuto_3_split_point_loop](../images/tuto_3_split_point_loop.png){width="700"}
</figure>


Finally, project two points:

<figure markdown="span">
![tuto_3_projection_points_2](../images/tuto_3_projection_points_2.png){width="700"}
</figure>

Split the volumes with a finite surface defined by four points:
<figure markdown="span">
![tuto_3_split_finite_surface_4points](../images/tuto_3_split_finite_surface_4points.png){width="700"}
</figure>


The model is now fully meshable; all volumes appear green:
<figure markdown="span">
![tuto_3_meshable](../images/tuto_3_meshable.png){width="700"}
</figure>


## Mesh generation

Click **Mesh CAD** at the bottom of the left panel to generate a structured hexahedral mesh:

<figure markdown="span">
![tuto_3_mesh_cad](../images/tuto_3_mesh_cad.png){width="700"}
</figure>

By default, HexaMSH assigns five nodes to each edge.

To assign `n` nodes to narrow edges, use [Set number of nodes on all edges](../../commands/18_set_number_of_nodes_on_all_edges/). Enter the number, select the edges, then double-click to finish the selection.

You only need to select one edge. HexaMSH automatically applies the same number of nodes to the opposite edges, which appear green. The mesh updates immediately:

<figure markdown="span">
![tuto_3_new_mesh](../images/tuto_3_new_mesh.png){width="700"}
</figure>

Once the node counts are correct, close the Gmsh window. HexaMSH writes the result to a `.msh` file.




