"""Replay script for workpiece1 test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(6, 7)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(6, 14, 23)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(21, 30)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(27, 21, 29)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(7, 14)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(32, 7, 23)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(18, 28, 12)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(1, 3, 2)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(7, 10)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(41, 11)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([41, 42, 34, 7])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(23, 108)
hexamshcore.projectPointOnCurve(23, 109)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([23, 43, 44, 33])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(6, 1)
hexamshcore.projectPointOnCurve(6, 3)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([45, 46, 14, 6])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(13, 128)
hexamshcore.projectPointOnCurve(13, 129)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([48, 47, 13, 5])

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(44, 3)

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(58, 3)

# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
end = time.time()
print(f"Time elapsed: {end-start}s.")
