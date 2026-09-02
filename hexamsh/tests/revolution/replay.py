"""Replay script for revolution test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(3, 1, 2)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(32, ratio=0.5)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(27, 20, 22)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(27, 5)
hexamshcore.projectPointOnCurve(27, 12)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(31, 30, 27)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(19, 53)
hexamshcore.projectPointOnCurve(19, 98)
hexamshcore.projectPointOnCurve(19, 54)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([19, 44, 45, 46, 21, 41])

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(39, 33)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(40, 34)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(155, 36)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(112, 35)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(11, 134)
hexamshcore.projectPointOnCurve(11, 92)
hexamshcore.projectPointOnCurve(11, 198)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([11, 71, 72, 73, 14, 35])

# --- removeSurfaces ---
hexamshcore.removeSurfaces([120])

# --- removeSurfaces ---
hexamshcore.removeSurfaces([115])

# --- removeSurfaces ---
hexamshcore.removeSurfaces([210])

# --- removeSurfaces ---
hexamshcore.removeSurfaces([145])

# --- removeSurfaces ---
hexamshcore.removeSurfaces([135])

# --- removeSurfaces ---
hexamshcore.removeSurfaces([185])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(74, ratio=0.2)
hexamshcore.addPointOnCurve(77, ratio=0.2)
hexamshcore.addPointOnCurve(70, ratio=0.2)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(75, 74, 76)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(72, ratio=0.8)
hexamshcore.addPointOnCurve(76, ratio=0.8)
hexamshcore.addPointOnCurve(67, ratio=0.8)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(96, 94, 95)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(314, ratio=0.4)
hexamshcore.addPointOnCurve(327, ratio=0.4)
hexamshcore.addPointOnCurve(374, ratio=0.4)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(114, 115, 116)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(80, ratio=0.5)
hexamshcore.addPointOnCurve(238, ratio=0.5)
hexamshcore.addPointOnCurve(190, ratio=0.5)
hexamshcore.addPointOnCurve(205, ratio=0.5)
hexamshcore.addPointOnCurve(150, ratio=0.5)
hexamshcore.addPointOnCurve(151, ratio=0.5)
hexamshcore.addPointOnCurve(264, ratio=0.5)
hexamshcore.addPointOnCurve(82, ratio=0.5)
hexamshcore.addPointOnCurve(146, ratio=0.5)
hexamshcore.addPointOnCurve(148, ratio=0.5)
hexamshcore.addPointOnCurve(263, ratio=0.5)
hexamshcore.addPointOnCurve(59, ratio=0.5)
hexamshcore.addPointOnCurve(61, ratio=0.5)
hexamshcore.addPointOnCurve(235, ratio=0.5)
hexamshcore.addPointOnCurve(187, ratio=0.5)
hexamshcore.addPointOnCurve(206, ratio=0.5)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([134, 135, 136, 128, 129, 126])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([137, 136, 128, 127])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([138, 139, 140, 141, 130, 133, 132, 131])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([142, 143, 144, 145, 101, 111, 94, 113])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([149, 148, 147, 146, 81, 91, 74, 93])

# --- removeSurfaces ---
hexamshcore.removeSurfaces([181])

# --- removeSurfaces ---
hexamshcore.removeSurfaces([119])

# --- removeCurves ---
hexamshcore.removeCurves([170])

# --- removeCurves ---
hexamshcore.removeCurves([171])

# --- removeCurves ---
hexamshcore.removeCurves([240])

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(378, 10)
hexamshcore.setNumberOfNodesOnEdge(305, 10)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(27, 3)
hexamshcore.setNumberOfNodesOnEdge(26, 3)
hexamshcore.setNumberOfNodesOnEdge(132, 3)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(386, 4)
hexamshcore.setNumberOfNodesOnEdge(318, 4)
hexamshcore.setNumberOfNodesOnEdge(290, 4)
hexamshcore.setNumberOfNodesOnEdge(362, 4)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
end = time.time()
print(f"Time elapsed: {end-start}s.")
