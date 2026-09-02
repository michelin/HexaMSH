"""Replay script for corner test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(5, 18)
hexamshcore.projectPointOnCurve(5, 17)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([5, 13, 14, 6])

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(5, 1, 3)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(4, 3)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
end = time.time()
print(f"Time elapsed: {end-start}s.")
