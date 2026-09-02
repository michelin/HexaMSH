"""Replay script for pipecreep test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([9, 6, 2, 1])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(19, 19)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(11, 12)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([22, 11, 19, 21])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(3, 42)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(4, 41)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([4, 24, 23, 3])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(25, 7)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(25, 9)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(4, 25, 27)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(57, 3)
hexamshcore.setNumberOfNodesOnEdge(51, 3)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(8, 7)
hexamshcore.setNumberOfNodesOnEdge(58, 7)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(10, 8)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()

end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
