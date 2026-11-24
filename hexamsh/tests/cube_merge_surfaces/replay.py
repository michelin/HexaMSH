import gmsh
from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(1, 3, 2, None)

# --- merge2Curves ---
hexamshcore.merge2Curves(3, 8)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
