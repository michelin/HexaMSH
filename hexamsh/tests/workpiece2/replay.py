import time

start = time.time()

import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([17, 18, 19, 20])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(42, 37)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(43, 40)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([56, 43, 42, 55])

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(37, 24, None, None)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([48, 33, 30, 45])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([31, 34, 47, 44])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(18, 36)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(20, 34)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(58, 31)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(19, 28)
hexamshcore.projectPointOnCurve(19, 49)
hexamshcore.projectPointOnCurve(19, 34)
hexamshcore.projectPointOnCurve(19, 22)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([18, 70, 69, 68, 67, 19, 66, 63])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(68, 88)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(70, 88)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(22, 41)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(42, 67)
hexamshcore.projectPointOnCurve(42, 45)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([82, 81, 42, 55])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(57, 113)
hexamshcore.projectPointOnCurve(57, 110)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([57, 83, 84, 58])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(128, 70)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(132, 100)

# --- splitWedgeVolume ---
hexamshcore.splitWedgeVolume(126, 130)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(155, 19)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(83, 240)
hexamshcore.projectPointOnCurve(83, 239)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([100, 99, 83, 84])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(152, 132)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(174, 138)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(185, 29)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(140, 190)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([25, 54, 27, 15])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(83, 188)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(15, 30)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(7, 224)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(19, 30)
hexamshcore.projectPointOnCurve(19, 53)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([19, 73, 125, 124])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(13, 94)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(252, 97)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([66, 72, 118, 6, 5])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([11, 12, 117, 73, 19])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(13, 330)
hexamshcore.projectPointOnCurve(13, 328)
hexamshcore.projectPointOnCurve(13, 340)
hexamshcore.projectPointOnCurve(13, 341)
hexamshcore.projectPointOnCurve(13, 145)
hexamshcore.projectPointOnCurve(13, 152)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([119, 14, 13, 130, 133, 134, 135, 132, 131])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(13, 334)
hexamshcore.projectPointOnCurve(13, 332)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(10, 375)
hexamshcore.projectPointOnCurve(10, 377)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(7, 379)
hexamshcore.projectPointOnCurve(7, 381)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([13, 14, 119, 137, 136])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([10, 9, 123, 139, 140])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([7, 8, 122, 141, 142])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([110, 109, 118, 6, 5])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([6, 118, 122, 8])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(284, ratio=0.4)
hexamshcore.addPointOnCurve(287, ratio=0.4)

# --- addSurface ---
hexamshcore.splitVolumeByPointLoop([144, 143, 4, 2, 120])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([3, 1, 121, 53, 26])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(412, ratio=0.9)
hexamshcore.addPointOnCurve(409, ratio=0.9)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([3, 1, 121, 146, 145])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(305, ratio=0.7)
hexamshcore.addPointOnCurve(303, ratio=0.7)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([147, 148, 146, 145])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(13, ratio=0.8)
hexamshcore.addPointOnCurve(11, ratio=0.8)
hexamshcore.addPointOnCurve(318, ratio=0.8)
hexamshcore.addPointOnCurve(410, ratio=0.8)
hexamshcore.addPointOnCurve(411, ratio=0.8)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([149, 150, 151, 152, 153])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([150, 151, 117, 12])

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(6, 2, 9)

# --- removeSurface ---
hexamshcore.removeSurfaces([516])

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(496, 3)
hexamshcore.setNumberOfNodesOnEdge(494, 3)
hexamshcore.setNumberOfNodesOnEdge(343, 3)
hexamshcore.setNumberOfNodesOnEdge(128, 3)
hexamshcore.setNumberOfNodesOnEdge(60, 3)
hexamshcore.setNumberOfNodesOnEdge(470, 3)
hexamshcore.setNumberOfNodesOnEdge(439, 3)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()

end = time.time()

print(f"Time elapsed: {end-start}s.")