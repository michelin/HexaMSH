import time

start = time.time()

import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([31, 34, 47, 44])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([45, 48, 33, 30])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(22, 24)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(18, 27)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([20, 19, 18, 17])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(18, 34)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(18, 59, 19)

# --- merge2Surfaces ---
hexamshcore.merge2Surfaces(37, 26, None, None)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(42, 115)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(43, 93)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([64, 43, 42, 63])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(20, 68)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(76, 51)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(87, 62)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(88, 97)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(86, 99)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(111, 29)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(122, 57)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(131, 30)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(15, 138)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(110, 124)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(13, 118)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(160, 120)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(55, 131)
hexamshcore.projectPointOnCurve(55, 128)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([56, 55, 98, 97])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(176, 86)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(180, 115)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(97, 45)
hexamshcore.projectPointOnCurve(97, 67)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([104, 103, 97, 98])

# --- splitWedgeVolume ---
hexamshcore.splitWedgeVolume(174, 178)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(111, 262)
hexamshcore.projectPointOnCurve(111, 263)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([113, 114, 107, 111])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(209, 180)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(223, 188)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(57, 133)
hexamshcore.projectPointOnCurve(57, 130)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([119, 120, 57, 58])

# --- splitWedgeVolume ---
hexamshcore.splitWedgeVolume(241, 243)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(122, 65)
hexamshcore.projectPointOnCurve(122, 47)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([126, 122, 129, 130])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(350, ratio=0.5)
hexamshcore.addPointOnCurve(347, ratio=0.5)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([119, 120, 132, 131])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(251, 88)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(274, 109)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(289, 152)

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(7, 165)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([70, 75, 147, 6, 5])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([118, 115, 11, 12, 148])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(100, 14)
hexamshcore.projectPointOnCurve(100, 16)
hexamshcore.projectPointOnCurve(100, 407)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([154, 153, 152, 100, 102])

# --- addVolumeBetweenTwoSurfaces ---
hexamshcore.addVolumeBetweenTwoSurfaces(159, 14)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([5, 6, 147, 91, 92])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([6, 147, 151, 8])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(212, ratio=0.4)
hexamshcore.addPointOnCurve(214, ratio=0.4)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([157, 158, 146, 2, 4])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([3, 1, 145, 53, 26])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(7, 428)
hexamshcore.projectPointOnCurve(7, 430)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([151, 8, 7, 159, 160])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(460, ratio=0.95)
hexamshcore.addPointOnCurve(462, ratio=0.95)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([145, 1, 3, 161, 162])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(206, ratio=0.7)
hexamshcore.addPointOnCurve(204, ratio=0.7)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([163, 164, 162, 161])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(10, 459)
hexamshcore.projectPointOnCurve(10, 461)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([10, 165, 166, 150, 9])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([153, 154, 150, 9])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(13, 492)
hexamshcore.projectPointOnCurve(13, 494)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([167, 168, 149, 14, 13])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(432, ratio=0.35)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(169, 433)
hexamshcore.projectPointOnCurve(169, 224)
hexamshcore.projectPointOnCurve(169, 223)
hexamshcore.projectPointOnCurve(169, 102)
hexamshcore.projectPointOnCurve(169, 113)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([169, 170, 172, 174, 173, 171])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([169, 11, 12, 148, 170])

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(509, ratio=0.41)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(175, 512)
hexamshcore.projectPointOnCurve(175, 534)
hexamshcore.projectPointOnCurve(175, 528)
hexamshcore.projectPointOnCurve(175, 532)
hexamshcore.projectPointOnCurve(175, 530)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([175, 176, 178, 180, 179, 177])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([13, 14, 149, 176, 175])

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(14, 153, 8)

# --- removeSurface ---
hexamshcore.removeSurface(619)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(473, 10)
hexamshcore.setNumberOfNodesOnEdge(451, 10)
hexamshcore.setNumberOfNodesOnEdge(96, 10)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(472, 3)
hexamshcore.setNumberOfNodesOnEdge(706, 3)
hexamshcore.setNumberOfNodesOnEdge(715, 3)
hexamshcore.setNumberOfNodesOnEdge(57, 3)
hexamshcore.setNumberOfNodesOnEdge(60, 3)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(29, 4)
hexamshcore.setNumberOfNodesOnEdge(31, 4)
hexamshcore.setNumberOfNodesOnEdge(192, 4)
hexamshcore.setNumberOfNodesOnEdge(106, 4)
hexamshcore.setNumberOfNodesOnEdge(363, 4)
hexamshcore.setNumberOfNodesOnEdge(362, 4)
hexamshcore.setNumberOfNodesOnEdge(298, 4)
hexamshcore.setNumberOfNodesOnEdge(297, 4)
hexamshcore.setNumberOfNodesOnEdge(220, 4)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(361, 3)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()
end = time.time()
print(f"Time elapsed: {end-start}s.")
