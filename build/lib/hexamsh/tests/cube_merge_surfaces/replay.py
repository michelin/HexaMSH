"""Replay script for cube_merge_surfaces test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(3, 1, None, 3)

# --- merge 2 curves ---
hexamshcore.merge2Curves(2, 10)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
end = time.time()
print(f"Time elapsed: {end-start}s.")
