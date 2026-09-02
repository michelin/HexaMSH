import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(23, 5)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(1, 4, None, None)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(22, 39)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(15, 39)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(26, 46)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(27, 52)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(19, 60)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(14, 13, None, None)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(62, 73)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(79, 74)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(87, 12, None, None)

# --- merge 2 curves ---
hexamshcore.merge2Curves(35, 34)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(98, 95, None, None)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(90, 99)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(54, 89)

# --- merge 2 curves ---
hexamshcore.merge2Curves(24, 25)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([9, 31, 54, 2, 1])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([10, 30, 55, 6, 5])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(44, 55)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(42, 165)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([78, 42, 61, 53, 49, 41])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([64, 44, 79, 38, 37, 56])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(9, 2)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(8, 114)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(16, ratio=0.2)

# --- splitSurfaceByCurve ---
nc = hexamshcore.splitSurfaceByCurve(32, 83, pattern=8)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(10, 37)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([49, 37, 44, 42])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([37, 22, 25, 44])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([42, 49, 50, 43])

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(128, 3)
hexamshcore.setNumberOfNodesOnEdge(30, 3)
hexamshcore.setNumberOfNodesOnEdge(153, 3)
hexamshcore.setNumberOfNodesOnEdge(26, 3)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(72, 2)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(140, 8)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(68, 3)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(13, 4)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(117, 3)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()

end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
