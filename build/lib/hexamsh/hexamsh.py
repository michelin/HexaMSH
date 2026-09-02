"""Interactive CAD editing and hexahedral meshing workflow built on Gmsh."""

# pylint: disable=too-many-lines

from dataclasses import dataclass
from pathlib import Path
from time import monotonic

import click
import gmsh
import keyboard

try:
    from pynput import keyboard as pynput_keyboard
    from pynput import mouse
except (ImportError, OSError):
    pynput_keyboard = None
    mouse = None

from hexamsh import shortcuts  # pylint: disable=unused-import
from hexamsh import gui_parameters
from hexamsh import hexamshcore as hc

STUDY_CONTEXT = {"path": None}

if not gmsh.isInitialized():
    gmsh.initialize()
gmodel = gmsh.model  # pylint: disable=invalid-name
goption = gmsh.option  # pylint: disable=invalid-name
gonelab = gmsh.onelab  # pylint: disable=invalid-name
gfltk = gmsh.fltk  # pylint: disable=invalid-name

GUI_PARAMETERS = gui_parameters.GUI_PARAMETERS  # pylint: disable=invalid-name
_view_state = {"mode": 2}  # pylint: disable=invalid-name
_mesh_settings = {  # pylint: disable=invalid-name
    "global_default_value": 5,
    "local_default_value": 5,
    "global_previous_value": 5,
    "local_previous_value": 5,
}


@dataclass
class _SelectionClickState:
    last: tuple[float, int, int] | None = None
    right_press: tuple[int, int] | None = None


_selection_click_state = _SelectionClickState()
_mapped_selection_clicks = []
_SELECTION_FINISHED = object()
_SELECTION_REMOVED = object()


def _consume_mapped_selection_click(x, y):
    now = monotonic()
    _mapped_selection_clicks[:] = [
        click for click in _mapped_selection_clicks if click[0] >= now
    ]
    for index, (_, click_x, click_y) in enumerate(_mapped_selection_clicks):
        if abs(x - click_x) <= 3 and abs(y - click_y) <= 3:
            _mapped_selection_clicks.pop(index)
            return True
    return False


def _send_selection_remove_click(x, y):
    mapped_click = (monotonic() + 0.5, x, y)
    _mapped_selection_clicks.append(mapped_click)
    try:
        mouse_controller = mouse.Controller()
        keyboard_controller = pynput_keyboard.Controller()
        keyboard_controller.press(pynput_keyboard.Key.shift)
        try:
            mouse_controller.click(mouse.Button.left)
        finally:
            keyboard_controller.release(pynput_keyboard.Key.shift)
    except (OSError, RuntimeError, NotImplementedError) as exc:
        if mapped_click in _mapped_selection_clicks:
            _mapped_selection_clicks.remove(mapped_click)
        print(f"Warning : Could not map right-click to deselection ({exc})")


def _on_mouse_click(x, y, button, pressed):
    """Handle selection gestures without consuming right-button view drags."""
    if mouse is None:
        return

    if button == mouse.Button.right:
        if pressed:
            if shortcuts.is_selection_in_progress() and shortcuts.is_gmsh_focused():
                _selection_click_state.right_press = (x, y)
            else:
                _selection_click_state.right_press = None
        else:
            start = _selection_click_state.right_press
            _selection_click_state.right_press = None
            if (
                start is not None
                and shortcuts.is_selection_in_progress()
                and shortcuts.is_gmsh_focused()
                and abs(x - start[0]) <= 5
                and abs(y - start[1]) <= 5
            ):
                _send_selection_remove_click(x, y)
        _selection_click_state.last = None
        return

    if not pressed:
        return
    if not shortcuts.is_selection_in_progress() or not shortcuts.is_gmsh_focused():
        _selection_click_state.last = None
        return

    if button != mouse.Button.left or _consume_mapped_selection_click(x, y):
        return

    now = monotonic()
    last_click = _selection_click_state.last
    if (
        last_click is not None
        and now - last_click[0] <= 0.5
        and abs(x - last_click[1]) <= 5
        and abs(y - last_click[2]) <= 5
    ):
        _selection_click_state.last = None
        keyboard.send("e")
        return

    _selection_click_state.last = (now, x, y)


@click.command("hexamsh", help="Hexahedral meshing of CAD geometries with Gmsh")
@click.argument("file_name", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--debug",
    default=False,
    is_flag=True,
    help="Show additional information in the GUI to help debugging",
)
@click.option(
    "--replay", default=False, is_flag=True, help="Replay a previously recorded script"
)
def main(file_name, debug, replay):
    """Entry point for interactive CAD editing and meshing workflow.

    Parameters
    ----------
    file_name : str
        Path to the CAD study file (can be a STEP or BREP file).
    debug : bool
        If True, enable extra entity labels in the GUI.
    replay : bool
        If True, replay operations from the recorded script instead of starting fresh.
    """
    STUDY_CONTEXT["path"] = file_name
    if not gmsh.isInitialized():
        gmsh.initialize()
    study_name, extension = Path(file_name).stem, Path(file_name).suffix.lower()
    mouse_listener = None
    try:
        if mouse is not None:
            try:
                mouse_listener = mouse.Listener(on_click=_on_mouse_click)
                mouse_listener.start()
            except Exception as exc:  # pylint: disable=broad-exception-caught
                mouse_listener = None
                print(f"Warning : Double-click detection unavailable ({exc})")
        else:
            print("Warning : Mouse selection gestures unavailable (pynput not loaded)")

        # Create a new replay script only for fresh sessions.
        if not replay:
            hc.initializeScript(study_name, filename="replay.py")
        initializeGUI(debug)

        # Load CAD directly or reconstruct it from replayed operations.
        if not replay:
            hc.initializeCAD()
        else:
            hc.replayScript(study_name)

        checkMeshable()
        while gfltk.isAvailable() and checkForEvent(study_name, debug):
            gfltk.wait()

        finalizeGmsh(study_name)
    finally:
        if mouse_listener is not None and mouse_listener.is_alive():
            mouse_listener.stop()
        gmsh.finalize()


def splitSurfaceByCurveCommand():
    """Interactive command to split a surface by creating a curve between two selected points."""
    print("Info    : Select two points for split curve creation")
    points = selectNPoints(2)
    if points is None or len(points) != 2:
        print("Info    : Action cancelled.")
        return False
    p1, p2 = points

    print("Info    : Select a pattern curve to guide the new curve creation")
    pattern_curve = getCurve()

    nc = hc.splitSurfaceByCurve(p1, p2, pattern=pattern_curve)

    hc.appendToScript(
        {
            "name": "splitSurfaceByCurve",
            "content": (
                "nc = hexamshcore.splitSurfaceByCurve("
                f"{p1}, {p2}"
                f", pattern={pattern_curve})\n\n"
            ),
        }
    )
    return True


def addPointOnCurveCommand():
    """Interactive command to add points at the midpoint of selected curves."""
    print("Info    : Select curves to add points on (press 'q' to finish)")
    ratio = gonelab.getNumber("Geometry/Add/A point on a curve (ratio)")[0]
    selected_curves = getCurveLoop()

    if not selected_curves:
        print("Info    : Action cancelled.")
        return False

    preview_points = []

    def _clear_preview_points():
        nonlocal preview_points
        if preview_points:
            gmsh.model.occ.remove([(0, p) for p in preview_points], recursive=True)
            gmsh.model.occ.synchronize()
            preview_points = []

    def _update_preview_points(current_ratio):
        nonlocal preview_points
        _clear_preview_points()
        for c in selected_curves:
            p = hc.createPointOnCurve(c, current_ratio)
            if p is not None:
                preview_points.append(p)
        gmsh.model.occ.synchronize()
        gmsh.fltk.update()

    _update_preview_points(ratio)
    print("Info    : Adjust ratio in ONELAB, press 'e' to validate or 'q' to cancel")

    while True:
        gmsh.fltk.wait()
        new_ratio = gonelab.getNumber("Geometry/Add/A point on a curve (ratio)")[0]
        if new_ratio != ratio:
            ratio = new_ratio
            _update_preview_points(ratio)

        if keyboard.is_pressed("q"):
            _clear_preview_points()
            print("Info    : Action cancelled.")
            return False

        if keyboard.is_pressed("e"):
            break

    _clear_preview_points()

    script_content = ""
    for c in selected_curves:
        new_point = hc.addPointOnCurve(c, ratio=ratio)
        script_content += f"hexamshcore.addPointOnCurve({c}, ratio={ratio})\n"

    hc.appendToScript(
        {
            "name": "addPointOnCurve",
            "content": script_content + "\n",
        }
    )
    return True


def addSurfaceByCurveCommand():
    """Interactive command to create a new surface from a selected curve loop."""
    print("Info    : Select a loop of curves to create a new surface")
    curve_loop = getCurveLoop()
    if not curve_loop:
        print("Info    : Action cancelled.")
        return False

    common_surface = hc.getCommonSurfaceFromCurvesList(curve_loop)
    if common_surface is not None:
        print(
            "Warning : It already exists a common surface "
            f"{common_surface} for the selected curve loop, "
            "cannot create a new one."
        )
        return False

    ns = hc.addSurfaceByCurveLoop(curve_loop)
    if ns is not None:
        print(f"Info    : Created surface {ns} from curve loop {curve_loop}")

    hc.appendToScript(
        {
            "name": "addSurface",
            "content": (f"hexamshcore.addSurfaceByCurveLoop({curve_loop})\n\n"),
        }
    )
    return True


def addSurfaceByPointCommand():
    """Interactive command to create a new surface from a selected point loop."""
    print("Info    : Select a loop of points to create a new surface")
    point_loop = getPointLoop()
    if not point_loop:
        print("Info    : Action cancelled.")
        return False

    common_surface = hc.getCommonSurfaceFromPointsList(point_loop)
    if common_surface is not None:
        print(
            "Warning : It already exists a common surface "
            f"{common_surface} for the selected point loop, "
            "cannot create a new one."
        )
        return False

    ns = hc.addSurfaceByPointLoop(point_loop)
    if ns is not None:
        print(f"Info    : Created surface {ns} from point loop {point_loop}")

    hc.appendToScript(
        {
            "name": "addSurface",
            "content": (f"hexamshcore.addSurfaceByPointLoop({point_loop})\n\n"),
        }
    )
    return True


def addVolumeBetweenTwoSurfacesCommand():
    """Interactive command wrapper for `addVolumeBetweenTwoSurfaces`."""
    print("Info    : Select first surface")
    s1 = getSurface()
    if s1 is None:
        print("Info    : Action cancelled.")
        return False

    _highlight_entities_in_red([(2, s1)])
    print("Info    : Select second surface")
    s2 = getSurface()

    if s2 is None or s2 == s1:
        print("Info    : Action cancelled.")
        return False

    hc.addVolumeBetweenTwoSurfaces(s1, s2)
    hc.appendToScript(
        {
            "name": "addVolumeBetweenTwoSurfaces",
            "content": f"hexamshcore.addVolumeBetweenTwoSurfaces({s1}, {s2})\n\n",
        }
    )
    return True


def applyViewMode(mode):
    """Apply volume visibility mode:
    0 = hide meshable volumes, 1 = hide non-meshable volumes, 2 = show all volumes.
    """
    _view_state["mode"] = mode
    surface_ids, meshable_ids, non_meshable_ids = _get_surface_meshability_sets()
    surface_entities = [(2, s) for s in surface_ids]

    # First hide all
    gmodel.setVisibility(surface_entities, 0)
    gmodel.setVisibility(gmodel.getEntities(1), 0)
    gmodel.setVisibility(gmodel.getEntities(0), 0)

    if mode == 0:
        gmodel.setVisibility([(2, s) for s in non_meshable_ids], 1)
        _show_related_entities(non_meshable_ids)
    elif mode == 1:
        gmodel.setVisibility([(2, s) for s in meshable_ids], 1)
        gmodel.setVisibility([(2, s) for s in non_meshable_ids], 0)
        _show_related_entities(meshable_ids)
    elif mode == 2:
        gmodel.setVisibility(surface_entities, 1)
        gmodel.setVisibility(gmodel.getEntities(1), 1)
        gmodel.setVisibility(gmodel.getEntities(0), 1)
    gmsh.graphics.draw()


def checkForEvent(study_name, debug):
    """Handle ONELAB actions from GUI and trigger geometry/mesh updates."""
    action = gonelab.getString("ONELAB/Action")
    if action and action[0] == "check":
        gonelab.setString("ONELAB/Action", [""])

        executeAction(study_name, debug)
        hideGhostPoints()
        gmsh.graphics.draw()

    if action == ["Write mesh"]:
        if checkMeshable():
            print("Info    : Meshing CAD...")
            gonelab.setString("ONELAB/Action", [""])
            meshCADCommand(first_mesh=True)
            executeAction(study_name, debug)
            gmsh.graphics.draw()
        else:
            print(
                "Info    : All volumes must contain 6 faces to be meshable, \n"
                "          please modify the geometry and try again"
            )
            gonelab.setString("ONELAB/Action", [""])

    return True


def checkMeshable():
    """Validate surface topology for structured hex meshing without volumes."""
    meshable = hc.findMeshableGroups()
    surfaces = gmodel.getEntities(2)
    meshable_ids = {s for group in meshable for s in group}
    non_meshable = [s for s in surfaces if s[1] not in meshable_ids]
    visible_surfaces = [
        (2, s) for _, s in gmodel.getEntities(2) if gmodel.getVisibility(2, s)
    ]
    _set_color(visible_surfaces, 255, 165, 0, 255)
    _set_color([(2, s) for group in meshable for s in group], 0, 255, 0, 255)
    _set_color(non_meshable, 255, 165, 0, 255)
    # Check if there's a common surface between non_meshable and visible_surfaces
    common_surfaces = set(non_meshable) & set(visible_surfaces)
    return len(common_surfaces) == 0


def cleanSelections():
    """Reset point/curve colors after interactive operations."""
    _set_color(gmodel.getEntities(0), 0, 0, 0, 255)
    _set_color(gmodel.getEntities(1), 0, 0, 255, 255)


def executeAction(study_name, _debug):
    """Dispatch and execute current ONELAB geometry/mesh action."""

    def _get_number_value(param):
        values = gonelab.getNumber(param)
        return values[0] if len(values) else 0

    geometry_action = {
        "Geometry/Add/A surface by curve loop": addSurfaceByCurveCommand,
        "Geometry/Add/A surface by point loop": addSurfaceByPointCommand,
        "Geometry/Add/A point on a curve (ratio)": addPointOnCurveCommand,
        "Geometry/Add/A volume between two surfaces": addVolumeBetweenTwoSurfacesCommand,
        "Geometry/Project/A point on a curve": projectPointOnCurveCommand,
        "Geometry/Project/A surface on a surface": projectSurfaceOnSurfaceCommand,
        "Geometry/Merge/Two Curves": merge2CurvesCommand,
        "Geometry/Merge/Two Surfaces": merge2SurfacesCommand,
        "Geometry/Remove/A curve": removeCurveCommand,
        "Geometry/Remove/A surface": removeSurfaceCommand,
        "Geometry/Split/A surface by a curve": splitSurfaceByCurveCommand,
        "Geometry/Split/A volume by an infinite plane (3 points)": splitBy3PointsCommand,
        "Geometry/Split/A volume by a finite surface (4 points)": splitBy4PointsCommand,
        "Geometry/Split/A volume by a point loop": splitByPointLoopCommand,
        "Geometry/Split/A triangle surface": splitTriangleSurfaceCommand,
        "Geometry/Split/A wedge volume": splitWedgeVolumeCommand,
        "Geometry/Undo previous action": lambda: getPreviousCADCommand(study_name),
    }
    for param, action in geometry_action.items():
        if _get_number_value(param) != 0:
            action()
            break
    for param, action in geometry_action.items():
        gonelab.setNumber(param, [0])

    view_action = {
        "View/Show all volumes": showAllVolumesCommand,
        "View/Hide all meshable volumes": hideMeshableVolumesCommand,
        "View/Hide all non-meshable volumes": hideNonMeshableVolumesCommand,
        "View/Hide volumes by selecting a surface": hideNonMeshableVolumesBySelectionCommand,
    }
    view_action_executed = False
    for param, action in view_action.items():
        if _get_number_value(param) != 0:
            action()
            view_action_executed = True
            break
    if view_action_executed:
        for param in view_action:
            gonelab.setNumber(param, [0])

    mesh_action = {
        "Mesh/Set number of nodes on /All edges": setNumberOfNodesOnAllEdgesCommand,
        "Mesh/Set number of nodes on /One edge": setNumberOfNodesOnEdgeCommand,
    }
    for param, action in mesh_action.items():
        if param == "Mesh/Set number of nodes on /All edges":
            _mesh_settings["global_default_value"] = _get_number_value(param)
        elif param == "Mesh/Set number of nodes on /One edge":
            _mesh_settings["local_default_value"] = _get_number_value(param)
        if (
            _mesh_settings["local_default_value"]
            != _mesh_settings["local_previous_value"]
        ):
            _mesh_settings["local_previous_value"] = _mesh_settings[
                "local_default_value"
            ]
            setNumberOfNodesOnEdgeCommand(_mesh_settings["local_default_value"])
        elif (
            _mesh_settings["global_default_value"]
            != _mesh_settings["global_previous_value"]
        ):
            _mesh_settings["global_previous_value"] = _mesh_settings[
                "global_default_value"
            ]
            setNumberOfNodesOnAllEdgesCommand(_mesh_settings["global_default_value"])
    cleanSelections()
    if not view_action_executed:
        checkMeshable()
    gfltk.update()


def getCurve():
    """Interactively select and return a curve tag (dimension 1)."""
    return _select_entity(1)


def getCurveLoop():
    """Interactively build a curve loop (stop by reselecting previous curve)."""
    selection = []
    previous = -1

    while True:
        c = _select_entity(1, allow_finish=True, allow_deselect=True)
        if _remove_from_selection(c, selection, 1):
            previous = selection[-1] if selection else -1
            _refresh_selection_highlights(1, selection)
            continue
        if c is _SELECTION_FINISHED:
            return selection
        if c is None:
            return None
        if c == previous:
            return selection
        selection.append(c)
        previous = c
        _highlight_entities_in_red([(1, c)])


def getPoint():
    """Interactively select and return a point tag (dimension 0)."""
    return _select_entity(0)


def getPointLoop():
    """Interactively build a point loop (stop by reselecting previous point)."""
    selection = []
    previous = -1

    while True:
        p = _select_entity(0, allow_finish=True, allow_deselect=True)
        if _remove_from_selection(p, selection, 0):
            previous = selection[-1] if selection else -1
            _refresh_selection_highlights(0, selection)
            continue
        if p is _SELECTION_FINISHED:
            return selection
        if p is None:
            return None
        if p == previous:
            return selection
        selection.append(p)
        previous = p
        _highlight_entities_in_red([(0, p)])


def getSurface():
    """Interactively select and return a surface tag (dimension 2)."""
    return _select_entity(2)


def finalizeGmsh(study_name):
    """Write final mesh to `<study_name>.msh`."""

    line1 = "hexamshcore.meshCAD(first_mesh=False)\n"
    line2 = f"hexamshcore.writeMesh()\n"

    replay_path = hc._script_path(  # pylint: disable=protected-access
        study_name, "replay.py"
    )
    with open(replay_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if (
        line1 not in lines and checkMeshable()
    ):  # Ensure final meshing is in the script for replay.
        hc.appendToScript(
            {
                "name": "finally mesh",
                "content": (f"{line1}" f"{line2}\n"),
            }
        )
    hc.writeMesh()


def getPreviousCADCommand(study_name):
    """Undo last scripted operation by replaying script minus final block."""
    hc.removeLastOperationFromScript(study_name)
    hc.replayScript(study_name)
    return True


def hideGhostPoints():
    """
    Hide points that exist in the model
    but not in OCC (e.g. from fragmentation),
    or points not connected to any curve,
    to avoid user confusion.
    """
    model_points = set(p[1] for p in gmodel.getEntities(0))
    occ_points = set(p[1] for p in gmsh.model.occ.getEntities(0))
    occ_ghost_points = model_points - occ_points
    isolated_points = {p for p in model_points if _is_ghost_point(p)}
    ghost_points = occ_ghost_points | isolated_points
    if ghost_points:
        gmodel.setVisibility([(0, p) for p in ghost_points], False)


def hideMeshableVolumesCommand():
    """Hide all meshable surfaces and keep only non-meshable ones visible."""
    applyViewMode(0)
    _set_view_checkboxes("View/Hide all meshable volumes")
    return True


def hideNonMeshableVolumesBySelectionCommand():
    """Hide one connected patch of non-meshable surfaces from a seed selection."""
    print("Info    : Select one non-meshable surface to hide its adjacent patch")
    selected_surface = getSurface()
    if selected_surface is None:
        print("Info    : Action cancelled.")
        return False

    _, _, non_meshable_ids = _get_surface_meshability_sets()
    if selected_surface not in non_meshable_ids:
        print("Info    : Selected surface is meshable, nothing to hide.")
        return False

    to_hide = _find_adjacent_non_meshable_component(selected_surface, non_meshable_ids)
    gmodel.setVisibility([(2, s) for s in to_hide], 0)
    _refresh_curves_and_points_visibility()
    _view_state["mode"] = 3
    _set_view_checkboxes("View/Hide volumes by selecting a surface")
    print(
        "Info    : Hidden non-meshable connected patch "
        f"starting from surface {selected_surface}"
    )
    return True


def hideNonMeshableVolumesCommand():
    """Hide all non-meshable surfaces and keep only meshable ones visible."""
    applyViewMode(1)
    _set_view_checkboxes("View/Hide all non-meshable volumes")
    return True


def initializeGUI(debug=False):
    """Configure ONELAB controls and rendering/display options.

    Parameters
    ----------
    debug : bool, optional
        If True, show surface/volume/curve/point labels, by default False.
    """
    gfltk.initialize()

    gonelab.set(GUI_PARAMETERS)

    # General UI/terminal behavior.
    goption.setNumber("General.ShowModuleMenu", 0)
    goption.setNumber("General.Terminal", 0)
    goption.setNumber("General.Verbosity", 0)

    # Entity rendering style.
    goption.setNumber("Geometry.PointNumbers", 1)
    goption.setNumber("Geometry.CurveType", 0)
    goption.setNumber("Geometry.CurveWidth", 5)
    goption.setNumber("Geometry.PointSize", 10)

    # Optional debug labels.
    debug_labels = 1 if debug else 0
    goption.setNumber("Geometry.SurfaceLabels", debug_labels)
    goption.setNumber("Geometry.VolumeLabels", debug_labels)
    goption.setNumber("Geometry.CurveLabels", debug_labels)
    goption.setNumber("Geometry.PointLabels", debug_labels)

    # Keep geometry and mesh display enabled.
    goption.setNumber("Geometry.Surfaces", 1)
    goption.setNumber("Geometry.SurfaceType", 0)
    goption.setNumber("Geometry.Volumes", 1)
    goption.setNumber("Geometry.VolumeType", 1)
    goption.setNumber("Mesh.VolumeEdges", 1)
    goption.setNumber("Mesh.SurfaceFaces", 1)

    # Default color palette.
    goption.setColor("Geometry.Color.Points", 0, 0, 0, 255)
    goption.setColor("Geometry.Color.Curves", 0, 0, 255, 255)
    goption.setColor("Geometry.Color.Volumes", 180, 180, 180)


def removeCurveCommand():
    """Interactive command wrapper for `removeCurve`."""
    print("Info    : Select curve to remove")
    c = getCurve()
    if c is None:
        print("Warning : Action cancelled.")
        return False
    surfaces, _ = gmodel.getAdjacencies(1, c)
    if len(surfaces) > 0:
        print("Warning : Curve must be orphan.")
        print("Warning : Action cancelled.")
        return False
    hc.removeCurve(c)
    hc.appendToScript(
        {
            "name": "removeCurve",
            "content": f"hexamshcore.removeCurve({c})\n\n",
        }
    )
    return True


def merge2CurvesCommand():
    """Interactive command to merge two curves sharing a single isolated point."""
    print("Info    : Select first curve to merge")
    c1 = getCurve()
    if c1 is None:
        print("Info    : Action cancelled.")
        return False
    _highlight_entities_in_red([(1, c1)])

    print("Info    : Select second curve to merge")
    c2 = getCurve()
    if c2 is None:
        print("Info    : Action cancelled.")
        return False

    if c1 == c2:
        print("Info    : Can not merge one unique curve it-self.")
        print("Info    : Action cancelled.")
        return False

    new_curve = hc.merge2Curves(c1, c2)
    if new_curve is None:
        print("Info    : Curve merge failed")
        return False
    hc.appendToScript(
        {
            "name": "merge2Curves",
            "content": (f"hexamshcore.merge2Curves({c1}, {c2})\n\n"),
        }
    )
    return True


def merge2SurfacesCommand():
    """Interactive command wrapper for `merge2Surfaces`."""
    print("Info    : Select first surface to merge")
    s1 = getSurface()
    if s1 is None:
        print("Info    : Action cancelled.")
        return False

    _highlight_entities_in_red([(2, s1)])
    s2 = getSurface()

    if s2 is None:
        print("Info    : Action cancelled.")
        return False

    if s1 == s2:
        print("Info    : Can not merge one unique surface it-self.")
        print("Info    : Action cancelled.")
        return False

    c = hc.getCommonCurveFromTwoSurfaces(s1, s2)
    if c is None:
        print("Info    : The two surfaces are not adjacent, cannot be merged")
        return False
    _, lines_a = gmodel.getAdjacencies(2, s1)
    _, lines_b = gmodel.getAdjacencies(2, s2)

    e1, e2 = None, None
    # Special handling for triangular surfaces to guide the merge.
    if len(lines_a) == 3:
        print(
            "Info    : Surface "
            f"{s1} has only 3 boundary curves, please select "
            "the edge of the triangular surface to merge"
        )
        e1 = getCurve()
        if e1 is None:
            print(
                "Info    : Will try to merge without selecting a specific edge, \n"
                "          but the result might be incorrect"
            )
            e1 = None
    if len(lines_b) == 3:
        print(
            "Info    : Surface "
            f"{s2} has only 3 boundary curves, please select "
            "the edge of the triangular surface to merge"
        )
        e2 = getCurve()
        if e2 is None:
            print(
                "Info    : Will try to merge without selecting a specific edge, \n"
                "          but the result might be incorrect"
            )
            e2 = None
    hc.merge2Surfaces(s1, s2, e1, e2)
    hc.appendToScript(
        {
            "name": "merge2Surfaces",
            "content": f"hexamshcore.merge2Surfaces({s1}, {s2}, {e1}, {e2})\n\n",
        }
    )
    return True


def meshCADCommand(first_mesh):
    """Run mesh generation if model passes meshability checks."""
    if checkMeshable():
        hc.meshCAD(first_mesh=first_mesh)
        line = "hexamshcore.initializeMesh()\n"
        replay_path = hc._script_path(  # pylint: disable=protected-access
            STUDY_CONTEXT["path"], "replay.py"
        )
        with open(replay_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if line not in lines:
            hc.appendToScript(
                {
                    "name": "meshCAD",
                    "content": f"{line}\n",
                }
            )
    else:
        print(
            "Info    : All volumes must contain 6 faces to be meshable, \n"
            "          please modify the geometry and try again"
        )
    return True


def projectPointOnCurveCommand():
    """Interactive command wrapper for `projectPointOnCurve`."""
    print("Info    : Select a point to project")
    p1 = getPoint()
    if p1 is None:
        print("Info    : Action cancelled.")
        return False

    _highlight_entities_in_red([(0, p1)])
    print(
        "Info    : Select curve(s) to project onto (double-click last curve to finish)"
    )

    curves = selectMultipleCurves(mesh=False)
    if not curves:
        return False
    script_content = ""
    for c in curves:
        hc.projectPointOnCurve(p1, c)
        script_content += f"hexamshcore.projectPointOnCurve({p1}, {c})\n"

    hc.appendToScript(
        {
            "name": "projectPointOnCurve",
            "content": f"{script_content}\n",
        }
    )
    return True


def projectSurfaceOnSurfaceCommand():
    """Interactive command wrapper for `projectSurfaceOnSurface`."""
    print("Info    : Select surface to project")
    s1 = getSurface()
    if s1 is None:
        print("Info    : Action cancelled.")
        return False

    _highlight_entities_in_red([(2, s1)])
    print("Info    : Select surface to project onto")
    s2 = getSurface()

    if s2 is None or s2 == s1:
        print("Info    : Action cancelled.")
        return False

    hc.projectSurfaceOnSurface(s1, s2)
    hc.appendToScript(
        {
            "name": "projectSurfaceOnSurface",
            "content": f"hexamshcore.projectSurfaceOnSurface({s1}, {s2})\n\n",
        }
    )
    return True


def removeSurfaceCommand():
    """Interactive command wrapper for `removeSurface`."""
    print("Info    : Select surface to remove")
    s1 = getSurface()
    if s1 is None:
        print("Info    : Action cancelled.")
        return False
    hc.removeSurface(s1)
    hc.appendToScript(
        {
            "name": "removeSurface",
            "content": f"hexamshcore.removeSurface({s1})\n\n",
        }
    )
    return True


def selectNPoints(n):
    """Select exactly n points interactively, returning None on cancellation."""
    points = []
    while len(points) < n:
        p = _select_entity(0, allow_deselect=True)
        if _remove_from_selection(p, points, 0):
            _refresh_selection_highlights(0, points)
            continue
        if p is None:
            print("Info    : Action cancelled.")
            return None
        points.append(p)
        _highlight_entities_in_red([(0, p)])
    return points


def selectMultiplePoints():
    points = []
    previous = -1

    while True:
        p1 = _select_entity(0, allow_finish=True, allow_deselect=True)
        if _remove_from_selection(p1, points, 0):
            previous = points[-1] if points else -1
            _refresh_selection_highlights(0, points)
            continue
        if p1 is _SELECTION_FINISHED:
            break
        if p1 is None:
            print("Info    : Action cancelled.")
            return False

        if p1 == previous:
            break

        points.append(p1)
        previous = p1
        _highlight_entities_in_red([(0, p1)])

    return points


def selectMultipleCurves(mesh):
    curves = []
    previous = -1

    while True:
        c1 = _select_entity(1, allow_finish=True, allow_deselect=True)
        if _remove_from_selection(c1, curves, 1):
            previous = curves[-1] if curves else -1
            _refresh_selection_highlights(1, curves, mesh=mesh)
            continue
        if c1 is _SELECTION_FINISHED:
            break
        if c1 is None:
            print("Info    : Action cancelled.")
            return False

        if c1 == previous:
            break

        curves.append(c1)
        previous = c1
        if mesh:
            curve_list = hc.getOppositeCurve({c1}, c1)
            _highlight_entities_in_green([(1, c) for c in curve_list])
        _highlight_entities_in_red([(1, c1)])

    return curves


def selectMultipleSurfaces():
    surfaces = []
    previous = -1

    while True:
        s1 = _select_entity(2, allow_finish=True, allow_deselect=True)
        if _remove_from_selection(s1, surfaces, 2):
            _refresh_selection_highlights(2, surfaces)
            continue
        if s1 is _SELECTION_FINISHED:
            break
        if s1 is None:
            print("Info    : Action cancelled.")
            return False

        if s1 == previous:
            break

        surfaces.append(s1)
        previous = s1
        _highlight_entities_in_red([(2, s1)])

    return surfaces


def setNumberOfNodesOnEdgeCommand(nb_nodes=None):
    """Interactive command wrapper for `setNumberOfNodesOnEdge`."""
    print("Info    : Select an edge to set the number of nodes on")
    curves = selectMultipleCurves(mesh=True)
    if not curves:
        print("Info    : Action cancelled.")
        return False

    if nb_nodes is None:
        input_val = gonelab.getNumber("Mesh/Set number of nodes on /One edge")[0]
    else:
        input_val = nb_nodes

    content = ""
    for c in curves:
        hc.setNumberOfNodesOnEdge(c, int(input_val))
        content += f"hexamshcore.setNumberOfNodesOnEdge({c}, {int(input_val)})\n"

    replay_path = hc._script_path(  # pylint: disable=protected-access
        STUDY_CONTEXT["path"], "replay.py"
    )
    with open(replay_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    line = "hexamshcore.meshCAD(first_mesh=False)\n"

    if line in lines:
        hc.removeLastOperationFromScript(
            STUDY_CONTEXT["path"]
        )  # Remove last operation if it is meshCAD.

    hc.appendToScript(
        {
            "name": "setNumberOfNodesOnEdge",
            "content": f"{content}\n\n",
        }
    )

    hc.meshCAD(first_mesh=False)
    return True


def setNumberOfNodesOnAllEdgesCommand(nb_nodes=None):
    """Interactive command wrapper for `setNumberOfNodesOnAllEdges`."""
    print("Info    : Select an edge to set the number of nodes on")
    if nb_nodes is None:
        nb_nodes = gonelab.getNumber("Mesh/Set number of nodes on /All edges")[0]
    hc.setNumberOfNodesOnAllEdges(nb_nodes)

    replay_path = hc._script_path(  # pylint: disable=protected-access
        STUDY_CONTEXT["path"], "replay.py"
    )
    with open(replay_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    line = "hexamshcore.meshCAD(first_mesh=False)\n"

    if line in lines:
        hc.removeLastOperationFromScript(
            STUDY_CONTEXT["path"]
        )  # Remove last operation if it is meshCAD.

    edge_line = "hexamshcore.setNumberOfNodesOnEdge("
    if any(edge_line in l for l in lines):
        lines = [l for l in lines if edge_line not in l]
        with open(replay_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    edge_line = "# --- setNumberOfNodesOnEdge ---"
    if any(edge_line in l for l in lines):
        lines = [l for l in lines if edge_line not in l]
        with open(replay_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    hc.appendToScript(
        {
            "name": "setNumberOfNodesOnAllEdges",
            "content": f"hexamshcore.setNumberOfNodesOnAllEdges({nb_nodes})\n\n",
        }
    )

    hc.meshCAD(first_mesh=False)
    return True


def showAllVolumesCommand():
    """Show all volumes/surfaces and related curves/points."""
    applyViewMode(2)
    _set_view_checkboxes("View/Show all volumes")
    return True


def splitBy3PointsCommand():
    """Interactive command: split all volumes by a 3-point plane."""
    print("Info    : Select 3 points to define the splitting plane")
    points = selectNPoints(3)
    if points is None:
        return False

    p1, p2, p3 = points
    if not hc.splitVolumeBy3Points(p1, p2, p3, None):
        return False

    hc.appendToScript(
        {
            "name": "splitVolumeBy3Points",
            "content": f"hexamshcore.splitVolumeBy3Points({p1}, {p2}, {p3})\n\n",
        }
    )
    return True


def splitBy4PointsCommand():
    """Interactive command: split all volumes by a 4-point surface."""
    print("Info    : Select 4 points to define the splitting surface")
    points = selectNPoints(4)
    if points is None:
        return False

    p1, p2, p3, p4 = points
    if not hc.splitVolumeBy4Points(p1, p2, p3, p4, None):
        return False

    hc.appendToScript(
        {
            "name": "splitVolumeBy4Points",
            "content": f"hexamshcore.splitVolumeBy4Points({p1}, {p2}, {p3}, {p4})\n\n",
        }
    )
    return True


def splitByPointLoopCommand():
    """Split volumes using a surface created from a selected point loop."""
    print("Info    : Select a loop of points to split the volume(s)")
    point_selection = getPointLoop()
    if point_selection is None:
        print("Info    : Action cancelled.")
        return False

    result = hc.splitVolumeByPointLoop(point_selection)

    if result is None:
        print("Info    : Action cancelled.")
        return False
    hc.appendToScript(
        {
            "name": "splitVolumeByPointLoop",
            "content": (f"hexamshcore.splitVolumeByPointLoop({point_selection})\n\n"),
        }
    )
    return True


def splitTriangleSurfaceCommand():
    """Interactive command: split a triangle surface into 3 quadrilaterals."""
    print("Info    : Select the triangle surface")
    s1 = getSurface()
    if s1 is None:
        return False
    _, lines = gmodel.getAdjacencies(2, s1)
    if lines is None or len(lines) != 3:
        print(f"Info    : Selected surface {s1} is not a triangle.")
        return False

    if not hc.splitTriangleSurface(s1):
        return False

    hc.appendToScript(
        {
            "name": "splitTriangleSurface",
            "content": f"hexamshcore.splitTriangleSurface({s1})\n\n",
        }
    )
    return True


def splitWedgeVolumeCommand():
    """Interactive command: split a wedge volume into smaller volumes."""
    print("Info    : Select the two triangle surfaces of the wedge volume")

    s1 = getSurface()
    if s1 is None:
        print("Info    : Action cancelled.")
        return False

    _, lines = gmodel.getAdjacencies(2, s1)
    if lines is None or len(lines) != 3:
        print(f"Info    : Selected surface {s1} is not a triangle.")
        return False

    _highlight_entities_in_red([(2, s1)])

    s2 = getSurface()
    if s2 is None or s2 == s1:
        print("Info    : Action cancelled.")
        return False

    _, lines = gmodel.getAdjacencies(2, s2)
    if lines is None or len(lines) != 3:
        print(f"Info    : Selected surface {s2} is not a triangle.")
        return False
    _highlight_entities_in_red([(2, s2)])

    if not hc.splitWedgeVolume(s1, s2):
        return False

    hc.appendToScript(
        {
            "name": "splitWedgeVolume",
            "content": f"hexamshcore.splitWedgeVolume({s1}, {s2})\n\n",
        }
    )
    return True


def _get_surface_meshability_sets():
    """Return (all_surfaces, meshable_ids, non_meshable_ids)."""
    meshable_groups = hc.findMeshableGroups()
    surface_entities = gmodel.getEntities(2)
    surface_ids = {s for _, s in surface_entities}
    meshable_ids = {s for group in meshable_groups for s in group if s in surface_ids}
    non_meshable_ids = {s for s in surface_ids if s not in meshable_ids}
    return surface_ids, meshable_ids, non_meshable_ids


def _find_adjacent_non_meshable_component(seed_surface, non_meshable_ids):
    """Return the connected component of non-meshable surfaces containing seed."""
    # Build a non-meshable surface adjacency graph through shared boundary curves.
    curve_to_surfaces = {}
    for s in non_meshable_ids:
        boundary_curves = [
            c[1] for c in gmodel.getBoundary([(2, s)], False, False, False) if c[0] == 1
        ]
        for c in boundary_curves:
            curve_to_surfaces.setdefault(c, set()).add(s)

    component = {seed_surface}
    stack = [seed_surface]
    while stack:
        current = stack.pop()
        boundary_curves = [
            c[1]
            for c in gmodel.getBoundary([(2, current)], False, False, False)
            if c[0] == 1
        ]
        for curve in boundary_curves:
            for neighbor in curve_to_surfaces.get(curve, set()):
                if neighbor not in component:
                    component.add(neighbor)
                    stack.append(neighbor)

    return component


def _find_meshable_surfaces_linked_to_non_meshable(meshable_ids, non_meshable_ids):
    """Return meshable surfaces that share at least one boundary curve with non-meshable ones."""
    if not meshable_ids or not non_meshable_ids:
        return set()

    non_meshable_boundary_curves = set()
    for s in non_meshable_ids:
        non_meshable_boundary_curves.update(
            c[1] for c in gmodel.getBoundary([(2, s)], False, False, False) if c[0] == 1
        )

    linked_meshable = set()
    for s in meshable_ids:
        boundary_curves = {
            c[1] for c in gmodel.getBoundary([(2, s)], False, False, False) if c[0] == 1
        }
        if boundary_curves & non_meshable_boundary_curves:
            linked_meshable.add(s)

    return linked_meshable


def _highlight_entities_in_green(entities):
    _set_color(entities, 0, 255, 0, 255)


def _is_ghost_point(p):
    """Return True if a point has no adjacent curves in the model graph."""
    curves, _ = gmsh.model.getAdjacencies(0, p)
    return len(curves) == 0


def _highlight_entities_in_red(entities):
    _set_color(entities, 255, 0, 0, 255)


def _select_entity(expected_dim, allow_finish=False, allow_deselect=False):
    while True:
        with shortcuts.selecting_entities():
            out = gfltk.selectEntities()
        if out and out[0] == 2:
            if allow_deselect and out[1]:
                dim, tag = out[1][0]
                if dim == expected_dim:
                    return (_SELECTION_REMOVED, tag)
            continue
        if out and out[0] == 4 and allow_finish:
            return _SELECTION_FINISHED
        if not out or not out[0] or not out[1]:
            return None
        dim, tag = out[1][0]
        if dim == expected_dim:
            return tag
        print(
            f"Info    : Wrong entity type selected, expected dimension {expected_dim}"
        )


def _remove_from_selection(result, selection, dim):
    if not isinstance(result, tuple) or result[0] is not _SELECTION_REMOVED:
        return False

    tag = result[1]
    if tag in selection:
        selection.remove(tag)
    return True


def _refresh_selection_highlights(dim, selection, mesh=False):
    if dim == 0:
        _set_color(gmodel.getEntities(0), 0, 0, 0)
    elif dim == 1:
        _set_color(gmodel.getEntities(1), 0, 0, 255)
        if mesh:
            opposite_curves = set()
            for curve in selection:
                opposite_curves.update(hc.getOppositeCurve({curve}, curve))
            _highlight_entities_in_green([(1, curve) for curve in opposite_curves])
    elif dim == 2:
        checkMeshable()

    _highlight_entities_in_red([(dim, tag) for tag in selection])


def _set_view_checkboxes(active_param):
    """Mark one view checkbox as active and clear the others."""
    view_params = [
        "View/Show all volumes",
        "View/Hide all meshable volumes",
        "View/Hide all non-meshable volumes",
        "View/Hide volumes by selecting a surface",
    ]
    for param in view_params:
        gonelab.setNumber(param, [1 if param == active_param else 0])


def _set_color(entities, r, g, b, a=255):
    entities = list(entities)
    if entities:
        gmodel.setColor(entities, r, g, b, a)


def _show_related_entities(surface_ids):
    surfaces = [(2, s) for s in surface_ids]
    if not surfaces:
        return
    curves = list(
        {c for c in gmodel.getBoundary(surfaces, False, False, False) if c[0] == 1}
    )
    points = (
        list({p for p in gmodel.getBoundary(curves, False, False, False) if p[0] == 0})
        if curves
        else []
    )
    if curves:
        gmodel.setVisibility(curves, 1)
    if points:
        gmodel.setVisibility(points, 1)


def _refresh_curves_and_points_visibility():
    """Show only curves/points connected to currently visible surfaces."""
    gmodel.setVisibility(gmodel.getEntities(1), 0)
    gmodel.setVisibility(gmodel.getEntities(0), 0)

    visible_surface_ids = [
        s for _, s in gmodel.getEntities(2) if gmodel.getVisibility(2, s)
    ]
    _show_related_entities(visible_surface_ids)
