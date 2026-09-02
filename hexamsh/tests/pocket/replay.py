"""Replay script for pocket test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(4, 7)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([20, 6, 5, 11, 15])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([19, 8, 7, 10, 16])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([3, 4, 17, 14, 9])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([18, 2, 1, 12, 13])

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(2, 6, 8)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(49, 4)

# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
end = time.time()
print(f"Time elapsed: {end-start}s.")
