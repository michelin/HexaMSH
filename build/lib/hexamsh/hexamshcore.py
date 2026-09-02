import math
import os
import shutil
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import gmsh
import numpy as np

# Cache frequently used Gmsh modules.
if not gmsh.isInitialized():
    gmsh.initialize()

gmodel = gmsh.model
gmesh = gmodel.mesh
goption = gmsh.option
gocc = gmodel.occ

# Hex-oriented meshing defaults.
goption.setNumber("General.NumThreads", 0)
goption.setNumber("General.Verbosity", 0)

goption.setNumber("Geometry.OCCParallel", 1)
goption.setNumber("Geometry.OCCAutoFix", 0)
goption.setNumber("Geometry.Tolerance", 1e-6)

goption.setNumber("Mesh.RecombineAll", 1)
goption.setNumber("Mesh.MeshOnlyVisible", 1)

goption.setString("Geometry.DoubleClickedPointCommand", "")
goption.setString("Geometry.DoubleClickedCurveCommand", "")
goption.setString("Geometry.DoubleClickedSurfaceCommand", "")


def addPointOnCurve(curve, ratio=0.5):
    """Add a point at a specified ratio along a curve.

    Ratio is measured along the preferred orientation (+X, then +Y, then +Z).
    """
    start = time.time()
    new_point = createPointOnCurve(curve, ratio=ratio)
    surfaces = [s for s in getCommonSurfacesFromCurve(curve) if s is not None]
    if len(surfaces) > 0:
        fragmentEntities([(2, s) for s in surfaces], [(0, new_point)])
    else:
        fragmentEntities([(1, curve)], [(0, new_point)])
    end = time.time()
    print(f"Info    : Added point in {end - start:.2f} seconds")
    return new_point


def addSurfaceByCurveLoop(cl):
    """Create a surface from a curve loop."""
    start = time.time()
    loop = createLoopFromCurves(cl)
    if loop is None:
        print("Warning : Failed to create curve loop for surface")
        return False
    curve_loop = gocc.addCurveLoop(loop)
    if curve_loop == -1:
        print("Warning : Failed to create curve loop for surface")
        return False
    surf = gocc.addSurfaceFilling(wireTag=curve_loop)
    gocc.synchronize()
    end = time.time()
    print(f"Info    : Added surface in {end - start:.2f} seconds")
    return surf


def addSurfaceByPointLoop(pl):
    """Create a surface from a curve loop."""
    start = time.time()
    loop = createLoopFromPoints(pl)
    if not loop:
        print("Warning : Failed to create curve loop for surface")
        return False
    curve_loop = gocc.addCurveLoop(loop)
    if curve_loop == -1:
        print("Warning : Failed to create curve loop for surface")
        return False
    surf = gocc.addSurfaceFilling(wireTag=curve_loop)
    gocc.synchronize()
    end = time.time()
    print(f"Info    : Added surface in {end - start:.2f} seconds")
    return surf


def addVolumeBetweenTwoSurfaces(s1, s2):
    """Add a volume between two surfaces by projecting points from s1 onto s2 and creating connecting curves."""

    start = time.time()
    ordered_points = order_points_into_loop(getPointsFromSurface(s1))

    xmin, ymin, zmin, xmax, ymax, zmax = gmodel.getBoundingBox(2, s2)
    bbox_size = np.linalg.norm(
        np.array([xmax, ymax, zmax], dtype=float)
        - np.array([xmin, ymin, zmin], dtype=float)
    )
    tol = 0.001 * bbox_size
    linking_surfaces = _find_linking_surfaces(s1, s2)
    linking_surface_points, points_on_linking_surfaces = (
        _build_linking_surface_point_sets(linking_surfaces)
    )

    point_tree, existing_point_tags, existing_coords_array = (
        _build_existing_points_tree(s2)
    )

    gocc.synchronize()

    # Point projection on s2 surface
    map_points = {}
    new_points = []
    point_fragments = set()
    curve_fragments = set()
    for point in ordered_points:
        if point in points_on_linking_surfaces:
            new_p, point_tree, existing_coords_array = (
                _project_point_from_linking_surface(
                    point,
                    s2,
                    linking_surfaces,
                    linking_surface_points,
                    point_tree,
                    existing_point_tags,
                    existing_coords_array,
                    tol,
                    point_fragments,
                    curve_fragments,
                )
            )
        else:
            new_p, point_tree, existing_coords_array = _project_point_on_target_surface(
                point,
                s2,
                point_tree,
                existing_point_tags,
                existing_coords_array,
                tol,
            )

        if not new_p:
            print(f"Error   : Failed to create projected point for {point}")
            continue

        new_points.append(new_p)
        map_points[new_p] = point

    gocc.synchronize()

    _fragment_surfaces_from_curve_and_point_fragments(curve_fragments, point_fragments)

    if new_points:
        # Curve creation between projected points + common surface
        _create_curves_between_projected_points(new_points, map_points, s2)
    else:
        print("Warning : No new points were created on the target surface")
    _create_side_surfaces_from_mapped_points(map_points)
    gocc.synchronize()
    end = time.time()
    print(f"Info    : Added volume between surfaces in {end - start:.2f} seconds")


def appendToScript(op, filename="replay.py"):
    """Append an operation block to replay script, preserving finalizer."""
    filepath = _script_path(filename=filename)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Temporarily remove last finalize to append before it.
    if lines and "gmsh.finalize()" in lines[-1]:
        lines = lines[:-1]

    block = [f"# --- {op['name']} ---\n", op["content"]]
    if not op["content"].endswith("\n"):
        block.append("\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
        f.writelines(block)
        f.write("gmsh.finalize()\n")


def checkIsolatedEntities():
    """Check for isolated points with less than 2 adjacent curves,
    which may cause fragmentation issues.
    """

    for tag, p in gocc.getEntities(0):
        curves, _ = gmodel.getAdjacencies(tag, p)
        if len(curves) < 2:
            print(
                f"Warning : Point {p} is isolated with only {len(curves)} adjacent curve(s)."
            )
            return True
    return False


def cleanAfterFragmentation():
    """Remove orphan entities created by fragmentation.

    - Remove curves not attached to any existing surface.
    - Remove points not attached to any existing curve.
    """
    cleanOrphanCurves()
    cleanOrphanPoints()
    gocc.synchronize()


def cleanOrphanCurves():
    """Remove curves that are not used by any remaining surface."""
    curves_to_keep = set()
    for _, stag in gocc.getEntities(2):
        _, curves = gmodel.getAdjacencies(2, stag)
        curves_to_keep.update(int(c) for c in curves)

    curve_list = gocc.getEntities(1)
    curves_to_remove = [
        (1, ctag) for _, ctag in curve_list if int(ctag) not in curves_to_keep
    ]
    if curves_to_remove:
        gocc.remove(curves_to_remove, recursive=True)
    return len(curves_to_remove)


def cleanOrphanPoints():
    """Remove points that are not used by any remaining curve."""
    points_to_keep = set()
    for _, ctag in gmodel.getEntities(1):
        _, points = gmodel.getAdjacencies(1, ctag)
        points_to_keep.update(int(p) for p in points)

    occ_points = {int(ptag) for _, ptag in gocc.getEntities(0)}
    model_points = {int(ptag) for _, ptag in gmodel.getEntities(0)}
    orphan_points = model_points - points_to_keep

    occ_points_to_remove = [(0, ptag) for ptag in sorted(orphan_points & occ_points)]
    model_only_points_to_remove = [
        (0, ptag) for ptag in sorted(orphan_points - occ_points)
    ]

    if occ_points_to_remove:
        gocc.remove(occ_points_to_remove, recursive=True)

    if model_only_points_to_remove:
        gmodel.removeEntities(model_only_points_to_remove, recursive=True)

    return len(occ_points_to_remove) + len(model_only_points_to_remove)


def cleanOrphanSurfaces():
    """Remove surfaces that are not used by any volume."""
    surfaces_to_keep = set()
    for _, vtag in gocc.getEntities(3):
        _, surfaces = gmodel.getAdjacencies(3, vtag)
        surfaces_to_keep.update(int(s) for s in surfaces)

    surface_list = gocc.getEntities(2)
    surfaces_to_remove = [
        (2, stag) for _, stag in surface_list if int(stag) not in surfaces_to_keep
    ]
    if surfaces_to_remove:
        print(f"Info    : Removing {len(surfaces_to_remove)} orphan surfaces")
        gocc.remove(surfaces_to_remove, recursive=True)
        gocc.synchronize()


def computeExtrusionNormal(s1, s2):
    """Compute an extrusion normal direction from surface s1 to s2,
    using linking curves if they exist.
    """

    center = np.array(gocc.getCenterOfMass(2, s1), dtype=float)
    [x2, y2, z2], param = gmodel.getClosestPoint(2, s2, tuple(center))
    target = np.array([x2, y2, z2], dtype=float)

    distance = 2 * np.linalg.norm(target - center)

    _, s1_curves = gmodel.getAdjacencies(2, s1)
    _, s2_curves = gmodel.getAdjacencies(2, s2)
    points_on_s1 = getPointsFromSurface(s1)
    points_on_s2 = getPointsFromSurface(s2)

    extrusion_curves = getLinkingCurves(points_on_s1, points_on_s2)
    curves_to_be_split = set()
    normal = None
    if len(extrusion_curves) != 0:
        for c in extrusion_curves:
            ctype = gmodel.getType(1, c).lower()
            if ctype == "line":
                _, pts = gmodel.getAdjacencies(1, c)
                p1, p2 = int(pts[0]), int(pts[1])
                if p1 in points_on_s1:
                    normal_dir = np.array(
                        gmodel.getValue(0, p2, []), dtype=float
                    ) - np.array(gmodel.getValue(0, p1, []), dtype=float)
                else:
                    normal_dir = np.array(
                        gmodel.getValue(0, p1, []), dtype=float
                    ) - np.array(gmodel.getValue(0, p2, []), dtype=float)

                normal = normal_dir / np.linalg.norm(normal_dir) * distance
                break
    if normal is None:
        normal = np.array(gmodel.getNormal(s2, param), dtype=float) * distance

        # Check direction sense: verify normal points from s1 to s2
        s1_center = np.array(gocc.getCenterOfMass(2, s1), dtype=float)
        s2_center = np.array(gocc.getCenterOfMass(2, s2), dtype=float)
        direction_to_s2 = s2_center - s1_center

        # If normal points opposite direction, reverse it
        if np.dot(normal, direction_to_s2) < 0:
            normal = -normal
    return normal


def createCurve(
    p1, p2, pattern=None, support_surface=None, nb_interpolation_points=100
):
    """Create a splitting curve on a common surface between two points."""

    common_curve = getCommonCurveFromTwoPoints(p1, p2)
    if common_curve is not None:
        print(f"Info    : Found existing curve {common_curve} between points")
        return common_curve

    if not support_surface:
        surfaces = getCommonSurfacesFromTwoPoints(p1, p2)
    else:
        surfaces = [support_surface]

    if not surfaces:
        curve = gocc.addLine(p1, p2)
        return curve

    curve = None
    for surface in surfaces:
        stype = gmodel.getType(2, surface)

        if stype == "Plane" and not pattern:
            # For planar surfaces, a straight line is sufficient.
            curve = gocc.addLine(p1, p2)
        else:
            x1, y1, z1 = gmodel.getValue(0, p1, [])
            x2, y2, z2 = gmodel.getValue(0, p2, [])

            interp_points = []
            if pattern is None:
                # Original linear interpolation
                for i in range(1, nb_interpolation_points + 1):
                    t = i / (nb_interpolation_points + 1)
                    xi = x1 + (x2 - x1) * t
                    yi = y1 + (y2 - y1) * t
                    zi = z1 + (z2 - z1) * t
                    interp_points.append((xi, yi, zi))
            else:
                # Add interpolation points following the pattern curve's shape.
                # Start from p1, go to p2, and sample points in between following the pattern curvature.
                # Step by step:
                # Sample the pattern curve
                # compute the distance between p1 and the pattern curve's start point, and between p2 and the pattern curve's end point.
                # offset the sampling in between p1 and p2 according to the pattern curve's shape.
                try:
                    bounds = gmodel.getParametrizationBounds(1, pattern)
                    tmin, tmax = bounds[0][0], bounds[1][0]

                    # Pattern end points for both orientations.
                    ps = np.array(gmodel.getValue(1, pattern, [tmin]), dtype=float)
                    pe = np.array(gmodel.getValue(1, pattern, [tmax]), dtype=float)
                    p1_xyz = np.array([x1, y1, z1], dtype=float)
                    p2_xyz = np.array([x2, y2, z2], dtype=float)

                    # Choose orientation that best matches (p1 -> start, p2 -> end).
                    direct_err = np.linalg.norm(p1_xyz - ps) + np.linalg.norm(
                        p2_xyz - pe
                    )
                    reverse_err = np.linalg.norm(p1_xyz - pe) + np.linalg.norm(
                        p2_xyz - ps
                    )
                    forward = direct_err <= reverse_err

                    if forward:
                        pstart, pend = ps, pe
                    else:
                        pstart, pend = pe, ps

                    # Endpoint offsets from pattern to target segment ends.
                    d_start = p1_xyz - pstart
                    d_end = p2_xyz - pend

                    for i in range(1, nb_interpolation_points + 1):
                        alpha = i / (nb_interpolation_points + 1)
                        t = (
                            tmin + alpha * (tmax - tmin)
                            if forward
                            else tmax - alpha * (tmax - tmin)
                        )

                        ppat = np.array(gmodel.getValue(1, pattern, [t]), dtype=float)

                        # Blend endpoint offsets along the path so the mapped curve
                        # follows the pattern curvature while matching p1/p2.
                        pnew = ppat + (1.0 - alpha) * d_start + alpha * d_end
                        interp_points.append(
                            (float(pnew[0]), float(pnew[1]), float(pnew[2]))
                        )
                except (RuntimeError, ValueError, TypeError):
                    # Fallback to linear interpolation if pattern sampling fails.
                    for i in range(1, nb_interpolation_points + 1):
                        t = i / (nb_interpolation_points + 1)
                        xi = x1 + (x2 - x1) * t
                        yi = y1 + (y2 - y1) * t
                        zi = z1 + (z2 - z1) * t
                        interp_points.append((xi, yi, zi))

            xi, yi, zi = interp_points[int(len(interp_points) / 2)]

            [xproj, yproj, zproj], _ = gmodel.getClosestPoint(2, surface, [xi, yi, zi])
            inside = gmodel.isInside(2, surface, [xproj, yproj, zproj])
            if not inside:
                # Interpolation leaves surface, try next surface if available.
                continue
            interior_tags = []
            for xi, yi, zi in interp_points:

                [xproj, yproj, zproj], _ = gmodel.getClosestPoint(
                    2, surface, [xi, yi, zi]
                )

                p = gocc.addPoint(
                    xproj,
                    yproj,
                    zproj,
                )
                interior_tags.append(p)
            curve = gocc.addSpline([p1] + interior_tags + [p2])
            gocc.remove([(0, t) for t in interior_tags])
            break

    return curve


def createLoopFromCurves(curve_selection):
    """Orient a list of connected curves into a consistent loop sign convention."""
    points = []
    for curve in curve_selection:
        _, p = gmodel.getAdjacencies(1, curve)
        points.append(p)

    loop = [curve_selection[0]]
    for i in range(1, len(curve_selection)):
        if points[i - 1][1] == points[i][0]:
            loop.append(curve_selection[i])
        else:
            # Flip orientation if connection does not match.
            loop.append(-curve_selection[i])
            points[i] = points[i][::-1]
    return loop


def createLoopFromPoints(ps):
    """Create/ensure a closed loop of curves from an ordered point list."""
    new_curves = []
    for i in range(1, len(ps)):
        curve = getCommonCurveFromTwoPoints(ps[i - 1], ps[i])
        if curve is None:
            nc = createCurve(ps[i - 1], ps[i])
            if nc is None:
                print("Error   : Failed to create curve for loop")
                return False
            new_curves.append(nc)
    curve = getCommonCurveFromTwoPoints(ps[-1], ps[0])
    if curve is None:
        nc = createCurve(ps[-1], ps[0])
        if nc is None:
            print("Error   : Failed to create curve for loop")
            return False
        new_curves.append(nc)

    if new_curves:
        gocc.synchronize()

    loop = []
    for i in range(1, len(ps)):
        ccurve = getCommonCurveFromTwoPoints(ps[i - 1], ps[i])
        if ccurve is None:
            print("Error   : Failed to find curve for loop")
            return False
        loop.append(ccurve)
    ccurve = getCommonCurveFromTwoPoints(ps[-1], ps[0])
    if ccurve is None:
        print("Error   : Failed to find curve for loop")
        return False
    loop.append(ccurve)

    return loop


def createPointOnCurve(curve, ratio=0.5):
    """Crreate a point at a specified ratio along a curve.

    Ratio is measured along the preferred orientation (+X, then +Y, then +Z).
    """
    bounds = gmodel.getParametrizationBounds(1, curve)
    tmin, tmax = bounds[0][0], bounds[1][0]

    ratio = max(0.0, min(1.0, float(ratio)))

    # Determine preferred curve orientation from scalar products with X/Y/Z axes,
    # then infer sign (+/-) on the dominant axis.
    x0, y0, z0 = gmodel.getValue(1, curve, [tmin])
    x1, y1, z1 = gmodel.getValue(1, curve, [tmax])
    p0 = np.array([x0, y0, z0], dtype=float)
    p1 = np.array([x1, y1, z1], dtype=float)
    d = p1 - p0

    tol = 1e-12
    axes = np.eye(3, dtype=float)  # X, Y, Z
    scalar_products = axes @ d
    dominant_axis = int(np.argmax(np.abs(scalar_products)))
    dominant_value = scalar_products[dominant_axis]

    if abs(dominant_value) <= tol:
        forward = True
    else:
        forward = dominant_value > 0.0

    tr = ratio if forward else (1.0 - ratio)
    tmid = tmin + tr * (tmax - tmin)
    xmid, ymid, zmid = gmodel.getValue(1, curve, [tmid])
    new_point = gocc.addPoint(xmid, ymid, zmid)
    return new_point


def findMeshableGroups():
    start = time.time()
    gocc.synchronize()
    adj = {}
    for _, s in gocc.getEntities(2):
        _, curves = gmodel.getAdjacencies(2, s)
        if len(curves) == 4:
            adj[s] = frozenset(int(c) for c in curves)

    c2s = defaultdict(set)
    for s, curves in adj.items():
        for c in curves:
            c2s[c].add(s)

    nbrs = defaultdict(set)
    for ss in c2s.values():
        for s1 in ss:
            nbrs[s1] |= ss - {s1}

    # ── Détection des shells : opposée + ceinture ─────────────────────────────
    # Dans un hexaèdre :
    #   - s0 et s_opp ne partagent aucune courbe  → s_opp ∉ nbrs[s0]
    #   - les 4 faces de ceinture = nbrs[s0] ∩ nbrs[s_opp]
    surf_set = set(adj)
    shells = set()

    def _validate(group):
        cu = defaultdict(int)
        for s in group:
            for c in adj[s]:
                cu[c] += 1
        return (
            len(cu) == 12
            and all(v == 2 for v in cu.values())
            and all(len(nbrs[s] & group) == 4 for s in group)
        )

    for s0 in sorted(surf_set):
        non_nbrs = surf_set - nbrs[s0] - {s0}
        for s_opp in non_nbrs:
            if s_opp <= s0:
                continue  # ordre canonique → pas de doublons
            belt = nbrs[s0] & nbrs[s_opp]
            if len(belt) != 4:
                continue  # pas une paire opposée valide
            group = frozenset({s0, s_opp} | belt)
            if _validate(group):
                shells.add(group)

    # ── Classification ────────────────────────────────────────────────────────
    meshable_surfs = set(s for g in shells for s in g)
    meshable = [sorted(g) for g in sorted(shells, key=min)]
    non_meshable = [[s] for s in sorted(surf_set - meshable_surfs)]
    end = time.time()
    print(
        f"Info    : {len(meshable)} meshable, {len(non_meshable)} non-meshable "
        f"in {end-start:.2f}s"
    )
    return meshable


def fragmentEntities(entities, tools):
    """Fragment entities with a given OCC tool entity list."""
    if entities is None or tools is None:
        print("Warning : Fragmentation skipped due to missing entities or tools")
        return False
    entities = list(entities)
    tools = list(tools)

    def _is_valid_dim_tag(item):
        if item is None:
            return False
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            return False
        return item[0] is not None and item[1] is not None

    entities_clean = [e for e in entities if _is_valid_dim_tag(e)]
    tools_clean = [t for t in tools if _is_valid_dim_tag(t)]

    if not entities_clean or not tools_clean:
        print(
            "Warning : Fragmentation skipped because no valid entities or tools remain"
        )
        return False

    try:
        _, out_entities = gocc.fragment(entities_clean, tools_clean)
    except TypeError:
        print("Warning : Fragmentation failed due to invalid entities or tools")
        return False
    if out_entities == []:
        print("Warning : Fragmentation failed")
    gocc.synchronize()
    return out_entities


def fragmentVolumeByLoop(pl, cl, new_surface):
    """Return surfaces impacted by a loop of curves."""
    tools = []
    surfaceobject = []
    surface = getCommonSurfaceFromCurvesList(cl)
    if surface:
        surfaceobject.append((2, surface))

    if (
        len(pl) < 7
    ):  # Simple patterns, we can check adjacencies to find impacted surfaces more precisely.
        for curve in cl:
            surfaces, points = gmodel.getAdjacencies(1, curve)
            if len(surfaces) != 0:
                continue
            tools.append((1, curve))
            surfaces = getCommonSurfacesFromTwoPoints(points[0], points[1])
            for surface in surfaces:
                surfaceobject.append((2, surface))
        if len(pl) == 6:  # Intermediate patterns
            opposite_curves = set()
            p1, p2, p3, p4, p5, p6 = pl

            s1 = getCommonSurfacesFromTwoPoints(p1, p4)
            s2 = getCommonSurfacesFromTwoPoints(p2, p5)
            s3 = getCommonSurfacesFromTwoPoints(p3, p6)
            if s1:
                for s in s1:
                    surfaceobject.append((2, s))
            if s2:
                for s in s2:
                    surfaceobject.append((2, s))
            if s3:
                for s in s3:
                    surfaceobject.append((2, s))
            if s1 or s2 or s3:
                tools.append((2, new_surface))
    else:  # General fallback: if loop is large, assume all surfaces could be impacted
        surfaceobject = getCandidateSurfaces(new_surface)
        tools = [(2, new_surface)]
    si = time.time()
    fragmentEntities(surfaceobject, tools)
    ei = time.time()
    print(f"Info    : Fragmentation took {ei - si:.2f}s")


def findCADFile():
    """Check for a CAD file in the current working directory and returns an error if multiple files found."""
    cwd = Path.cwd()
    cad_extensions = [".step", ".stp", ".iges", ".igs", ".brep"]
    cad_files = [f for f in cwd.iterdir() if f.suffix.lower() in cad_extensions]
    if len(cad_files) != 1:
        if len(cad_files) == 0:
            print("Error   : No CAD file found in the current working directory.")
        else:
            print(
                "Error   : Multiple CAD files found in the current working directory."
            )
        return None
    else:
        return cad_files[0]


def generateQuadrilaterals(s):
    """Generate quadrilaterals on a triangular surface by adding midpoints and a central point."""
    # Add midpoints on each edge
    midpoints = []
    _, curves = gmodel.getAdjacencies(2, s)
    if len(curves) != 3:
        print(f"Error   : Surface {s} is not triangular, cannot split")
        return False

    for c in curves:
        new_point = addPointOnCurve(c, ratio=0.5)
        midpoints.append(new_point)

    # Create central point
    coords_list = [np.array(gmodel.getValue(0, p, []), dtype=float) for p in midpoints]
    central_point_coords = np.mean(coords_list, axis=0)
    [xproj, yproj, zproj], _ = gmodel.getClosestPoint(
        2, s, central_point_coords.tolist()
    )
    central_point_tag = gocc.addPoint(xproj, yproj, zproj)
    gocc.synchronize()

    # Create new curves
    new_curves = []
    for i in range(3):
        curve = createCurve(
            midpoints[i],
            central_point_tag,
            support_surface=s,
            nb_interpolation_points=200,
        )
        if curve:
            new_curves.append(curve)

    # Fragment the original surface with new curves and points
    if new_curves:
        fragmentEntities([(2, s)], [(1, c) for c in new_curves])
    else:
        print(f"Error   : Failed to create new curves for splitting surface {s}")
        return False
    return central_point_tag, midpoints


def generateVolumes():
    """Create OCC volumes from closed surface shells identified by findMeshableGroups()."""
    meshable = findMeshableGroups()
    created_volumes = []
    surface_list_old = gocc.getEntities(2)
    for surfaces in meshable:
        ordered_surfaces = _order_surfaces_for_shell(list(surfaces))
        nb_surfaces_before = len(gocc.getEntities(2))
        sl = gocc.addSurfaceLoop(ordered_surfaces)
        nb_surfaces_after = len(gocc.getEntities(2))
        if nb_surfaces_after != nb_surfaces_before:
            print(
                f"Warning : Surface loop creation caused fragmentation, creating additional surfaces. Consider simplifying geometry or adjusting meshing parameters."
            )
        vol = gocc.addVolume([sl])
        created_volumes.append(int(vol))
    if created_volumes:
        gocc.synchronize()
        cleanOrphanSurfaces()
    return created_volumes


def getCommonCurveFromTwoPoints(a, b):
    """Return one common curve incident to both points, if any."""
    lines_a, _ = gmodel.getAdjacencies(0, a)
    lines_b, _ = gmodel.getAdjacencies(0, b)
    inter = set(lines_a) & set(lines_b)
    return int(next(iter(inter))) if inter else None


def getCommonCurveFromTwoSurfaces(a, b):
    """Return one common boundary curve between two surfaces, if any."""
    _, lines_a = gmodel.getAdjacencies(2, a)
    _, lines_b = gmodel.getAdjacencies(2, b)
    inter = set(lines_a) & set(lines_b)
    return int(next(iter(inter))) if inter else None


def getCommonSurfacesFromTwoPoints(p1, p2):
    """Return all surfaces shared by two points."""
    lines_a, _ = gmodel.getAdjacencies(0, p1)
    lines_b, _ = gmodel.getAdjacencies(0, p2)
    surfaces_a = set()
    surfaces_b = set()
    for line in lines_a:
        surf, _ = gmodel.getAdjacencies(1, line)
        surfaces_a.update(surf)
    for line in lines_b:
        surf, _ = gmodel.getAdjacencies(1, line)
        surfaces_b.update(surf)
    common_surface = surfaces_a & surfaces_b
    return list(common_surface) if common_surface else []


def getCommonSurfacesFromTwoCurves(c1, c2):
    """Return one surface shared by two curves."""
    surfaces_a, _ = gmodel.getAdjacencies(1, c1)
    surfaces_b, _ = gmodel.getAdjacencies(1, c2)
    surfaces_a = set(surfaces_a)
    surfaces_b = set(surfaces_b)
    common_surface = surfaces_a & surfaces_b
    return list(common_surface) if common_surface else []


def getCommonSurfacesFromCurve(c):
    """Return surfaces incident to a curve."""
    surfaces, _ = gmodel.getAdjacencies(1, c)
    return list(surfaces)


def getCommonSurfaceFromCurvesList(curves):
    """Return the surface shared by a list of curves via incident surfaces."""
    if not curves:
        return None
    common = None
    for c in curves:
        surfaces, _ = gmodel.getAdjacencies(1, c)
        s = set(surfaces)
        if common is None:
            common = s
        else:
            common &= s
        if not common:
            return None
    return int(next(iter(common))) if common else None


def getCommonSurfaceFromPointsList(points):
    """Return the unique surface shared by all points, or None."""
    if not points:
        return None

    common_surfaces = None
    for point in points:
        lines, _ = gmodel.getAdjacencies(0, point)
        point_surfaces = set()
        for line in lines:
            surfaces, _ = gmodel.getAdjacencies(1, line)
            point_surfaces.update(surfaces)

        if common_surfaces is None:
            common_surfaces = point_surfaces
        else:
            common_surfaces &= point_surfaces

        if not common_surfaces:
            return None

    if not common_surfaces or len(common_surfaces) != 1:
        return None
    return int(next(iter(common_surfaces)))


def getLinkingCurves(ps1, ps2):
    """Return curves connecting two sets of points, if any."""
    curves = []
    for p1 in ps1:
        for p2 in ps2:
            c = getCommonCurveFromTwoPoints(p1, p2)
            if c is not None:
                curves.append(c)
    return curves


def getListOfOppositeSurfaces(volume):
    """Return pairs of non-adjacent surfaces in a volume."""
    _, surfaces = gmodel.getAdjacencies(3, volume)
    opposite_surface_list = []
    for i in range(len(surfaces)):
        for j in range(i + 1, len(surfaces)):
            curve = getCommonCurveFromTwoSurfaces(surfaces[i], surfaces[j])
            if curve is None:
                opposite_surface_list.append([surfaces[i], surfaces[j]])
    return opposite_surface_list


def getNewPointsFromFragmentation(surface, point_selection, scale=1e-3):
    """Return new point tags created on a surface after fragmentation."""

    _, curves = gmodel.getAdjacencies(2, surface)
    point_loop = set()
    new_points = set()

    for curve in curves:
        _, points = gmodel.getAdjacencies(1, curve)
        for p in points:
            point_loop.add(int(p))

    all_points = [int(p) for _, p in gocc.getEntities(0)]
    candidate_points = []
    for ap in all_points:
        curves, _ = gmodel.getAdjacencies(0, ap)
        if len(curves) == 2:
            candidate_points.append(ap)

    candidate_points_coords = {}
    for cp in candidate_points:
        if cp in point_loop:
            continue
        candidate_points_coords[cp] = np.array(gmodel.getValue(0, cp, []), dtype=float)

    # Compute tolerance based on CAD bounding box
    xmin, ymin, zmin, xmax, ymax, zmax = gmodel.getBoundingBox(-1, -1)
    bbox_diagonal = np.linalg.norm(
        np.array([xmax - xmin, ymax - ymin, zmax - zmin], dtype=float)
    )
    tolerance = scale * bbox_diagonal  # Scale tolerance by bounding box diagonal

    # The new points created by fragmentation should be very close to the original loop points, so we can identify them by proximity.
    for p in point_loop:
        p_coords = np.array(gmodel.getValue(0, p, []), dtype=float)
        for cp, cp_coords in candidate_points_coords.items():
            if np.linalg.norm(cp_coords - p_coords) < tolerance:
                new_points.add(cp)

    # The new points can be connected to the loop points, but we want to exclude the original loop points from the result.
    point_loop = point_loop - set(point_selection)
    new_points.update(point_loop)
    return list(new_points)


def getOppositeCurve(oppositeCurveList, curve_tag):
    """Recursively collect opposite/non-touching curves across adjacent surfaces."""
    ls, current_points = gmodel.getAdjacencies(1, curve_tag)
    for s in ls:
        _, lc = gmodel.getAdjacencies(2, s)
        for c in lc:
            _, lp = gmodel.getAdjacencies(1, c)
            if any(p in current_points for p in lp):
                continue
            if c not in oppositeCurveList:
                oppositeCurveList.add(c)
                getOppositeCurve(oppositeCurveList, c)
    return oppositeCurveList


def getPointsFromCurveLoop(loop):
    """Return point tags on a curve loop."""
    points = set()
    for curve in loop:
        _, ps = gmodel.getAdjacencies(1, curve)
        points.update(int(p) for p in ps)
    return list(points)


def getPointsFromSurface(surface):
    """Return point tags on a surface."""
    _, curves = gmodel.getAdjacencies(2, surface)
    points = set()
    for curve in curves:
        _, ps = gmodel.getAdjacencies(1, curve)
        points.update(int(p) for p in ps)
    return list(points)


def getCandidateSurfaces(ref_surface, threshold=1e-3, distance_workers=None):
    """Return candidate surfaces to fragment based on proximity to a reference surface."""
    gcs1 = time.time()
    ref_bb = gocc.getBoundingBox(2, ref_surface)

    # 1) AABB filter: find surfaces whose bounding boxes are within threshold distance of the reference surface's bounding box.
    shortlist = []
    all_surfaces = gocc.getEntities(2)
    for _, s in all_surfaces:
        if s == ref_surface:
            continue
        bb = gocc.getBoundingBox(2, s)
        if _aabb_distance(ref_bb, bb) <= threshold:
            shortlist.append(s)
    gcs2 = time.time()
    print(
        f"Info    : AABB filter, surfaces found in {gcs2 - gcs1:.2f} seconds: {len(shortlist)}/{len(all_surfaces)}."
    )

    # 2) Point-cloud filter: this gates what getDistance ever sees below, so a
    # surface dropped here is never validated at all (getDistance only runs on
    # what survives). Both ref_surface and each candidate's interior are sampled
    # (not just existing boundary points, which missed interior crossings) and
    # compared via a KDTree, with a margin proven to be a safe upper bound on the
    # sampling error. Whenever sampling is inconclusive for a surface, it fails
    # open (keeps the candidate) rather than risk silently corrupting the mesh.
    gocc.synchronize()
    new_shortlist = _filter_by_surface_point_cloud(ref_surface, shortlist, threshold)
    gcs2b = time.time()
    print(
        f"Info    : Point-cloud filter, surfaces found in {gcs2b - gcs2:.2f} seconds: {len(new_shortlist)}/{len(shortlist)}."
    )

    # 3) Exact OCC distance filter only on the narrowed shortlist
    def _distance_to_surface(surface):
        distance, *_ = gocc.getDistance(2, ref_surface, 2, surface)
        return surface, distance

    if distance_workers is None:
        distance_workers = os.getenv("HEXAMSH_DISTANCE_WORKERS", "12")

    try:
        workers = max(1, int(distance_workers))
    except (TypeError, ValueError):
        workers = 1

    if workers > 1 and len(new_shortlist) > 1:
        try:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                distances = list(executor.map(_distance_to_surface, new_shortlist))
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(
                f"Warning : Parallel OCC distance failed ({exc}); retrying sequentially"
            )
            distances = [_distance_to_surface(surface) for surface in new_shortlist]
    else:
        distances = [_distance_to_surface(surface) for surface in new_shortlist]

    candidates = [
        (2, surface) for surface, distance in distances if 0 <= distance < threshold
    ]
    gcs3 = time.time()
    print(
        f"Info    : Candidate surfaces found in {gcs3 - gcs2b:.2f} seconds among {len(candidates)}/{len(new_shortlist)} surfaces."
    )
    return candidates


def getSurfacesFromPoint(point):
    """Return surfaces incident to a point via adjacent curves."""
    surfaces = set()
    lines, _ = gmodel.getAdjacencies(0, point)
    for line in lines:
        surf, _ = gmodel.getAdjacencies(1, line)
        surfaces.update(surf)
    return list(surfaces)


def getVolumesAdjascentToSurface(surface):
    """Return volume tags adjacent to a given surface."""
    _, volumes = gmodel.getAdjacencies(2, surface)
    return [int(v) for v in volumes]


def getWeightBetweenPatterns(point_tag, pattern1, pattern2):
    """
    Compute a weight between two patterns for a point,
    based on proximity to each pattern's closest point.
    The weight is 0 if the point is on pattern2, 1 if on pattern1,
    and interpolated in between.
    """
    x, y, z = gmodel.getValue(0, point_tag, [])
    pt = np.array([x, y, z])

    # Closest point sur chaque pattern
    d1 = d2 = 0
    if pattern2 is None:
        [xc1, yc1, zc1], _ = gmodel.getClosestPoint(1, pattern1, [x, y, z])
        d1 = np.linalg.norm(pt - np.array([xc1, yc1, zc1]))
        return (
            0 if d1 < 1e-12 else 1
        )  # If only one pattern, weight is binary based on proximity
    else:
        [xc1, yc1, zc1], _ = gmodel.getClosestPoint(1, pattern1, [x, y, z])
        d1 = np.linalg.norm(pt - np.array([xc1, yc1, zc1]))
        [xc2, yc2, zc2], _ = gmodel.getClosestPoint(1, pattern2, [x, y, z])
        d2 = np.linalg.norm(pt - np.array([xc2, yc2, zc2]))
        total = d1 + d2
        if total < 1e-12:
            return (
                0.5  # degenerate case: point is on both patterns, assign equal weight
            )
        # Closer to pattern2 → more weight on pattern1, and vice versa
        w1 = d2 / total
        return w1
    return 0.5  # Default to equal weight if patterns are indistinguishable


def initializeCAD():
    """Load STEP geometry and clean duplicate OCC entities."""
    study_name = str(findCADFile())
    gmodel.add(study_name)
    gmsh.merge(study_name)
    removeDuplicates()
    v = gocc.getEntities(3)  # Force synchronization after loading
    gocc.remove(v, recursive=False)  # Remove volumes to start with clean slate
    gocc.synchronize()


def initializeGmsh():
    """Initialize global Gmsh handles and default meshing options."""
    # Cache frequently used Gmsh modules.
    gmodel_local = gmsh.model
    globals().update(
        {
            "gmodel": gmodel_local,
            "gmesh": gmodel_local.mesh,
            "goption": gmsh.option,
            "gocc": gmodel_local.occ,
        }
    )


def initializeMesh():
    """Initialize mesh with transfinite constraints on curves/surfaces/volumes."""
    start = time.time()
    volumes = generateVolumes()
    gocc.synchronize()
    initializeTransfiniteConstraints()
    end = time.time()
    print(f"Info    : Initialized mesh in {end - start:.2f} seconds")


def initializeScript(study_name, filename="replay.py"):
    """Create/reset the replay script used to persist user operations."""
    filepath = _script_path(study_name, filename)
    print(f"Info    : Initializing script {filepath}")

    if Path(filepath).exists():
        # copy paste replay.py to replay_backup.py
        backup_path = _script_path(study_name, "replay_backup.py")
        shutil.copyfile(filepath, backup_path)
        Path(filepath).unlink()

    # Minimal bootstrap script: init -> CAD load -> user ops -> finalize.
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("import gmsh\n")
        f.write("from hexamsh import hexamshcore\n\n")
        f.write("hexamshcore.initializeGmsh()\n")
        f.write(f"hexamshcore.initializeCAD()\n")
        f.write("# ===== OPERATIONS =====\n\n")
        f.write("gmsh.finalize()\n")

    return filepath


def initializeTransfiniteConstraints():
    """Set transfinite constraints on curves, surfaces, and volumes to enable recombination into hexes where possible."""

    gocc.synchronize()
    # Forcing 5 points on curves ensures a minimum of 4 elements per edge.
    for _, tag in gocc.getEntities(1):
        gmesh.setTransfiniteCurve(tag, 5)
    entities_to_hide = []
    for _, tag in gocc.getEntities(2):
        _, curves = gmodel.getAdjacencies(2, tag)
        if len(curves) == 4:
            gmesh.setTransfiniteSurface(tag)
        else:
            print(
                f"Warning : Surface {tag} has {len(curves)} bounding curves, hiding it."
            )
            entities_to_hide.append((2, tag))
    for _, tag in gocc.getEntities(3):
        gmesh.setTransfiniteVolume(tag)
    print(
        f"Info    : Set transfinite constraints on curves, surfaces, and volumes. Hiding {len(entities_to_hide)} non-quad surfaces."
    )
    gmodel.setVisibility(entities_to_hide, 0)


def merge2Curves(c1, c2, curve_dict=None):
    """Merge two curves sharing a single common endpoint into one curve, and update adjacent surfaces accordingly."""
    start = time.time()
    # Validate inputs
    common_point = _validate_curve_merge_inputs(c1, c2)
    if common_point is None:
        return None

    _, p1 = gmodel.getAdjacencies(1, c1)
    _, p2 = gmodel.getAdjacencies(1, c2)
    extra_points = (set(map(int, p1)) | set(map(int, p2))) - {int(common_point)}

    # Create merged curve
    target_curve = None
    if curve_dict is not None:
        target_curve = _find_curve_from_endpoints(curve_dict, extra_points)
    new_c = _merge_adjacent_curves_at_point(
        c1, c2, common_point, new_curve_tag=target_curve
    )

    if not new_c:
        print("Error   : Invalid endpoints or failed to create merged curve")
        return None

    gocc.synchronize()

    # Rebuild affected surfaces
    replacement_map = {c1: new_c, c2: new_c}
    affected_surfaces = _get_affected_surfaces_for_curves(c1, c2)
    _rebuild_surfaces_after_curve_merge(affected_surfaces, replacement_map)

    # Remove old surfaces
    gocc.remove(
        [(2, s) for s in affected_surfaces] + [(1, c1), (1, c2), (0, common_point)],
        recursive=False,
    )
    gocc.synchronize()
    end = time.time()
    print(f"Info    : Merged curves in {end - start:.2f} seconds")
    return new_c


def merge2Surfaces(sa, sb, edge1=None, edge2=None):
    """
    Merge two adjacent surfaces (`sa` and `sb`) into a single surface while preserving
    topological consistency of surrounding surfaces and volumes.

    Surface strategy: No need to rebuild the volumes.
    """
    start = time.time()

    # Get boundary curves for both surfaces
    result = _get_merge_boundaries(sa, sb)
    if result[0] is None:
        print("Error   : No shared boundary")
        return False

    shared_lines, outer_lines, affected_volumes, (lines_a, lines_b) = result
    affected_surfaces = {sa, sb}

    # Identify and protect triangular faces
    shared_line_set = set(int(l) for l in shared_lines)
    protected_curves = _identify_protected_curves(
        lines_a, lines_b, shared_line_set, edge1, edge2
    )

    # Identify curves at intersection points that can be updated
    curves_to_update, shared_line_set, outer_line_set, intersection_points = (
        _identify_curves_to_update(shared_lines, outer_lines, protected_curves)
    )

    # Mark all surfaces using updated curves as affected
    for c in curves_to_update:
        up_s, _ = gmodel.getAdjacencies(1, c)
        affected_surfaces.update(map(int, up_s))

    # Snapshot original loops for affected surfaces
    surface_loops = {}
    for s in affected_surfaces:
        _, loops = gocc.getCurveLoops(s)
        surface_loops[s] = loops

    # Build replacement map by merging adjacent outer curves
    replacement_map = _build_replacement_map_for_merge(
        intersection_points,
        shared_line_set,
        outer_line_set,
        protected_curves,
        edge1,
        edge2,
    )

    # Create the merged outer surface, passing source surfaces and seam curves
    # so that guide points can steer the filling toward original curvature
    merged_surface = _create_merged_outer_surface(
        outer_lines,
        replacement_map,
        source_surfaces=(sa, sb),
        seam_curves=shared_lines,
    )
    if not merged_surface:
        return False

    # Rebuild all affected surfaces
    rebuilt_surfaces = _rebuild_affected_surfaces_for_merge(
        affected_surfaces,
        sa,
        sb,
        surface_loops,
        replacement_map,
        shared_line_set,
        merged_surface,
    )

    if not rebuilt_surfaces:
        return False

    # Remove old surfaces
    gocc.remove([(2, s) for s in affected_surfaces], recursive=False)
    gocc.synchronize()
    cleanAfterFragmentation()
    end = time.time()
    print(f"Info    : Merged surfaces in {end - start:.2f} seconds")
    return True


def meshCAD(first_mesh=True):
    """Generate 3D mesh; optionally initialize transfinite constraints first."""
    if first_mesh:
        initializeMesh()
    gmesh.generate(3)


def order_curves_into_loop(curves):
    """Order an unordered list of connected curve tags into a continuous loop."""
    if not curves:
        return []

    # Build adjacency map: point -> incident oriented curve traversal.
    point_to_curves = {}
    for c in curves:
        c = abs(int(c))
        _, pts = gmodel.getAdjacencies(1, c)
        p1, p2 = int(pts[0]), int(pts[1])
        point_to_curves.setdefault(p1, []).append((c, p1, p2))
        point_to_curves.setdefault(p2, []).append((c, p2, p1))

    # Seed traversal with first curve.
    c0 = abs(int(curves[0]))
    _, pts = gmodel.getAdjacencies(1, c0)
    p_start, p_next = int(pts[0]), int(pts[1])

    ordered = [c0]
    used = {c0}
    current_point = p_next

    while len(ordered) < len(curves):
        found = False
        for c, p_from, p_to in point_to_curves[current_point]:
            if c in used:
                continue
            ordered.append(c)
            used.add(c)
            current_point = p_to
            found = True
            break

        if not found:
            print(
                "Error   : Failed to order curves into a loop, the geometry might be invalid"
            )
            return False
    return ordered


def order_points_into_loop(points):
    """Order an unordered list of connected point tags into a continuous loop."""
    # Ensure points form a consistent clockwise/anticlockwise loop
    # (angle sort on a local plane basis) to avoid crossing segments.
    if len(points) >= 3:
        coords = np.array([gmodel.getValue(0, p, []) for p in points], dtype=float)
        center = coords.mean(axis=0)
        rel = coords - center

        # Best-fit plane normal from PCA (smallest-variance axis).
        _, _, vh = np.linalg.svd(rel, full_matrices=False)
        normal = vh[-1]

        # Build stable in-plane basis (u, v).
        axis = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(axis, normal)) > 0.9:
            axis = np.array([0.0, 1.0, 0.0])
        u = np.cross(normal, axis)
        un = np.linalg.norm(u)
        if un < 1e-12:
            axis = np.array([0.0, 0.0, 1.0])
            u = np.cross(normal, axis)
            un = np.linalg.norm(u)
        u = u / un
        v = np.cross(normal, u)

        uv = np.column_stack((rel @ u, rel @ v))
        angles = np.arctan2(uv[:, 1], uv[:, 0])
        order = np.argsort(angles)

        # Rotate so first point stays deterministic (closest to original first point).
        original_first = np.array(gmodel.getValue(0, points[0], []), dtype=float)
        ordered_tags = [points[i] for i in order]
        ordered_coords = [coords[i] for i in order]
        first_idx = int(
            np.argmin([np.linalg.norm(c - original_first) for c in ordered_coords])
        )
        points = ordered_tags[first_idx:] + ordered_tags[:first_idx]
    return points


def projectPointOnCurve(point, curve):
    """Project a point onto a curve and fragment volumes with projected point."""
    start = time.time()
    coords = gmodel.getValue(0, point, [])
    if coords is None or len(coords) == 0:
        print(f"Error   : Could not find coordinates for point {point}")
        return None
    [x2, y2, z2], _ = gmodel.getClosestPoint(1, curve, coords)
    p2 = gocc.addPoint(x2, y2, z2)
    surfaces_list = getCommonSurfacesFromCurve(curve)
    fragmentEntities([(2, s) for s in surfaces_list], [(0, p2)])
    end = time.time()
    print(f"Info    : Projected point in {end - start:.2f} seconds")
    return p2


def projectSurfaceOnSurface(s1, s2):
    """Project one surface toward another via extrusion and keep intersection volume.
    If linking curves exist between the two surfaces, follow them for projection.
    Create new curves for points not connected to linking curves.
    """

    start = time.time()
    s1_center = np.array(gocc.getCenterOfMass(2, s1), dtype=float)
    normal = computeExtrusionNormal(s1, s2)

    out_dim_tags = gocc.extrude([(2, s1)], *normal.tolist())
    new_volume = out_dim_tags[1][1]

    out_dim_tags_map = fragmentEntities([(3, new_volume)], [(2, s2)])

    candidate_volumes = out_dim_tags_map[0]

    new_s1 = None
    for dim, tag in gocc.getEntities(2):
        si_center = np.array(gocc.getCenterOfMass(2, tag), dtype=float)
        if np.linalg.norm(si_center - s1_center) < 1e-6:
            new_s1 = tag
            break

    for dim, tag in candidate_volumes:
        _, surfaces = gmodel.getAdjacencies(3, tag)
        if new_s1 not in surfaces:
            gocc.remove([(dim, tag)], recursive=True)
    gocc.remove([(3, new_volume)], recursive=False)
    removeDuplicates()
    end = time.time()
    print(f"Info    : Projected surface in {end - start:.2f} seconds")


def removeCurve(c):
    """Remove a curve with OCC."""
    start = time.time()
    gocc.remove([(1, c)], recursive=False)
    gocc.synchronize()
    end = time.time()
    print(f"Info    : Removed curve {c} in {end - start:.2f} seconds")


def removeLastOperationFromScript(study_name, filename="replay.py"):
    """Remove the last recorded operation block from replay script."""
    filepath = _script_path(study_name, filename)
    if not Path(filepath).exists():
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the trailing finalize line.
    finalize_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if "gmsh.finalize()" in lines[i]:
            finalize_idx = i
            break

    if finalize_idx is None:
        return False

    content = lines[:finalize_idx]

    # Find the last operation marker.
    last_op_idx = None
    for i in range(len(content) - 1, -1, -1):
        if content[i].startswith("# --- "):
            last_op_idx = i
            break

    if last_op_idx is None:
        return False

    new_lines = content[:last_op_idx]
    while new_lines and new_lines[-1].strip() == "":
        new_lines.pop()

    new_lines.append("\n")
    new_lines.append("gmsh.finalize()\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    return True


def removeDuplicates():
    """Remove duplicate entities created by operations,
    which can cause issues in subsequent operations.
    """
    gocc.removeAllDuplicates()
    gocc.synchronize()


def removePoints(points, curve_dict=None):
    """Remove a list of point tags from the model."""
    if not points:
        return False
    for p in points:
        print(f"Info    : Removing isolated point {p}")
        curves, _ = gmodel.getAdjacencies(0, p)
        if len(curves) == 2:
            c1, c2 = curves
            new_c = merge2Curves(c1, c2, curve_dict)
            print(
                f"Info    : Merged curves {c1} and {c2} into {new_c} to remove point {p}"
            )
        else:
            print(
                f"Warning : Point {p} has {len(curves)} adjacent curves, cannot be removed"
            )
    gocc.synchronize()
    return True


def removeSurface(s):
    """Remove a surface by defeaturing its unique adjacent volume."""
    start = time.time()
    gocc.remove([(2, s)], recursive=False)
    gocc.synchronize()
    end = time.time()
    print(f"Info    : Removed surface in {end - start:.2f} seconds")
    return True


def removeVolume(v):
    """Remove a volume by defeaturing its unique adjacent surfaces."""
    start = time.time()
    gocc.remove([(3, v)], recursive=False)
    gocc.synchronize()
    end = time.time()
    print(f"Info    : Removed volume {v} in {end - start:.2f} seconds")
    return True


def replayScript(study_name):
    """Rebuild CAD state by executing recorded replay operations."""
    gmsh.clear()
    initializeGmsh()
    initializeCAD()

    replay_path = _script_path(study_name, "replay.py")
    if Path(replay_path).exists():
        with open(replay_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Skip bootstrap/finalize lines and run only operation content.
        skip_tokens = (
            "gmsh.initialize()",
            "hexamshcore.initializeGmsh()",
            "hexamshcore.initializeCAD()",
            "gmsh.finalize()",
        )

        filtered_code = "".join(
            line for line in lines if not any(token in line for token in skip_tokens)
        )
        exec(filtered_code, globals())  # pylint: disable=exec-used


def setNumberOfNodesOnEdge(c, number_of_nodes):
    """Assign transfinite node count to an edge and opposite edges, then remesh."""
    gmesh.clear()

    curve_list = getOppositeCurve({c}, c)
    int_number_of_nodes = int(number_of_nodes)
    for tag in curve_list:
        print(f"Info    : Curve {tag} set to have {int_number_of_nodes} nodes")
        gmesh.setTransfiniteCurve(tag, int_number_of_nodes)


def setNumberOfNodesOnAllEdges(nodes=5):
    """Assign transfinite node count to all edges based on their lengths and remesh."""
    gmesh.clear()
    int_nodes = int(nodes)
    for _, c in gocc.getEntities(1):
        print(f"Info    : Curve {c} set to have {int_nodes} nodes")
        gmesh.setTransfiniteCurve(c, int_nodes)


def splitSurfaceByCurve(p1, p2, pattern=None):
    """Split a surface by creating a curve between two points, with optional interpolation patterns."""
    start = time.time()
    nc = createCurve(p1, p2, pattern=pattern, nb_interpolation_points=500)
    gocc.synchronize()
    if nc is None:
        print(f"Warning : Failed to create curve between points {p1} and {p2}")
        return False
    cleanOrphanPoints()
    s1 = getSurfacesFromPoint(p1)
    s2 = getSurfacesFromPoint(p2)
    fragmentEntities([(2, s) for s in s1 + s2], [(1, nc)])
    end = time.time()
    print(f"Info    : Split surface by curve in {end - start:.2f} seconds")
    return nc


def splitTriangleSurface(s):
    """split a triangular surface into 4 smaller quadrilaterals by adding midpoints on each edge + creating a central point, then remeshing."""
    start10 = time.time()
    midpoint, midpoint_curves = generateQuadrilaterals(s)
    end10 = time.time()
    print(f"Info    : Split triangle surface {s} in {end10 - start10:.2f} seconds")
    return True


def splitVolumeBy3Points(p1, p2, p3, volumes=None):
    """Creates a surface from 3 points and fragments the volume(s) it intersects."""
    start = time.time()

    coords1 = np.array(gmodel.getValue(0, p1, []), dtype=float)
    coords2 = np.array(gmodel.getValue(0, p2, []), dtype=float)
    coords3 = np.array(gmodel.getValue(0, p3, []), dtype=float)

    p1p2 = coords2 - coords1
    p1p3 = coords3 - coords1
    normal = np.cross(p1p2, p1p3)
    if np.linalg.norm(normal) < 1e-6:
        print(f"Info    : Points {p1}, {p2}, {p3} colinéaires")
        return False

    u = p1p2 / np.linalg.norm(p1p2)
    v = np.cross(normal, u)
    v = v / np.linalg.norm(v)

    xmin, ymin, zmin, xmax, ymax, zmax = gmodel.getBoundingBox(-1, -1)
    L = np.linalg.norm([xmax - xmin, ymax - ymin, zmax - zmin]) * 1.2
    c = coords1

    tags = [gocc.addPoint(*(c + L * d)) for d in [u + v, -u + v, -u - v, u - v]]
    lines = [gocc.addLine(tags[i], tags[(i + 1) % 4]) for i in range(4)]
    big_surface = gocc.addPlaneSurface([gocc.addCurveLoop(lines)])

    surfaces = getCandidateSurfaces(big_surface)

    out_map = fragmentEntities(surfaces, [(2, big_surface)])
    if out_map is None or len(out_map) < len(surfaces):
        print("Error   : Failed to fragment surfaces with big surface")
        return False

    # Identify tool fragments corresponding to the original big surface,
    # which may be split into multiple pieces after fragmentation.
    tool_fragments = [(2, int(tag)) for dim, tag in out_map[len(surfaces)] if dim == 2]

    # Build curve to surface adjacency count for tool fragments
    # to identify exterior fragments to remove.
    c2s = defaultdict(int)
    for _, s in gocc.getEntities(2):
        _, curves = gmodel.getAdjacencies(2, s)
        for c in curves:
            c2s[int(c)] += 1

    exterior = [
        (2, s)
        for _, s in tool_fragments
        if any(
            c2s[int(c)] < 2  # courbe libre → extérieur
            for c in gmodel.getAdjacencies(2, s)[1]
        )
    ]
    if exterior:
        gocc.remove(exterior, recursive=True)
    cleanAfterFragmentation()
    print(f"Info    : Split 3 points en {time.time()-start:.2f}s")
    return True


def splitVolumeBy4Points(p1, p2, p3, p4, volumes=None):
    """Creates a surface from 4 points and fragments the volume(s) it intersects."""
    start = time.time()
    coords = [
        np.array(gmodel.getValue(0, p, []), dtype=float) for p in (p1, p2, p3, p4)
    ]
    lines = [
        gocc.addLine(int(p1), int(p2)),
        gocc.addLine(int(p2), int(p3)),
        gocc.addLine(int(p3), int(p4)),
        gocc.addLine(int(p4), int(p1)),
    ]
    loop = gocc.addCurveLoop(lines)
    surface = gocc.addPlaneSurface([loop])

    surfaces = getCandidateSurfaces(surface)
    out_map = fragmentEntities(surfaces, [(2, surface)])
    cleanAfterFragmentation()
    end = time.time()
    print(f"Info    : Split 4 points en {end-start:.2f}s")
    return True


def splitVolumeByPointLoop(point_selection):
    """Split volumes using a surface created from a given point loop."""
    start = time.time()
    initial_points = gocc.getEntities(0)
    loop = createLoopFromPoints(point_selection)
    curve_dict = {
        int(curve_tag): tuple(
            int(p) for p in gmodel.getAdjacencies(1, int(curve_tag))[1][:2]
        )
        for _, curve_tag in gocc.getEntities(1)
    }

    if not loop:
        print(
            "Error   : Failed to create a curve loop from the selected points, please try again"
        )
        return False

    cl = gocc.addCurveLoop(loop)

    if cl == -1:
        print("Error   : You have not selected a closed loop, please try again")
        return False

    new_surface = gocc.addSurfaceFilling(wireTag=cl)
    fragmentVolumeByLoop(point_selection, loop, new_surface)
    end = time.time()
    print(f"Info    : Split point loop in {end - start:.2f} seconds")
    return True


def splitWedgeVolume(s1, s2):
    """Split a wedge volume by:
    - Splitting the triangular surface s1 into 4 quadrilaterals
    - Connectind the two opposite triangular surfaces s1 and s2 with 3 side surfaces
    """
    startw = time.time()
    central_point_s1, midpoint_curves_s1 = generateQuadrilaterals(s1)
    central_point_s2, midpoint_curves_s2 = generateQuadrilaterals(s2)
    new_curves = _connecting_opposite_points(midpoint_curves_s1, midpoint_curves_s2)

    if _create_side_surfaces_from_curves(
        central_point_s1,
        midpoint_curves_s1,
        central_point_s2,
        midpoint_curves_s2,
        new_curves,
    ):
        endw = time.time()
        print(f"Info    : Split wedge volume in {endw - startw:.2f} seconds")
        return True
    return False


def writeMesh():
    """Write the current mesh to a MSH file."""
    startwm = time.time()
    name = findCADFile()
    name = Path(name).with_suffix(".msh")
    gmsh.write(str(name))
    endwm = time.time()
    print(f"Info    : Wrote mesh in {endwm - startwm:.2f} seconds")


def _aabb_distance(bb1, bb2):
    """Compute the distance between two axis-aligned bounding boxes (AABBs)."""
    # bb = (xmin, ymin, zmin, xmax, ymax, zmax)
    dx = max(0.0, bb1[0] - bb2[3], bb2[0] - bb1[3])
    dy = max(0.0, bb1[1] - bb2[4], bb2[1] - bb1[4])
    dz = max(0.0, bb1[2] - bb2[5], bb2[2] - bb1[5])
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _append_point_to_tree(
    point_tag, point_coord, existing_point_tags, existing_coords_array
):
    """Append a point to KDTree inputs and rebuild the tree."""
    from scipy.spatial import cKDTree

    existing_point_tags.append(int(point_tag))
    if existing_coords_array.size == 0:
        updated_coords_array = np.array([point_coord], dtype=float)
    else:
        updated_coords_array = np.vstack([existing_coords_array, point_coord])

    return cKDTree(updated_coords_array), updated_coords_array


def _build_existing_points_tree(surface):
    """Build a KDTree from current model points and return tags + coordinates."""
    from scipy.spatial import cKDTree

    points_on_surface = getPointsFromSurface(surface)
    existing_point_tags = []
    existing_point_coords = []
    for pt_tag in points_on_surface:
        px, py, pz = gmodel.getValue(0, pt_tag, [])
        existing_point_tags.append(int(pt_tag))
        existing_point_coords.append([float(px), float(py), float(pz)])

    existing_coords_array = np.array(existing_point_coords, dtype=float)
    point_tree = cKDTree(existing_coords_array)
    return point_tree, existing_point_tags, existing_coords_array


def _build_linking_surface_point_sets(linking_surfaces):
    """Return per-linking-surface points and their global union."""
    linking_surface_points = {
        int(surface): set(getPointsFromSurface(surface)) for surface in linking_surfaces
    }
    points_on_linking_surfaces = set()
    for points in linking_surface_points.values():
        points_on_linking_surfaces.update(points)
    return linking_surface_points, points_on_linking_surfaces


def _build_replacement_map_for_merge(
    intersection_points, shared_line_set, outer_line_set, protected_curves, edge1, edge2
):
    """Build a mapping of old curves to replacement curves by merging adjacent pairs."""
    replacement_map = {}
    selected_edges = {abs(e) for e in (edge1, edge2) if e is not None}

    for p in intersection_points:
        adj_curves, _ = gmodel.getAdjacencies(0, p)
        if len(adj_curves) > 3:
            continue
        candidates = [
            int(c)
            for c in adj_curves
            if int(c) not in shared_line_set
            and int(c) in outer_line_set
            and int(c) not in protected_curves
        ]

        if len(candidates) != 2:
            continue

        c1, c2 = candidates

        # Skip protected curves unless explicitly selected
        if (c1 in protected_curves and c1 not in selected_edges) or (
            c2 in protected_curves and c2 not in selected_edges
        ):
            continue

        new_c = _merge_adjacent_curves_at_point(c1, c2, p, new_curve_tag=None)
        if new_c:
            gocc.synchronize()
            replacement_map[c1] = new_c
            replacement_map[c2] = new_c

    return replacement_map


def _build_surface_filling_guide_points(source_surfaces, seam_curves=None):
    """Create interior guide points to steer OCC filling toward source curvature.

    Samples points densely from the source surfaces and seam curves.
    """
    guide_points = []
    for s in source_surfaces:
        points_on_s = getPointsFromSurface(s)
        guide_points.extend(_interpolate_surface_points(points_on_s, s))

    if seam_curves:
        for c in {abs(int(curve)) for curve in seam_curves if curve is not None}:
            guide_points.extend(_interpolate_curve_points(c))
    return guide_points


def _concat_point_tags(*parts):
    """Concatenate point-tag sequences while avoiding adjacent duplicates."""
    out = []
    for part in parts:
        for p in part:
            if not out or out[-1] != p:
                out.append(p)
    return out


def _connecting_opposite_points(ps1, ps2):
    """Find pairs of points from two sets of curves and create connecting curves between them."""
    pairs = []
    new_curves = []
    for i in ps1:
        for j in ps2:
            surfaces = getCommonSurfacesFromTwoPoints(i, j)
            if surfaces:
                pairs.append((i, j))
                nc = createCurve(i, j)
                if nc:
                    new_curves.append(nc)
    if new_curves:
        gocc.synchronize()
    return new_curves


def _coord_tolerance(scale=1e-8, minimum=1e-9):
    """Return a geometry-scaled coordinate tolerance."""
    xmin, ymin, zmin, xmax, ymax, zmax = gmodel.getBoundingBox(-1, -1)
    diagonal = np.linalg.norm(
        np.array([xmax - xmin, ymax - ymin, zmax - zmin], dtype=float)
    )
    return max(minimum, scale * diagonal)


def _create_curves_between_projected_points(new_points, map_points, s2):
    """Create missing boundary curves between successive projected points on s2."""
    if not new_points:
        return

    new_curves = []
    projected_points = list(map_points.keys())
    first_indices = {}
    for i, p in enumerate(projected_points):
        if p not in first_indices:
            first_indices[p] = i

    for point in new_points:
        idx = first_indices[point]
        prev_projected_point = projected_points[(idx - 1) % len(projected_points)]
        next_projected_point = projected_points[(idx + 1) % len(projected_points)]

        prev_curve = getCommonCurveFromTwoPoints(prev_projected_point, point)
        if not prev_curve:
            upper_point = map_points[point]
            upper_prev_projected_point = map_points[prev_projected_point]
            upper_prev_curve = getCommonCurveFromTwoPoints(
                upper_prev_projected_point, upper_point
            )
            prev_curve = createCurve(
                point,
                prev_projected_point,
                support_surface=s2,
                pattern=upper_prev_curve,
                nb_interpolation_points=300,
            )
            if prev_curve:
                new_curves.append(prev_curve)
                gocc.synchronize()
        next_curve = getCommonCurveFromTwoPoints(point, next_projected_point)
        if not next_curve:
            upper_point = map_points[point]
            upper_next_projected_point = map_points[next_projected_point]
            upper_next_curve = getCommonCurveFromTwoPoints(
                upper_next_projected_point, upper_point
            )
            next_curve = createCurve(
                point,
                next_projected_point,
                support_surface=s2,
                pattern=upper_next_curve,
                nb_interpolation_points=300,
            )
            if next_curve:
                new_curves.append(next_curve)
                gocc.synchronize()
    if new_curves:
        out = fragmentEntities([(2, s2)], [(1, c) for c in new_curves])
        if out == []:
            s = addSurfaceByPointLoop(new_points)
            out = fragmentEntities([(2, s2)], [(2, s)])
            if out == []:
                print(
                    f"Warning : Could not fragment surface {s2} with new curves {new_curves} or new surface {s}"
                )


def _create_merged_outer_surface(
    outer_lines, replacement_map, source_surfaces=None, seam_curves=None
):
    """Create the outer boundary surface from merged/replaced curves.

    If source surfaces are provided, add interior guide points and use a stronger
    OCC filling setup to better follow the original curvatures.
    """
    merged_boundary = _replace_curves(outer_lines, replacement_map, set())
    ordered = order_curves_into_loop(merged_boundary)

    if not ordered:
        print("Error   : Failed to order merged boundary")
        return False

    oriented_loop = createLoopFromCurves(ordered)
    cl = gocc.addCurveLoop(oriented_loop)

    guide_points = []
    if source_surfaces:
        guide_points = _build_surface_filling_guide_points(source_surfaces, seam_curves)

    merged_surface = None
    if guide_points:
        try:
            merged_surface = gocc.addSurfaceFilling(pointTags=guide_points, wireTag=cl)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"Warning : Guided surface filling failed ({exc})")
            merged_surface = None

    if not merged_surface:
        print("Info    : Failed to use guide points, using default surface filling")
        try:
            merged_surface = gocc.addSurfaceFilling(wireTag=cl)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"Error   : Surface filling failed ({exc})")
            return False

    if guide_points:
        try:
            gocc.remove([(0, int(p)) for p in guide_points], recursive=False)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    return merged_surface


def _create_side_surfaces_from_curves(c1, mp1, c2, mp2, nc):
    """Create side surfaces between two sets of curves and split the volume accordingly."""
    for c in nc:
        _, points = gmodel.getAdjacencies(1, c)
        p1, p2 = points
        existing = getCommonCurveFromTwoPoints(p1, c1)
        if existing:
            pl = [p1, c1, c2, p2]
        else:
            pl = [p1, c2, c1, p2]
        splitVolumeByPointLoop(pl)
    return True


def _create_side_surfaces_from_mapped_points(map_points):
    """Create or split side surfaces between original and projected loops."""
    map_items = list(map_points.items())
    for i, (p1, p2) in enumerate(map_items):
        next_p1, next_p2 = map_items[(i + 1) % len(map_items)]
        common_surface = getCommonSurfaceFromPointsList([p1, p2, next_p2, next_p1])

        if common_surface is None:
            addSurfaceByPointLoop([p1, p2, next_p2, next_p1])
            continue

        loop_points = [p1, p2, next_p2, next_p1]
        new_curves = []
        for j, lp1 in enumerate(loop_points):
            lp2 = loop_points[(j + 1) % len(loop_points)]
            curve = getCommonCurveFromTwoPoints(lp1, lp2)
            if not curve:
                curve = createCurve(lp1, lp2, nb_interpolation_points=300)
            if curve:
                new_curves.append(curve)

        if new_curves:
            out = fragmentEntities([(2, common_surface)], [(1, c) for c in new_curves])
            if out == []:
                print("Warning : Could not fragment surface with new curves")
        else:
            print(
                f"Warning : Could not create curves for side surface between points {p1}, {p2}, {next_p2}, {next_p1}"
            )


def _create_surface_guide_points(surface_tag, loops, max_points=100):
    """Create interior guide points on an existing surface, away from boundary curves."""
    if surface_tag is None:
        return []

    try:
        s = int(surface_tag)
        if s <= 0:
            return []
    except (TypeError, ValueError):
        return []

    boundary_curves = {
        abs(int(c)) for loop in (loops or []) for c in (loop or []) if int(c) != 0
    }
    if not boundary_curves:
        return []

    try:
        umin, umax = gmodel.getParametrizationBounds(2, s)
        u0, v0 = float(umin[0]), float(umin[1])
        u1, v1 = float(umax[0]), float(umax[1])
    except (RuntimeError, ValueError, TypeError, IndexError):
        return []

    if abs(u1 - u0) < 1e-14 or abs(v1 - v0) < 1e-14:
        return []

    xmin, ymin, zmin, xmax, ymax, zmax = gmodel.getBoundingBox(2, s)
    diag = np.linalg.norm(
        np.array([xmax - xmin, ymax - ymin, zmax - zmin], dtype=float)
    )
    min_boundary_dist = max(1e-6, 1e-3 * diag)

    guide_points = []
    grid_n = 10
    for i in range(1, grid_n - 1):
        for j in range(1, grid_n - 1):
            if len(guide_points) >= max_points:
                return guide_points

            u = u0 + (u1 - u0) * (i / (grid_n - 1))
            v = v0 + (v1 - v0) * (j / (grid_n - 1))

            try:
                x, y, z = gmodel.getValue(2, s, [float(u), float(v)])
            except (RuntimeError, ValueError, TypeError):
                continue

            p = np.array([x, y, z], dtype=float)
            too_close_to_boundary = False

            for c in boundary_curves:
                try:
                    closest, _ = gmodel.getClosestPoint(1, int(c), p.tolist())
                    d = np.linalg.norm(np.array(closest, dtype=float) - p)
                except (RuntimeError, ValueError, TypeError):
                    continue

                if d < min_boundary_dist:
                    too_close_to_boundary = True
                    break

            if too_close_to_boundary:
                continue

            guide_points.append(gocc.addPoint(float(x), float(y), float(z)))

    return guide_points


def _curve_points(curve_tag):
    """Return endpoint point tags of a curve."""
    _, pts = gmodel.getAdjacencies(1, curve_tag)
    return [int(p) for p in pts]


def _curve_type(curve_tag):
    """Classify a curve as 'line' or fallback 'spline'."""
    ctype = gmodel.getType(1, curve_tag).lower()
    if "line" in ctype:
        return "line"
    return "spline"


def _dedup(seq):
    """Deduplicate a sequence while preserving first-seen order."""
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def _find_curve_from_endpoints(curve_dict, points):
    """Return the curve tag whose two endpoints match `points` (order-independent)."""
    point_set = {int(p) for p in points}
    for curve_tag, endpoints in curve_dict.items():
        if len(endpoints) != 2:
            continue
        if {int(endpoints[0]), int(endpoints[1])} == point_set:
            return int(curve_tag)
    return None


def _find_linking_surfaces(s1, s2):
    """Find intermediate linking surfaces between s1 and s2 and ordered points lying on them."""
    points_on_s1 = set(getPointsFromSurface(s1))
    points_on_s2 = set(getPointsFromSurface(s2))
    linking_surfaces = []
    for _, stag in gmodel.getEntities(2):
        if int(stag) in (int(s1), int(s2)):
            continue
        s_pts = set(getPointsFromSurface(stag))
        if (s_pts & points_on_s1) and (s_pts & points_on_s2):
            linking_surfaces.append(int(stag))

    return linking_surfaces


def _find_surfaces_from_point_coords(point_tags, excluded_surfaces=None, min_matches=1):
    """Find surfaces whose point sets match the given point coordinates."""
    if excluded_surfaces is None:
        excluded_surfaces = set()

    tolerance = _coord_tolerance()
    target_keys = {_point_coord_key(point_tag, tolerance) for point_tag in point_tags}
    if not target_keys:
        return set()

    matched_surfaces = set()
    for _, surface_tag in gocc.getEntities(2):
        surface_tag = int(surface_tag)
        if surface_tag in excluded_surfaces:
            continue
        if (
            len(_surface_coord_keys(surface_tag, tolerance) & target_keys)
            >= min_matches
        ):
            matched_surfaces.add(surface_tag)
    return matched_surfaces


def _fragment_surfaces_from_curve_and_point_fragments(curve_fragments, point_fragments):
    """Fragment impacted surfaces using projected points created on linking curves."""
    surfaces_list = set()
    for curve in curve_fragments:
        surfaces_list.update(getCommonSurfacesFromCurve(curve))

    if surfaces_list and point_fragments:
        fragmentEntities(
            [(2, s) for s in surfaces_list], [(0, p) for p in point_fragments]
        )


def _get_affected_surfaces_for_curves(c1, c2):
    """Get all surfaces incident to either of the two curves."""
    up_surfaces_1, _ = gmodel.getAdjacencies(1, c1)
    up_surfaces_2, _ = gmodel.getAdjacencies(1, c2)
    return set(map(int, up_surfaces_1)) | set(map(int, up_surfaces_2))


def _get_merge_boundaries(sa, sb):
    """Extract shared and outer boundary curves from two surfaces."""
    volumes_a, lines_a = gmodel.getAdjacencies(2, sa)
    volumes_b, lines_b = gmodel.getAdjacencies(2, sb)

    shared_lines = sorted(set(lines_a) & set(lines_b))
    if not shared_lines:
        return None, None, None, None

    outer_lines = list((set(lines_a) | set(lines_b)) - set(shared_lines))
    affected_volumes = set(volumes_a) | set(volumes_b)

    return shared_lines, outer_lines, affected_volumes, (lines_a, lines_b)


def _identify_curves_to_update(shared_lines, outer_lines, protected_curves):
    """Identify curves at intersection points that can be merged."""
    outer_line_set = set(int(l) for l in outer_lines)
    shared_line_set = set(int(l) for l in shared_lines)
    curves_to_update = set(int(l) for l in shared_lines)

    intersection_points = _dedup(
        [p for l in shared_lines for p in _curve_points(int(l))]
    )

    # Identify candidate curves at each intersection point
    for p in intersection_points:
        adj_curves, _ = gmodel.getAdjacencies(0, int(p))
        if len(adj_curves) > 3:
            continue
        candidates = [
            int(c)
            for c in adj_curves
            if int(c) in outer_line_set
            and int(c) not in shared_line_set
            and int(c) not in protected_curves
        ]
        if 1 <= len(candidates) <= 2:
            curves_to_update.update(candidates)

    return curves_to_update, shared_line_set, outer_line_set, intersection_points


def _identify_protected_curves(lines_a, lines_b, shared_line_set, edge1, edge2):
    """Identify curves on triangular faces that should not be modified."""
    protected_curves = set()

    if len(lines_a) == 3:
        protected_curves.update(
            int(c) for c in lines_a if int(c) not in shared_line_set and int(c) != edge1
        )
    if len(lines_b) == 3:
        protected_curves.update(
            int(c) for c in lines_b if int(c) not in shared_line_set and int(c) != edge2
        )

    return protected_curves


def _interpolate_curve_points(curve_tag, num_points=10):
    """Interpolate points along a seam curve and create OCC points."""
    if curve_tag is None or num_points <= 0:
        return []

    bounds = gmodel.getParametrizationBounds(1, int(curve_tag))
    tmin, tmax = float(bounds[0][0]), float(bounds[1][0])

    interpolated_points = []
    for j in range(1, num_points + 1):
        t = tmin + (tmax - tmin) * (j / float(num_points + 1))
        x, y, z = gmodel.getValue(1, int(curve_tag), [t])
        p_tag = gocc.addPoint(float(x), float(y), float(z))
        interpolated_points.append(int(p_tag))

    return interpolated_points


def _interpolate_surface_points(points_on_s, s, num_points=5):
    """Interpolate additional points on the surface to create a denser guide point set.

    Uses edge samples + interior chord samples (all corner pairs) + centroid rays
    to get a broader mapping over the patch (not only diagonal-like paths).
    """
    if not points_on_s or len(points_on_s) < 2 or num_points <= 0:
        return []

    def _pt_xyz(pt_tag):
        xyz = gmodel.getValue(0, int(pt_tag), [])
        return float(xyz[0]), float(xyz[1]), float(xyz[2])

    corners = [_pt_xyz(p) for p in points_on_s]
    n = len(corners)
    interpolated_points = []
    seen = set()

    def _project_and_add(x, y, z):
        cp_out = gmodel.getClosestPoint(2, s, [x, y, z])
        closest = (
            cp_out[0]
            if isinstance(cp_out, (list, tuple)) and len(cp_out) > 0
            else [x, y, z]
        )
        if len(closest) >= 3:
            xp, yp, zp = float(closest[0]), float(closest[1]), float(closest[2])
        else:
            xp, yp, zp = x, y, z

        # Avoid near-duplicate OCC points from different interpolation paths
        key = (round(xp, 10), round(yp, 10), round(zp, 10))
        if key in seen:
            return False
        seen.add(key)

        p_tag = gocc.addPoint(xp, yp, zp)
        interpolated_points.append(int(p_tag))
        return True

    def _sample_segment(p0, p1):
        x0, y0, z0 = p0
        x1, y1, z1 = p1
        for j in range(1, num_points + 1):
            t = j / float(num_points + 1)
            x = x0 + t * (x1 - x0)
            y = y0 + t * (y1 - y0)
            z = z0 + t * (z1 - z0)
            _project_and_add(x, y, z)

    # For quadrangles, use only uniform bilinear interpolation over the patch.
    if n == 4:
        # Check and correct corner ordering to avoid hourglass (bow-tie) patterns
        # in either direction by testing edge crossings in a stable 2D projection.
        p0, p1, p2, p3 = corners[0], corners[1], corners[2], corners[3]

        # Project to the dominant coordinate plane (drop axis with largest normal component).
        e1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        e2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
        nrm = (
            e1[1] * e2[2] - e1[2] * e2[1],
            e1[2] * e2[0] - e1[0] * e2[2],
            e1[0] * e2[1] - e1[1] * e2[0],
        )
        ax = max(range(3), key=lambda k: abs(nrm[k]))

        def _p2(p):
            if ax == 0:
                return (p[1], p[2])
            if ax == 1:
                return (p[0], p[2])
            return (p[0], p[1])

        def _orient(a, b, c):
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

        def _on_seg(a, b, c):
            eps = 1e-14
            return (
                min(a[0], b[0]) - eps <= c[0] <= max(a[0], b[0]) + eps
                and min(a[1], b[1]) - eps <= c[1] <= max(a[1], b[1]) + eps
            )

        def _seg_inter(a, b, c, d):
            o1 = _orient(a, b, c)
            o2 = _orient(a, b, d)
            o3 = _orient(c, d, a)
            o4 = _orient(c, d, b)
            eps = 1e-14

            # Proper intersection
            if (o1 * o2 < 0.0) and (o3 * o4 < 0.0):
                return True

            # Collinear / touching
            if abs(o1) <= eps and _on_seg(a, b, c):
                return True
            if abs(o2) <= eps and _on_seg(a, b, d):
                return True
            if abs(o3) <= eps and _on_seg(c, d, a):
                return True
            if abs(o4) <= eps and _on_seg(c, d, b):
                return True
            return False

        def _is_hourglass(quad):
            q = [_p2(pt) for pt in quad]
            # In a bow-tie, one pair of opposite edges intersects.
            return _seg_inter(q[0], q[1], q[2], q[3]) or _seg_inter(
                q[1], q[2], q[3], q[0]
            )

        if _is_hourglass(corners):
            # Try both possible single swaps to fix either "horizontal" or "vertical" bow-tie.
            cand1 = [corners[0], corners[2], corners[1], corners[3]]
            cand2 = [corners[0], corners[1], corners[3], corners[2]]
            if not _is_hourglass(cand1):
                corners = cand1
            elif not _is_hourglass(cand2):
                corners = cand2

        grid_density = max(2, num_points)
        for i in range(1, grid_density + 1):
            u = i / float(grid_density + 1)
            for j in range(1, grid_density + 1):
                v = j / float(grid_density + 1)
                x = (
                    (1 - u) * (1 - v) * corners[0][0]
                    + u * (1 - v) * corners[1][0]
                    + u * v * corners[2][0]
                    + (1 - u) * v * corners[3][0]
                )
                y = (
                    (1 - u) * (1 - v) * corners[0][1]
                    + u * (1 - v) * corners[1][1]
                    + u * v * corners[2][1]
                    + (1 - u) * v * corners[3][1]
                )
                z = (
                    (1 - u) * (1 - v) * corners[0][2]
                    + u * (1 - v) * corners[1][2]
                    + u * v * corners[2][2]
                    + (1 - u) * v * corners[3][2]
                )
                _project_and_add(x, y, z)
        return interpolated_points

    # 1) Boundary edge mapping
    for i in range(n):
        _sample_segment(corners[i], corners[(i + 1) % n])

    # 2) Interior mapping across all non-adjacent corner pairs (not only diagonals)
    if n >= 4:
        for i in range(n):
            for j in range(i + 1, n):
                if j == i + 1 or (i == 0 and j == n - 1):
                    continue  # skip polygon edges already sampled
                _sample_segment(corners[i], corners[j])

    # 3) Interior mapping from centroid to each corner
    cx = sum(p[0] for p in corners) / float(n)
    cy = sum(p[1] for p in corners) / float(n)
    cz = sum(p[2] for p in corners) / float(n)
    c = (cx, cy, cz)
    for p in corners:
        _sample_segment(c, p)

    # 4) Optional edge-midpoint chords through centroid for wider areal coverage
    if n >= 3:
        mids = []
        for i in range(n):
            x0, y0, z0 = corners[i]
            x1, y1, z1 = corners[(i + 1) % n]
            mids.append(((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5))
        for m in mids:
            _sample_segment(c, m)

    # 5) Uniform grid mapping across the convex hull for even space coverage
    if n >= 3:
        grid_density = max(2, num_points // 2)
        for i in range(grid_density + 1):
            alpha = i / float(grid_density + 1) if grid_density > 0 else 0.5
            for j in range(grid_density + 1):
                beta = j / float(grid_density + 1) if grid_density > 0 else 0.5
                # Bilinear interpolation across the quad (or simplex for triangles)
                if n == 3:
                    # Barycentric coordinates for triangle
                    gamma = 1.0 - alpha - beta
                    if gamma >= 0:
                        x = (
                            alpha * corners[0][0]
                            + beta * corners[1][0]
                            + gamma * corners[2][0]
                        )
                        y = (
                            alpha * corners[0][1]
                            + beta * corners[1][1]
                            + gamma * corners[2][1]
                        )
                        z = (
                            alpha * corners[0][2]
                            + beta * corners[1][2]
                            + gamma * corners[2][2]
                        )
                        _project_and_add(x, y, z)
                elif n == 4:
                    # Bilinear interpolation for quad
                    u, v = alpha, beta
                    x = (
                        (1 - u) * (1 - v) * corners[0][0]
                        + u * (1 - v) * corners[1][0]
                        + u * v * corners[2][0]
                        + (1 - u) * v * corners[3][0]
                    )
                    y = (
                        (1 - u) * (1 - v) * corners[0][1]
                        + u * (1 - v) * corners[1][1]
                        + u * v * corners[2][1]
                        + (1 - u) * v * corners[3][1]
                    )
                    z = (
                        (1 - u) * (1 - v) * corners[0][2]
                        + u * (1 - v) * corners[1][2]
                        + u * v * corners[2][2]
                        + (1 - u) * v * corners[3][2]
                    )
                    _project_and_add(x, y, z)
                else:
                    # Fallback: weighted average for n > 4
                    x = sum(corners[k][0] for k in range(n)) / float(n)
                    y = sum(corners[k][1] for k in range(n)) / float(n)
                    z = sum(corners[k][2] for k in range(n)) / float(n)
                    _project_and_add(x, y, z)

    return interpolated_points


def _loop_area(loop):
    """Compute a rough planar area estimate of a loop using XY projection."""
    pts = []
    for c in loop:
        _, p = gmodel.getAdjacencies(1, abs(c))
        pts.append(p[0])
    coords = [gmodel.getValue(0, pt, [])[:2] for pt in pts]

    # Shoelace formula on projected 2D polygon.
    area = 0
    for i in range(len(coords)):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % len(coords)]
        area += x1 * y2 - x2 * y1

    return abs(area) * 0.5


def _merge_adjacent_curves_at_point(c1, c2, p, new_curve_tag=None):
    """Return a merged/reused curve tag for two curves sharing point p, or None on failure."""
    p1 = _other_point(c1, p)
    p2 = _other_point(c2, p)
    if p1 is None or p2 is None or p1 == p2:
        return None
    if new_curve_tag is not None:
        curve_tag = new_curve_tag
        print(
            f"Info    : Merging curves {c1} and {c2} at point {p} into new curve {curve_tag}"
        )
    else:
        curve_tag = -1

    existing = getCommonCurveFromTwoPoints(p1, p2)
    if existing is not None and existing not in (c1, c2):
        return existing

    t1 = _curve_type(c1)
    t2 = _curve_type(c2)

    if t1 == "line" and t2 == "line":
        x1 = np.array(gmodel.getValue(0, p1, []))
        xm = np.array(gmodel.getValue(0, p, []))
        x2 = np.array(gmodel.getValue(0, p2, []))
        v1 = xm - x1
        v2 = x2 - xm
        cross = np.linalg.norm(np.cross(v1, v2))
        if cross / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-16) < 1e-6:
            return gocc.addLine(p1, p2, tag=curve_tag)

        line1_pts, _ = _sample_interior_points(c1, p1)
        line2_pts, _ = _sample_interior_points(c2, p)
        all_pts = _concat_point_tags([p1], line1_pts, [p], line2_pts, [p2])
        new_c = gocc.addSpline(all_pts, tag=curve_tag)
        tmp_pts = [(0, pt) for pt in set(line1_pts + line2_pts)]
        if tmp_pts:
            try:
                gocc.remove(tmp_pts, recursive=False)
            except RuntimeError:
                pass
        return new_c

    if t1 == "line" and t2 == "spline":
        line_pts, _ = _sample_interior_points(c1, p1)
        curve_pts, _ = _sample_interior_points(c2, p)
        all_pts = _concat_point_tags([p1], line_pts, [p], curve_pts, [p2])
        return gocc.addSpline(all_pts, tag=curve_tag)

    if t1 == "spline" and t2 == "line":
        curve_pts, _ = _sample_interior_points(c1, p1)
        line_pts, _ = _sample_interior_points(c2, p)
        all_pts = _concat_point_tags([p1], curve_pts, [p], line_pts, [p2])
        return gocc.addSpline(all_pts, tag=curve_tag)

    interior1, _ = _sample_interior_points(c1, p1)
    interior2, _ = _sample_interior_points(c2, p)
    all_pts = _concat_point_tags([p1], interior1, [p], interior2, [p2])
    return gocc.addSpline(all_pts, tag=curve_tag)


def _order_surfaces_for_shell(surfaces):
    """Order surfaces of a shell by adjacency to form a valid OCC surface loop.

    Builds an ordering where each surface shares at least one boundary curve with
    the next surface, enabling proper topology for volume creation.
    """
    if not surfaces or len(surfaces) < 2:
        return surfaces

    # Start with first surface
    ordered = [surfaces[0]]
    remaining = set(surfaces[1:])

    # Greedily add surfaces that are adjacent to the current end
    while remaining:
        current_surf = ordered[-1]
        _, current_curves = gmodel.getAdjacencies(2, current_surf)
        current_curves_set = set(int(c) for c in current_curves)

        # Find a remaining surface that shares at least one curve with current
        found = False
        for next_surf in remaining:
            _, next_curves = gmodel.getAdjacencies(2, next_surf)
            next_curves_set = set(int(c) for c in next_curves)

            if current_curves_set & next_curves_set:  # Share at least one curve
                ordered.append(next_surf)
                remaining.remove(next_surf)
                found = True
                break

        if not found:
            # No adjacent surface found, just take the first remaining one
            # (this may happen in some degenerate configurations)
            next_surf = remaining.pop()
            ordered.append(next_surf)

    return ordered


def _other_point(curve_tag, point_tag):
    """Return the opposite endpoint of a 2-point curve."""
    pts = _curve_points(curve_tag)
    if len(pts) != 2:
        return False
    return pts[1] if pts[0] == point_tag else pts[0] if pts[1] == point_tag else None


def _point_coord_key(point_tag, tolerance):
    """Quantize a point position into a stable coordinate key."""
    coords = np.array(gmodel.getValue(0, int(point_tag), []), dtype=float)
    return tuple(int(round(value / tolerance)) for value in coords)


def _project_point_from_linking_surface(
    point,
    s2,
    linking_surfaces,
    linking_surface_points,
    point_tree,
    existing_point_tags,
    existing_coords_array,
    tol,
    point_fragments,
    curve_fragments,
):
    """Project a source point via a linking surface boundary curve toward s2."""
    points_on_s2 = getPointsFromSurface(s2)
    for surface in linking_surfaces:
        points_on_surface = linking_surface_points[int(surface)]
        if point not in points_on_surface:
            continue

        target_curve = getCommonCurveFromTwoSurfaces(surface, s2)
        if target_curve is None:
            continue

        coords = gmodel.getValue(0, point, [])
        if coords is None or len(coords) == 0:
            print(f"Error   : Could not find coordinates for point {point}")
            return None, point_tree, existing_coords_array

        _, lines = gmodel.getAdjacencies(2, surface)
        for line in lines:
            _, points_on_line = gmodel.getAdjacencies(1, line)
            if point in points_on_line:
                candidate_point = [p for p in points_on_line if p != point][0]
                if candidate_point in points_on_s2:
                    new_p = candidate_point
                    return int(new_p), point_tree, existing_coords_array

        [x2, y2, z2], _ = gmodel.getClosestPoint(1, target_curve, coords)
        target = np.array([x2, y2, z2], dtype=float)

        distance, idx = point_tree.query(target)

        if distance < tol:
            new_p = existing_point_tags[idx]
            return new_p, point_tree, existing_coords_array

        new_p = gocc.addPoint(x2, y2, z2)
        point_fragments.add(int(new_p))
        curve_fragments.add(int(target_curve))
        point_tree, existing_coords_array = _append_point_to_tree(
            new_p, target, existing_point_tags, existing_coords_array
        )
        return int(new_p), point_tree, existing_coords_array

    return None, point_tree, existing_coords_array


def _project_point_on_target_surface(
    point, s2, point_tree, existing_point_tags, existing_coords_array, tol
):
    """Project a point directly on s2 and ensure a connecting curve exists."""
    coords = gmodel.getValue(0, point, [])
    [x2, y2, z2], _ = gmodel.getClosestPoint(2, s2, coords)
    target = np.array([x2, y2, z2], dtype=float)

    distance, idx = point_tree.query(target)
    if distance < tol:
        new_p = existing_point_tags[idx]
        createCurve(point, new_p)
        return int(new_p), point_tree, existing_coords_array

    new_p = gocc.addPoint(x2, y2, z2)
    gocc.addLine(point, new_p)
    point_tree, existing_coords_array = _append_point_to_tree(
        new_p, target, existing_point_tags, existing_coords_array
    )
    return int(new_p), point_tree, existing_coords_array


def _rebuild_affected_surfaces_for_merge(
    affected_surfaces,
    sa,
    sb,
    surface_loops,
    replacement_map,
    shared_line_set,
    merged_surface,
):
    """Rebuild all affected surfaces after the merge operation."""
    rebuilt_surfaces = {sa: merged_surface, sb: merged_surface}

    for s in affected_surfaces:
        if s in (sa, sb):
            continue

        rebuilt_loops = []
        for loop in surface_loops[s]:
            updated = _replace_curves(loop, replacement_map, set(shared_line_set))
            ordered_loop = order_curves_into_loop(updated)
            if not ordered_loop:
                print("Error   : Failed to order merged boundary")
                return False

            if ordered_loop and len(ordered_loop) >= 3:
                rebuilt_loops.append(updated)

        if not rebuilt_loops:
            continue

        # Identify outer loop by maximum area; others are holes
        areas = [_loop_area(loop) for loop in rebuilt_loops]
        outer_idx = areas.index(max(areas))

        outer_loop = rebuilt_loops[outer_idx]
        inner_loops = [
            rebuilt_loops[i] for i in range(len(rebuilt_loops)) if i != outer_idx
        ]

        new_s = _rebuild_surface_from_loops(outer_loop, inner_loops, s)
        if new_s:
            rebuilt_surfaces[s] = new_s

    return rebuilt_surfaces


def _rebuild_surface_from_loops(outer_loop, inner_loops=None, surface_tag=None):
    """Rebuild a surface from an outer loop and optional holes using boolean operations.

    Strategy: Create outer surface, then subtract hole surfaces via boolean cut.
    This is more robust than topological hole representation for planar surfaces.
    """
    if inner_loops is None:
        inner_loops = []

    # Create outer boundary surface
    outer_cl = gocc.addCurveLoop(createLoopFromCurves(outer_loop))
    if not outer_cl:
        return None

    # Add interior guide points from the original affected surface to preserve curvature.
    guide_points = _create_surface_guide_points(
        surface_tag, [outer_loop] + list(inner_loops)
    )

    try:
        try:
            outer_surface = gocc.addSurfaceFilling(outer_cl, pointTags=guide_points)
        except TypeError:
            outer_surface = gocc.addSurfaceFilling(outer_cl)
    finally:
        if guide_points:
            gocc.remove([(0, int(pt)) for pt in guide_points], recursive=True)

    if not outer_surface:
        return None

    # If no holes, return outer surface directly
    if not inner_loops:
        return outer_surface

    # Create and subtract hole surfaces via boolean cut operations
    result_surface = outer_surface

    for hole_loop in inner_loops:
        if not hole_loop or len(hole_loop) < 3:
            continue

        try:
            hole_cl = gocc.addCurveLoop(createLoopFromCurves(hole_loop))
            if not hole_cl:
                continue

            hole_surface = gocc.addSurfaceFilling(hole_cl)
            if not hole_surface:
                continue

            # Perform boolean cut: result = result - hole
            _, out_map = gocc.cut(
                [(2, result_surface)],
                [(2, hole_surface)],
                removeObject=True,
                removeTool=True,
            )

            # Extract the new surface from boolean result
            if out_map and len(out_map) > 0:
                cut_results = out_map[0]
                if cut_results and len(cut_results) > 0:
                    # Take first result surface (usually the only one for single-hole case)
                    new_dim, new_tag = cut_results[0]
                    if new_dim == 2:
                        result_surface = int(new_tag)
                    else:
                        print(f"Warning : Boolean cut returned non-surface entity")
                        continue
                else:
                    print(f"Warning : Boolean cut produced no result")
                    continue
            else:
                print(f"Warning : Boolean cut failed or returned empty map")
                continue

        except (RuntimeError, ValueError, TypeError) as e:
            print(f"Warning : Failed to subtract hole on surface {surface_tag}: {e}")
            continue

    return result_surface


def _rebuild_surfaces_after_curve_merge(affected_surfaces, replacement_map):
    """Rebuild all affected surfaces after curve replacement with updated topology."""
    rebuilt_surfaces = {}

    for s in affected_surfaces:
        _, loops = gocc.getCurveLoops(s)
        rebuilt_loops = []

        for loop_index, loop in enumerate(loops):
            updated = _replace_curves(loop, replacement_map, set())
            ordered = order_curves_into_loop(updated)
            if not ordered:
                print("Error   : Failed to order merged boundary")
                return False

            if ordered and len(ordered) >= 3:
                rebuilt_loops.append((loop_index, updated))

        if not rebuilt_loops:
            continue

        rebuilt_loops.sort(key=lambda item: item[0])
        outer_loop = rebuilt_loops[0][1]
        inner_loops = [loop for _, loop in rebuilt_loops[1:]]

        new_s = _rebuild_surface_from_loops(outer_loop, inner_loops, s)
        if new_s:
            rebuilt_surfaces[s] = new_s

    return rebuilt_surfaces


def _replace_curves(curves, replacement_map, removed_curves):
    """Replace curve tags according to a mapping and drop removed curves."""
    out = []
    seen_abs = set()
    for c in curves:
        c = int(c)
        sign = -1 if c < 0 else 1
        base = abs(c)
        if base in removed_curves:
            continue
        nc = int(replacement_map.get(base, base))
        if nc in seen_abs:
            continue
        out.append(sign * nc)
        seen_abs.add(nc)
    return out


def _sample_interior_points(curve_tag, from_point, nb=30):
    """Sample interior points along a curve from a chosen endpoint direction."""
    _, end_pts = gmodel.getAdjacencies(1, curve_tag)
    p0, p1 = int(end_pts[0]), int(end_pts[1])
    if from_point not in (p0, p1):
        return [], None
    other = p1 if from_point == p0 else p0

    umin, umax = gmodel.getParametrizationBounds(1, curve_tag)
    u0, u1 = float(umin[0]), float(umax[0])
    if abs(u1 - u0) < 1e-14 or nb <= 0:
        return [], other

    us = np.linspace(u0, u1, nb + 2)[1:-1]

    # Reverse parameter direction if needed so first sample is near `from_point`.
    x_from = np.array(gmodel.getValue(0, from_point, []), dtype=float)
    x_first = np.array(gmodel.getValue(1, curve_tag, [float(us[0])]), dtype=float)
    x_last = np.array(gmodel.getValue(1, curve_tag, [float(us[-1])]), dtype=float)

    if np.linalg.norm(x_last - x_from) < np.linalg.norm(x_first - x_from):
        us = us[::-1]

    interior = []
    for u in us:
        xp, yp, zp = gmodel.getValue(1, curve_tag, [float(u)])
        interior.append(gocc.addPoint(xp, yp, zp))
    return interior, other


def _script_path(study_name=None, filename="replay.py"):
    """Return the path to the replay script,
    optionally within a study subdirectory.
    """
    base = _study_path(study_name)
    return str(Path(base).parent / filename)


def _study_path(study_name):
    """Return the absolute path to the STEP file of a study."""
    return str(Path(f"{study_name}.stp").resolve())


def _surface_coord_keys(surface_tag, tolerance):
    """Return quantized coordinate keys for all points of a surface."""
    return {
        _point_coord_key(point_tag, tolerance)
        for point_tag in getPointsFromSurface(surface_tag)
    }


def _sample_surface_grid_points(surface, grid_n=10):
    """Sample a parametric grid of points over a surface, including its corners."""
    try:
        umin, umax = gmodel.getParametrizationBounds(2, surface)
        u0, v0 = float(umin[0]), float(umin[1])
        u1, v1 = float(umax[0]), float(umax[1])
    except (RuntimeError, ValueError, TypeError, IndexError):
        return np.empty((0, 3))

    if abs(u1 - u0) < 1e-14 or abs(v1 - v0) < 1e-14:
        return np.empty((0, 3))

    points = []
    for i in range(grid_n + 1):
        u = u0 + (u1 - u0) * (i / grid_n)
        for j in range(grid_n + 1):
            v = v0 + (v1 - v0) * (j / grid_n)
            try:
                points.append(gmodel.getValue(2, surface, [u, v]))
            except (RuntimeError, ValueError, TypeError):
                continue
    return np.array(points, dtype=float) if points else np.empty((0, 3))


def _grid_cell_margin(samples, grid_n):
    """Return a safe upper bound on the distance from any point on the sampled
    surface to its nearest sample point.

    When the full (grid_n+1)x(grid_n+1) grid was sampled successfully, this is
    half the diagonal of the largest actual cell (computed from real per-direction
    neighbor distances, not a generic nearest-neighbor proxy, which can
    underestimate on anisotropic/stretched parametrizations). This is a rigorous
    bound for a bilinear cell. If the grid is incomplete (some evaluations
    failed), fall back to a much more generous estimate based on the sparsest gap
    observed, doubled as extra safety margin since the surface shape between
    samples is no longer controlled.
    """
    expected_n = (grid_n + 1) ** 2
    if len(samples) == expected_n:
        grid = samples.reshape(grid_n + 1, grid_n + 1, 3)
        du = np.linalg.norm(grid[1:, :, :] - grid[:-1, :, :], axis=-1)
        dv = np.linalg.norm(grid[:, 1:, :] - grid[:, :-1, :], axis=-1)
        return 0.5 * np.hypot(du.max(initial=0.0), dv.max(initial=0.0))

    if len(samples) < 2:
        return 0.0

    from scipy.spatial import cKDTree

    tree = cKDTree(samples)
    distances, _ = tree.query(samples, k=2)
    return 2.0 * float(distances[:, 1].max())


def _filter_by_surface_point_cloud(
    ref_surface, shortlist, threshold, ref_grid_n=10, candidate_grid_n=5
):
    """Narrow a shortlist by comparing point clouds sampled on ref_surface and each candidate.

    This gates what reaches the exact `getDistance` check afterwards: a surface
    dropped here is never validated at all, so the margin must be a proven safe
    upper bound on the sampling error, not just a rough shrink heuristic. Both
    surfaces are sampled over their full interior (not just their existing
    boundary points), since a candidate can be close to ref_surface through a
    crossing in the middle of a face that never touches an existing vertex.
    Whenever sampling fails or is too sparse for a surface, it fails open (keeps
    the candidate) rather than risk silently dropping a real one.
    """
    from scipy.spatial import cKDTree

    ref_samples = _sample_surface_grid_points(ref_surface, grid_n=ref_grid_n)
    if len(ref_samples) < 2:
        return shortlist

    ref_margin = _grid_cell_margin(ref_samples, ref_grid_n)
    tree = cKDTree(ref_samples)

    narrowed = []
    for s in shortlist:
        sample_parts = []
        boundary_points = getPointsFromSurface(s)
        if boundary_points:
            sample_parts.append(
                np.array(
                    [gmodel.getValue(0, p, []) for p in boundary_points], dtype=float
                )
            )

        interior_samples = _sample_surface_grid_points(s, grid_n=candidate_grid_n)
        if len(interior_samples):
            sample_parts.append(interior_samples)

        if not sample_parts:
            narrowed.append(s)
            continue

        candidate_margin = (
            _grid_cell_margin(interior_samples, candidate_grid_n)
            if len(interior_samples) >= 2
            else 0.0
        )
        margin = threshold + ref_margin + candidate_margin

        distances, _ = tree.query(np.vstack(sample_parts))
        if distances.min() <= margin:
            narrowed.append(s)
    return narrowed


def _surface_intersects_plane(s, point, normal):
    """Filtre bbox rapide avant fragment."""
    xmin, ymin, zmin, xmax, ymax, zmax = gmodel.getBoundingBox(2, s)
    corners = np.array(
        [
            [xmin, ymin, zmin],
            [xmax, ymin, zmin],
            [xmin, ymax, zmin],
            [xmax, ymax, zmin],
            [xmin, ymin, zmax],
            [xmax, ymin, zmax],
            [xmin, ymax, zmax],
            [xmax, ymax, zmax],
        ]
    )
    dists = (corners - point) @ (normal / np.linalg.norm(normal))
    return not (np.all(dists > 1e-6) or np.all(dists < -1e-6))


def _validate_curve_merge_inputs(c1, c2):
    """Validate that two curves can be merged: must share exactly one point and no other curves at that point."""
    pts1 = _curve_points(c1)
    pts2 = _curve_points(c2)
    shared = set(pts1) & set(pts2)

    if len(shared) != 1:
        print("Error   : Curves do not share exactly one point")
        return None

    p = list(shared)[0]
    adj_curves, _ = gmodel.getAdjacencies(0, p)
    adj_curves = list(map(int, adj_curves))

    if set(adj_curves) != {c1, c2}:
        print("Error   : Shared point is not isolated (more than 2 curves connected)")
        return None

    return p
