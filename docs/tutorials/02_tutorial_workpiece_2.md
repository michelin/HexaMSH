---
title: Tutorial 2 - Workpiece 2
---


## Goal

The goal of this tutorial is to partition `workpiece2` into meshable blocks and generate a structured hexahedral mesh.

You will use HexaMSH to partition the CAD model and generate the mesh.


## Before you begin

Download the CAD file [here](https://gitlab.michelin.com/dord/simulation/cadmesh/hexamsh/-/blob/main/hexamsh/tests/workpiece2/workpiece2.stp?ref_type=heads).

Open it from a prompt in a Python environment that contains HexaMSH:

```console
hexamsh workpiece2.stp
```

Gmsh opens with the CAD model:

<figure markdown="span">
![tuto_2_intro](../images/tuto_2_intro.png){width="700"}
</figure>

The aim is to partition the CAD model into meshable sub-volumes:

<figure markdown="span">
![tuto_2_intro_end](../images/tuto_2_intro_end.png){width="500"}
</figure>

## CAD partitioning

There are several ways to obtain this partitioning. This tutorial presents one possible workflow.

### Create the first blocks

Use [Split a volume by a point loop](../../commands/10_split_volume_by_point_loop/) (`L`).

Select the points that define the loop, then double-click to finish the selection:

<figure markdown="span">
![tuto_2_split_point_loop_1](../images/tuto_2_split_point_loop_1.png){width="700"}
</figure>

The operation splits the geometry and creates a new surface:

<figure markdown="span">
![tuto_2_split_point_loop_1_done](../images/tuto_2_split_point_loop_1_done.png){width="700"}
</figure>

Repeat the same command on the next four points. This creates the first meshable block, shown in green:

<figure markdown="span">
![tuto_2_split_point_loop_2](../images/tuto_2_split_point_loop_2.png){width="700"}
</figure>

Use [Add a volume between two surfaces](../../commands/06_add_a_volume_between_two_surfaces/) (`D`). Select the lower surface first, then the upper surface:

<figure markdown="span">
![tuto_2_add_volume_1](../images/tuto_2_add_volume_1.png){width="700"}
</figure>

The command creates a new volume between the selected surfaces:

<figure markdown="span">
![tuto_2_add_volume_1_done](../images/tuto_2_add_volume_1_done.png){width="700"}
</figure>

!!! note "How is the volume created?"
    Three connecting surfaces already exist between the selected volumes. HexaMSH only needs to create the remaining surface, which produces a new sub-volume.

Repeat the command on the next two surfaces:

<figure markdown="span">
![tuto_2_add_volume_2](../images/tuto_2_add_volume_2.png){width="700"}
</figure>

This creates another volume between the selected surfaces:

<figure markdown="span">
![tuto_2_add_volume_2_done](../images/tuto_2_add_volume_2_done.png){width="700"}
</figure>

Separate the CAD with `Split a volume by a point loop`, selecting the four points shown below:


<figure markdown="span">
![tuto_2_split_point_loop_3](../images/tuto_2_split_point_loop_3.png){width="700"}
</figure>

The operation splits the geometry and creates a new surface:

<figure markdown="span">
![tuto_2_split_point_loop_3_done](../images/tuto_2_split_point_loop_3_done.png){width="700"}
</figure>


Repeat the operation on the upper points. First create two new points with [Project a point on a curve](../../commands/01_project_point_on_curve/) (`P`):

<figure markdown="span">
![tuto_2_click_projection_point](../images/tuto_2_click_projection_point.png){width="700"}
</figure>

Then project the second point:

<figure markdown="span">
![tuto_2_click_projection_point_2](../images/tuto_2_click_projection_point_2.png){width="700"}
</figure>

Finally, split the volume with a point loop:


<figure markdown="span">
![tuto_2_split_point_loop_4](../images/tuto_2_split_point_loop_4.png){width="700"}
</figure>

The operation splits the geometry and creates a new surface:

<figure markdown="span">
![tuto_2_split_point_loop_4_done](../images/tuto_2_split_point_loop_4_done.png){width="700"}
</figure>

Project the point onto the curve shown below:


<figure markdown="span">
![tuto_2_click_projection_point_3](../images/tuto_2_click_projection_point_3.png){width="700"}
</figure>

Now split the CAD into two parts with [Split all volumes by a plane (3 points)](../../commands/07_split_all_volumes_by_plane_3_points/) (`M`). Select three points:

<figure markdown="span">
![tuto_2_split_3_points](../images/tuto_2_split_3_points.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_2_split_3_points_done](../images/tuto_2_split_3_points_done.png){width="700"}
</figure>

Add a new volume with [Add a volume between two surfaces](../../commands/06_add_a_volume_between_two_surfaces/):

<figure markdown="span">
![tuto_2_add_volume_3](../images/tuto_2_add_volume_3.png){width="700"}
</figure>

The command directly creates three new meshable sub-volumes:

<figure markdown="span">
![tuto_2_add_volume_3_done](../images/tuto_2_add_volume_3_done.png){width="700"}
</figure>


Repeat the same command three times to create the remaining volumes:

<figure markdown="span">
![tuto_2_add_volume_4](../images/tuto_2_add_volume_4.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_2_add_volume_4_done](../images/tuto_2_add_volume_4_done.png){width="700"}
</figure>


Use [Merge two surfaces](../../commands/14_merge_two_surfaces/) (`V`) to simplify the CAD:

<figure markdown="span">
![tuto_2_merge_2_surfaces](../images/tuto_2_merge_2_surfaces.png){width="700"}
</figure>

Create a new volume in two steps:

1. Project points onto curves:

<figure markdown="span">
![tuto_2_click_projection_point_4](../images/tuto_2_click_projection_point_4.png){width="700"}
</figure>

2. Split the volume with a point loop:

<figure markdown="span">
![tuto_2_split_4_points_done](../images/tuto_2_split_4_points_done.png){width="700"}
</figure>

The last operation creates a wedge, which cannot be meshed with the transfinite methods.

Use [Split a wedge volume](../../commands/12_split_a_wedge_volume/) (`I`) and select the two triangular faces:

<figure markdown="span">
![tuto_2_split_wedge](../images/tuto_2_split_wedge.png){width="700"}
</figure>

This generates meshable sub-volumes inside the wedge:


<figure markdown="span">
![tuto_2_split_wedge_done](../images/tuto_2_split_wedge_done.png){width="700"}
</figure>

Add a volume between the two surfaces shown below:

<figure markdown="span">
![tuto_2_add_volume_5](../images/tuto_2_add_volume_5.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_2_add_volume_5_done](../images/tuto_2_add_volume_5_done.png){width="700"}
</figure>

Finally, use the same feature to split the remaining orange volume in that region:

<figure markdown="span">
![tuto_2_add_volume_6](../images/tuto_2_add_volume_6.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_2_add_volume_6_done](../images/tuto_2_add_volume_6_done.png){width="700"}
</figure>

Propagate the four surfaces vertically down to the CAD ground:

<figure markdown="span">
![tuto_2_add_volume_7](../images/tuto_2_add_volume_7.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_2_add_volume_7_done](../images/tuto_2_add_volume_7_done.png){width="700"}
</figure>

!!! tip "Play with views and geometry display"
    At any time, we can hide/show the green and orange volumes using the view options in the left pannel:
    <figure markdown="span">
    ![view_pannel](../images/view_pannel.png){width="200"}
    </figure>

    We can also use the Gmsh options to hide/show surfaces (`alt + S`), curves  (`alt + L`) and points  (`alt + P`) for a better visibility. 


### Partition the other side

Repeat the same strategy for the matching shape on the other side of the CAD model:

<figure markdown="span">
![tuto_2_other_part](../images/tuto_2_other_part.png){width="700"}
</figure>

Follow the same sequence:

1. Split vertically to create a wedge:

<figure markdown="span">
![tuto_2_other_part_1](../images/tuto_2_other_part_1.png){width="700"}
</figure>

2. Split the wedge:

<figure markdown="span">
![tuto_2_other_part_2](../images/tuto_2_other_part_2.png){width="700"}
</figure>

3. Add volumes to create meshable blocks.

!!! warning "A projection can create an unwanted split"
    Projecting points can sometimes create unwanted points when geometries intersect:

    <figure markdown="span">
    ![tuto_2_other_part_2_warning](../images/tuto_2_other_part_2_warning.png){width="700"}
    </figure>

    Instead, use [Add a point on a curve](../../commands/03_add_a_point_on_curve/). Adjust the ratio, select the curves to split, and double-click to finish the selection. Adjust the ratio again if needed, then press `E` to validate the split.

    <figure markdown="span">
    ![tuto_2_other_part_2_split_curve](../images/tuto_2_other_part_2_split_curve.png){width="700"}
    </figure>

    Then split the volume with a point loop. This produces a cleaner, meshable split:

    <figure markdown="span">
    ![tuto_2_other_part_2_split_point_loop](../images/tuto_2_other_part_2_split_point_loop.png){width="700"}
    </figure>


!!! tip "Undo an unexpected operation"
    Use [Back to previous CAD](../../commands/00_back_to_previous_cad/) to revert an operation. The keyboard shortcut is `Ctrl + Z`.

The partitioned model should now look like this:

<figure markdown="span">
![tuto_2_other_part_3](../images/tuto_2_other_part_3.png){width="700"}
</figure>


### Partition around the hole

Split the CAD around the hole:

<figure markdown="span">
![tuto_2_split_propostion](../images/tuto_2_split_propostion.png){width="700"}
</figure>

Use the following commands in sequence to create this partition:

1. [Project a point on a curve](../../commands/01_project_point_on_curve/).
2. [Split a volume by a point loop](../../commands/10_split_volume_by_point_loop/).
3. [Add a volume between two surfaces](../../commands/06_add_a_volume_between_two_surfaces/).

<figure markdown="span">
![tuto_2_split_5_points_done](../images/tuto_2_split_5_points_done.png){width="700"}
</figure>


!!! tip "Combine features to complete the partitioning"
    HexaMSH often requires a combination of features. For the result above, use [Add a volume between two surfaces](../../commands/06_add_a_volume_between_two_surfaces/) for most operations. For the final split, use [Add a point on a curve](../../commands/03_add_a_point_on_curve/):

    <figure markdown="span">
    ![tuto_2_other_part_2_split_curve_2](../images/tuto_2_other_part_2_split_curve_2.png){width="700"}
    </figure>

    Then split the volume with a point loop.


Project the point onto the curve shown below:

<figure markdown="span">
![tuto_2_click_projection_point_5](../images/tuto_2_click_projection_point_5.png){width="700"}
</figure>

Split the CAD with an infinite plane by selecting three points:

<figure markdown="span">
![tuto_2_split_3_points_2](../images/tuto_2_split_3_points_2.png){width="700"}
</figure>

### Propagate the pocket

Propagate the pocket down to the ground:

<figure markdown="span">
![tuto_2_pocket_propagation](../images/tuto_2_pocket_propagation.png){width="700"}
</figure>

Use [Project surface onto surface](../../commands/02_project_surface_on_surface/) (`S`) to generate a new volume. Select the upper surface first, then the ground surface:

<figure markdown="span">
![tuto_2_pocket_propagation_done](../images/tuto_2_pocket_propagation_done.png){width="700"}
</figure>


Split the CAD by projecting points onto curves and then using [Split a volume by a point loop](../../commands/10_split_volume_by_point_loop/):

<figure markdown="span">
![tuto_2_split_propostion_2](../images/tuto_2_split_propostion_2.png){width="700"}
</figure>

The result is:

<figure markdown="span">
![tuto_2_split_propostion_2_done](../images/tuto_2_split_propostion_2_done.png){width="700"}
</figure>


!!! warning "A point loop can contain more than four points"
    Some point loops contain five points here. Select all five points to split the CAD correctly.

Create the next split to force surfaces with four curves:

<figure markdown="span">
![tuto_2_split_propostion_3](../images/tuto_2_split_propostion_3.png){width="700"}
</figure>

Partition this part:
<figure markdown="span">
![tuto_2_split_propostion_4](../images/tuto_2_split_propostion_4.png){width="700"}
</figure>

The result is:
<figure markdown="span">
![tuto_2_split_propostion_4_done](../images/tuto_2_split_propostion_4_done.png){width="700"}
</figure>


Split the volume at the location shown below:
<figure markdown="span">
![tuto_2_split_propostion_5](../images/tuto_2_split_propostion_5.png){width="700"}
</figure>

The result is:
<figure markdown="span">
![tuto_2_split_propostion_5_done](../images/tuto_2_split_propostion_5_done.png){width="700"}
</figure>


Split the next volume at the location shown below:
<figure markdown="span">
![tuto_2_split_propostion_6](../images/tuto_2_split_propostion_6.png){width="700"}
</figure>

The result is:
<figure markdown="span">
![tuto_2_split_propostion_6_done](../images/tuto_2_split_propostion_6_done.png){width="700"}
</figure>



Finally, split the full CAD with an infinite plane defined by three points:

<figure markdown="span">
![tuto_2_split_3_points_3](../images/tuto_2_split_3_points_3.png){width="700"}
</figure>

Split the pocket at the location shown below:
<figure markdown="span">
![tuto_2_split_propostion_7](../images/tuto_2_split_propostion_7.png){width="700"}
</figure>

The result is:
<figure markdown="span">
![tuto_2_split_propostion_7_done](../images/tuto_2_split_propostion_7_done.png){width="700"}
</figure>

Remove the orange surface created by the infinite-plane split with [Remove surfaces](../../commands/16_remove_surface/) (`R`), double-click to finish the selection:

<figure markdown="span">
![tuto_2_split_remove_surface](../images/tuto_2_split_remove_surface.png){width="700"}
</figure>

!!! tip "Change the surface view"
    Press `Alt + T` to switch to the `solid` surface view:
    <figure markdown="span">
    ![tuto_2_solid_surface](../images/tuto_2_solid_surface.png){width="700"}
    </figure>
    The `wireframe` view is more suitable for editing the CAD. Press `Alt + T` again to return to it.


The model is now fully meshable: all volumes appear green.


## Mesh generation

Click **Mesh CAD** at the bottom of the left panel to generate a structured hexahedral mesh:

<figure markdown="span">
![tuto_2_mesh_cad](../images/tuto_2_mesh_cad.png){width="700"}
</figure>

By default, five nodes are assigned to every edge. To use three nodes on selected edges, use [Set number of nodes on edges](../../commands/17_set_number_of_nodes_on_edges/):

<figure markdown="span">
![tuto_2_set_3_nodes](../images/tuto_2_set_3_nodes.png){width="700"}
</figure>


To assign `n` nodes to a group of wider edges, use [Set number of nodes on all edges](../../commands/18_set_number_of_nodes_on_all_edges/). Set the number, select the edges, and double-click to finish the selection.

You only need to select one edge. HexaMSH automatically applies the same number of nodes to the opposite edges, which appear green. The mesh updates immediately:

<figure markdown="span">
![tuto_2_new_mesh](../images/tuto_2_new_mesh.png){width="700"}
</figure>

Once the node counts are correct, close the Gmsh window. HexaMSH writes the result to a `.msh` file.




