import time

start = time.time()

import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([15, 22, 21, 16])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(20, ratio=0.5)
hexamshcore.addPointOnCurve(27, ratio=0.5)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(18, ratio=0.7)
hexamshcore.addPointOnCurve(29, ratio=0.7)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([14, 12, 13, 32, 31])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([10, 11, 7, 34, 33])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(4, 18)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(5, 35)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(7, 28)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(2, 52)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(58, 3)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(67, 43)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(60, 72)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(59, 77)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(38, 24)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(93, 13)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(90, 17)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(89, 101)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(44, 109)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(82, 115)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(83, 120)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(78, 125)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(71, 130)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(36, 135)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(105, 14)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(141, 142)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(138, 149)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(133, 156)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(111, 16)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(117, 170)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(122, 177)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(128, 184)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(127, 15)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(134, 198)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnAllEdges ---
hexamshcore.setNumberOfNodesOnAllEdges(2.0)

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(222, 6)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(144, 5)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(145, 4)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(136, 3)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(137, 6)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()

end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
