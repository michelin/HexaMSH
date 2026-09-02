"""Replay script for link test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(30, 28, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(29, 31, 83, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(24, 22, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(23, 37, 73, None)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(34, 33, 2)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(32, 29, 3)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(31, 30, 5)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([6, 5, 21, 22])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([28, 27, 30, 31])

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(28, 27, 21)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(26, 23, 17)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(25, 24, 19)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(36, 35, 13)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(1, 80)
hexamshcore.projectPointOnCurve(1, 78)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([1, 2, 82, 81])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(34, 181)
hexamshcore.projectPointOnCurve(34, 179)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([34, 33, 84, 83])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([36, 35, 24, 25])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([13, 16, 20, 19])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([40, 39, 9, 8])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(8, 55)
hexamshcore.projectPointOnCurve(8, 56)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([85, 86, 9, 8])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(40, 208)
hexamshcore.projectPointOnCurve(40, 207)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([40, 39, 88, 87])

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(47, 48, 46)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(19, 10)

# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
end = time.time()
print(f"Time elapsed: {end-start}s.")
