"""Replay script for patch test case."""

import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(31, 30, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(34, 33, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(37, 36, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(39, 40, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(38, 53, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(42, 43, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(1, 3, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(20, 19, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(14, 13, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(17, 16, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(11, 10, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(15, 68, None, None)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(8, 7, None, None)

# --- removeSurface ---
hexamshcore.removeSurface(27)

# --- removeSurface ---
hexamshcore.removeSurface(6)

# --- removeCurve ---
hexamshcore.removeCurve(34)

# --- removeCurve ---
hexamshcore.removeCurve(35)

# --- merge 2 curves ---
hexamshcore.merge2Curves(78, 36)

# --- addSurface ---
hexamshcore.addSurfaceByCurveLoop([23, 21, 33, 149, 64])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(25, 71)


# --- removeSurface ---
hexamshcore.removeSurface(23)

# --- removeSurface ---
hexamshcore.removeSurface(22)

# --- removeCurve ---
hexamshcore.removeCurve(67)

# --- merge 2 curves ---
hexamshcore.merge2Curves(72, 68)

# --- removeSurface ---
hexamshcore.removeSurface(64)

# --- removeCurve ---
hexamshcore.removeCurve(27)

# --- addSurface ---
hexamshcore.addSurfaceByPointLoop([81, 25, 24, 48, 49])

# --- merge 2 curves ---
hexamshcore.merge2Curves(153, 26)

# --- addSurface ---
hexamshcore.addSurfaceByPointLoop([81, 26, 28, 50])

# --- addSurface ---
hexamshcore.addSurfaceByCurveLoop([29, 24, 25, 154, 155, 28, 135])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([19, 27, 36, 14])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([1, 21, 45, 28, 26])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(19, ratio=0.4)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([82, 26, 28, 42, 8])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(1, 158)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([2, 1, 83, 43, 7])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(30, ratio=0.5)
hexamshcore.addPointOnCurve(39, ratio=0.5)
hexamshcore.addPointOnCurve(41, ratio=0.5)
hexamshcore.addPointOnCurve(45, ratio=0.5)
hexamshcore.addPointOnCurve(47, ratio=0.5)
hexamshcore.addPointOnCurve(53, ratio=0.5)
hexamshcore.addPointOnCurve(57, ratio=0.5)
hexamshcore.addPointOnCurve(59, ratio=0.5)
hexamshcore.addPointOnCurve(33, ratio=0.5)
hexamshcore.addPointOnCurve(109, ratio=0.5)
hexamshcore.addPointOnCurve(121, ratio=0.5)
hexamshcore.addPointOnCurve(120, ratio=0.5)
hexamshcore.addPointOnCurve(117, ratio=0.5)
hexamshcore.addPointOnCurve(115, ratio=0.5)
hexamshcore.addPointOnCurve(76, ratio=0.5)
hexamshcore.addPointOnCurve(111, ratio=0.5)
hexamshcore.addPointOnCurve(114, ratio=0.5)
hexamshcore.addPointOnCurve(112, ratio=0.5)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([1, 91, 92, 21])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([1, 26, 90, 91])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([84, 85, 86, 87])

# --- merge 2 curves ---
hexamshcore.merge2Curves(183, 182)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(134, 133, None, None)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(164, ratio=0.2)
hexamshcore.addPointOnCurve(165, ratio=0.2)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([103, 102, 37, 88, 13])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(230, ratio=0.5)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([84, 87, 88, 90, 26, 104])

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(24, 25, None, None)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([23, 46, 50, 81, 24])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(249, ratio=0.63)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([57, 95, 71, 105, 23, 46])

# --- merge 2 curves ---
hexamshcore.merge2Curves(197, 196)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(170, 171, None, None)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(258, ratio=0.8)
hexamshcore.addPointOnCurve(257, ratio=0.8)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([107, 106, 62, 97, 76])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(266, ratio=0.5)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([23, 108, 98, 99, 101, 100, 97, 95, 94, 93, 81, 24])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(24, 250)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([24, 118, 56, 114, 70, 48])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([52, 77, 111, 63, 53, 115])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(166, ratio=0.8)
hexamshcore.addPointOnCurve(28, ratio=0.8)
hexamshcore.addPointOnCurve(168, ratio=0.8)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([120, 121, 118, 24])

# --- merge 2 curves ---
hexamshcore.merge2Curves(303, 304)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(7, ratio=0.8)
hexamshcore.addPointOnCurve(214, ratio=0.8)
hexamshcore.addPointOnCurve(60, ratio=0.8)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([123, 124, 125, 121, 120, 119])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(256, ratio=0.2)
hexamshcore.addPointOnCurve(248, ratio=0.2)
hexamshcore.addPointOnCurve(305, ratio=0.2)
hexamshcore.addPointOnCurve(97, ratio=0.2)
hexamshcore.addPointOnCurve(287, ratio=0.2)
hexamshcore.addPointOnCurve(82, ratio=0.2)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([126, 127, 128, 131, 130, 129])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([127, 1, 83, 128])

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnAllEdges ---
hexamshcore.setNumberOfNodesOnAllEdges(3.0)

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(88, 5)
hexamshcore.setNumberOfNodesOnEdge(233, 5)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(79, 4)
hexamshcore.setNumberOfNodesOnEdge(171, 4)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()

end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
