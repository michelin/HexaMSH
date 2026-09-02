import time

start = time.time()
import gmsh

from hexamsh import hexamshcore

hexamshcore.initializeGmsh()
hexamshcore.initializeCAD()
# ===== OPERATIONS =====

# --- splitTriangleSurface ---
hexamshcore.splitTriangleSurface(30)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(24, 53)
hexamshcore.projectPointOnCurve(24, 37)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([24, 21, 56, 55])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(42, 93)
hexamshcore.projectPointOnCurve(42, 91)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([57, 58, 25, 42])

# --- splitTriangleSurface ---
hexamshcore.splitTriangleSurface(46)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(48, 44)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(47, 59)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(52, 37)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(4, 36)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(11, 100)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(9, 106)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(10, 112)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(12, 118)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(31, 123)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(32, 129)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(30, 143)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(2, 156)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(3, 169)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(21, 186)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(64, ratio=0.5)
hexamshcore.addPointOnCurve(297, ratio=0.5)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(116, 205)

# --- projectSurfaceOnSurface ---
hexamshcore.projectSurfaceOnSurface(111, 202)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(93, 39)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(103, 93, 94)

# --- addPointOnCurve ---
hexamshcore.addPointOnCurve(321, ratio=0.5)
hexamshcore.addPointOnCurve(344, ratio=0.5)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(108, 343)

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(109, 108, 107)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([44, 35, 109, 108])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([32, 47, 105, 106])

# --- splitVolumeBy3Points ---
hexamshcore.splitVolumeBy3Points(57, 58, 42)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([36, 43, 143, 144])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([31, 141, 142, 48])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(53, 2)
hexamshcore.projectPointOnCurve(53, 6)
hexamshcore.projectPointOnCurve(53, 10)
hexamshcore.projectPointOnCurve(53, 433)
hexamshcore.projectPointOnCurve(53, 443)
hexamshcore.projectPointOnCurve(53, 450)
hexamshcore.projectPointOnCurve(53, 245)
hexamshcore.projectPointOnCurve(53, 250)
hexamshcore.projectPointOnCurve(53, 268)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([53, 145, 146, 147, 150, 153, 152, 151, 81, 128])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(147, 349)
hexamshcore.projectPointOnCurve(147, 475)
hexamshcore.projectPointOnCurve(147, 352)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([147, 150, 153, 162, 161, 160])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(11, 375)
hexamshcore.projectPointOnCurve(11, 373)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(11, 458)
hexamshcore.projectPointOnCurve(11, 471)

# --- splitVolumeBy4Points ---
hexamshcore.splitVolumeBy4Points(166, 165, 164, 163)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(10, 401)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([170, 11, 10, 173])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([12, 169, 170, 11])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(9, 404)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([9, 174, 169, 12])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([174, 9, 10, 173])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(173, 467)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([170, 166, 175, 173])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(174, 460)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([176, 174, 169, 165])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([175, 173, 174, 176, 59, 66])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(17, 34)
hexamshcore.projectPointOnCurve(17, 118)
hexamshcore.projectPointOnCurve(17, 65)
hexamshcore.projectPointOnCurve(17, 77)
hexamshcore.projectPointOnCurve(17, 151)
hexamshcore.projectPointOnCurve(17, 92)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([17, 177, 178, 179, 180, 181, 182, 76, 122, 174])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(18, 629)
hexamshcore.projectPointOnCurve(18, 625)
hexamshcore.projectPointOnCurve(18, 611)
hexamshcore.projectPointOnCurve(18, 612)
hexamshcore.projectPointOnCurve(18, 639)
hexamshcore.projectPointOnCurve(18, 616)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([18, 187, 188, 189, 190, 191, 192, 75, 121, 173])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(147, 346)
hexamshcore.projectPointOnCurve(147, 480)
hexamshcore.projectPointOnCurve(147, 351)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([147, 150, 153, 199, 198, 197])

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(197, 32)
hexamshcore.projectPointOnCurve(197, 66)
hexamshcore.projectPointOnCurve(197, 567)
hexamshcore.projectPointOnCurve(197, 67)
hexamshcore.projectPointOnCurve(197, 374)
hexamshcore.projectPointOnCurve(197, 49)
hexamshcore.projectPointOnCurve(197, 73)
hexamshcore.projectPointOnCurve(197, 379)
hexamshcore.projectPointOnCurve(197, 72)
hexamshcore.projectPointOnCurve(197, 68)
hexamshcore.projectPointOnCurve(197, 69)
hexamshcore.projectPointOnCurve(197, 71)
hexamshcore.projectPointOnCurve(197, 284)
hexamshcore.projectPointOnCurve(197, 286)
hexamshcore.projectPointOnCurve(197, 70)
hexamshcore.projectPointOnCurve(197, 367)
hexamshcore.projectPointOnCurve(197, 584)
hexamshcore.projectPointOnCurve(197, 487)
hexamshcore.projectPointOnCurve(197, 368)

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([199, 213, 210, 214, 211, 208, 207, 206, 197, 198])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop([218, 217, 215, 20, 169, 119, 73])

# --- splitVolumeByPointLoop ---
hexamshcore.splitVolumeByPointLoop(
    [218, 212, 213, 210, 209, 203, 201, 205, 204, 202, 200, 215, 216, 217]
)

# --- projectPointOnCurve ---
hexamshcore.projectPointOnCurve(19, 74)
hexamshcore.projectPointOnCurve(19, 279)

# --- splitVolumeBy4Points ---
hexamshcore.splitVolumeBy4Points(19, 74, 233, 232)

# --- removeSurface ---
hexamshcore.removeSurface(772)

# --- removeCurve ---
hexamshcore.removeCurve(893)

# --- meshCAD ---
hexamshcore.initializeMesh()

# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(455, 10)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(262, 3)
hexamshcore.setNumberOfNodesOnEdge(249, 3)
hexamshcore.setNumberOfNodesOnEdge(269, 3)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(54, 10)


# --- setNumberOfNodesOnEdge ---
hexamshcore.setNumberOfNodesOnEdge(287, 2)


# --- finally mesh ---
hexamshcore.meshCAD(first_mesh=False)
hexamshcore.writeMesh()

gmsh.finalize()

end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
