"""Replay script for pog test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([9, 2, 1, 12])

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnAllEdges ---
hexamshcore.setNumberOfNodesOnAllEdges(4.0)

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(6, 3)

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(13, 7)

# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
end = time.time()
print(f"Time elapsed: {end-start}s.")
