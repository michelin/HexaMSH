---
title: Tutorial 1 - Workpiece 1
---


## Goal

The goal of this tutorial is to partition `workpiece1` into meshable blocks and generate a structured hexahedral mesh.

You will use HexaMSH to partition the CAD model and generate the mesh.


## Before you begin

Download the CAD file [here](https://gitlab.michelin.com/dord/simulation/cadmesh/hexamsh/-/blob/main/hexamsh/tests/workpiece1/workpiece1.brep?ref_type=heads).

Open it from a prompt in a Python environment that contains HexaMSH:

```console
hexamsh workpiece1.brep
```

Gmsh opens with the CAD model:

<figure markdown="span">
![tuto_1_intro](../images/tuto_1_intro.png){width="800"}
</figure>

The aim is to partition the CAD model into meshable sub-volumes:

<figure markdown="span">
![tuto_1_intro_end](../images/tuto_1_intro_end.png){width="500"}
</figure>


## CAD partitioning

There are several ways to obtain this partitioning. This tutorial presents one possible workflow.

### Create the first blocks

Use [Project a point on a curve](../../commands/01_project_point_on_curve/) (`P`). Select the point to project, then select the curves to split. Double-click to finish the selection. Right-click to remove an entity from the selections.

<figure markdown="span">
![tuto_1_click_projection_point](../images/tuto_1_click_projection_point.png){width="800"}
</figure>

The point is projected onto the two curves shown below:

<figure markdown="span">
![tuto_1_proj_1](../images/tuto_1_projection_point_1.png){width="400"}
</figure>

The operation creates two new points and splits the curves:

<figure markdown="span">
![tuto_1_projected_point_1](../images/tuto_1_projected_point_1.png){width="400"}
</figure>

!!! tips "Entities selection and unselection"
    Right-click a selected entity to remove it from the selection. Double-click with the left mouse button to finish selecting.


Next, use [Split a volume by a point loop](../../commands/10_split_volume_by_point_loop/) (`L`).

Select the points that define a loop. The direction does not matter, but the points must form a closed loop. Double-click to finish the selection. Right-click to remove an entity from the selections.

<figure markdown="span">
![tuto_1_split_point_loop_selection](../images/tuto_1_split_point_loop_selection.png){width="400"}
</figure>

This creates the first meshable block, shown in green:

<figure markdown="span">
![tuto_1_first_block](../images/tuto_1_first_block.png){width="400"}
</figure>

The goal is for every block to be meshable, so all blocks should appear green.

Repeat the same feature to create a second block:

<figure markdown="span">
![tuto_1_split_2](../images/tuto_1_split_2.png){width="400"}
</figure>

This creates a second meshable block:

<figure markdown="span">
![tuto_1_split_2_done](../images/tuto_1_split_2_done.png){width="400"}
</figure>


Project points onto the vertical edges shown below:

<figure markdown="span">
![tuto_1_projection_point_2](../images/tuto_1_projection_point_2.png){width="400"}
</figure>

The result is:

<figure markdown="span">
![tuto_1_projection_point_2_done](../images/tuto_1_projection_point_2_done.png){width="400"}
</figure>

Then split the CAD with a point loop:

<figure markdown="span">
![tuto_1_block_3](../images/tuto_1_block_3.png){width="400"}
</figure>

### Split the upper section

Split the upper section into two parts with [Split all volumes by a plane (3 points)](../../commands/07_split_all_volumes_by_plane_3_points/) (`M`). Select three points:

<figure markdown="span">
![tuto_1_3_points_split](../images/tuto_1_3_points_split.png){width="400"}
</figure>

The CAD is split by an infinite plane:

<figure markdown="span">
![tuto_1_3_points_split_done](../images/tuto_1_3_points_split_done.png){width="400"}
</figure>

!!! warning "Infinite-plane split"
    This operation works because the fourth point around the cylindrical hole is aligned with the other three points. Otherwise, the split would create a new point.


Project an upper point onto the lower edge to create the partition around the fillet:

<figure markdown="span">
![tuto_1_projection_point_3](../images/tuto_1_projection_point_3.png){width="400"}
</figure>

This creates three points that define a new infinite plane:

<figure markdown="span">
![tuto_1_projection_point_3_done](../images/tuto_1_projection_point_3_done.png){width="400"}
</figure>

Define the infinite plane that splits the CAD:

<figure markdown="span">
![tuto_1_3_points_split_2](../images/tuto_1_3_points_split_2.png){width="400"}
</figure>

The new partition creates additional blocks:

<figure markdown="span">
![tuto_1_3_points_split_2_done](../images/tuto_1_3_points_split_2_done.png){width="400"}
</figure>

!!! tip "Play with views and geometry display"
    At any time, we can hide/show the green and orange volumes using the view options in the left pannel:
    <figure markdown="span">
    ![view_pannel](../images/view_pannel.png){width="200"}
    </figure>

    We can also use the Gmsh options to hide/show surfaces (`alt + S`), curves  (`alt + L`) and points  (`alt + P`) for a better visibility. 

### Split around the cylinder

Finally, split the CAD around the cylinder:

<figure markdown="span">
![tuto_1_split_around_cylinder](../images/tuto_1_split_around_cylinder.png){width="400"}
</figure>

Project the corresponding points onto the cylinder edges. There are eight points to project. Then split the volumes with four point loops, each containing four points.

First block:
<figure markdown="span">
![tuto_1_final_blocks_1](../images/tuto_1_final_blocks_1.png){width="400"}
</figure>

Second block:
<figure markdown="span">
![tuto_1_final_blocks_2](../images/tuto_1_final_blocks_2.png){width="400"}
</figure>

Third block:
<figure markdown="span">
![tuto_1_final_blocks_3](../images/tuto_1_final_blocks_3.png){width="400"}
</figure>

Fourth block:
<figure markdown="span">
![tuto_1_final_blocks_4](../images/tuto_1_final_blocks_4.png){width="400"}
</figure>


The model is now fully meshable: all volumes appear green.


## Mesh generation

Click **Mesh CAD** at the bottom of the left panel:

<figure markdown="span">
![tuto_1_mesh_cad](../images/tuto_1_mesh_cad.png){width="800"}
</figure>

HexaMSH generates a transfinite mesh on the partitioned geometry:

<figure markdown="span">
![tuto_1_meshed](../images/tuto_1_meshed.png){width="400"}
</figure>

By default, five nodes are assigned to every edge. To use six nodes on selected edges, use [Set number of nodes on edges](../../commands/17_set_number_of_nodes_on_edges/):

<figure markdown="span">
![tuto_1_set_6_nodes](../images/tuto_1_set_6_nodes.png){width="400"}
</figure>

To assign three nodes to a group of narrow edges, use [Set number of nodes on all edges](../../commands/18_set_number_of_nodes_on_all_edges/). Set the number to `3`, select the edges, and double-click to finish the selection. Right-click to remove an entity from the selections.


<figure markdown="span">
![tuto_1_set_3_nodes](../images/tuto_1_set_3_nodes.png){width="400"}
</figure>

You only need to select one edge. HexaMSH automatically applies the same number of nodes to the opposite edges, which appear green. The mesh updates immediately:

<figure markdown="span">
![tuto_1_new_mesh](../images/tuto_1_new_mesh.png){width="400"}
</figure>

Once the node counts are correct, close the Gmsh window. HexaMSH writes the result to a `.msh` file.




