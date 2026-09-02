import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- splitWedgeVolume ---
hexamshcore.splitWedgeVolume(1, 2)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
