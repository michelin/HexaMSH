"""Test suite for hexamsh: validates mesh generation against reference outputs."""

import math
import os
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import gmsh

# ========================
# CONFIG
# ========================
NODE_TOL = 1e-3


# ========================
# UTILS
# ========================
def load_mesh(filename):
    """Load node coordinates and element connectivity from a mesh file."""
    gmsh.clear()
    gmsh.open(str(filename))

    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    nodes = {
        int(tag): tuple(float(coords[3 * i + j]) for j in range(3))
        for i, tag in enumerate(node_tags)
    }

    element_types, _, element_node_tags = gmsh.model.mesh.getElements()
    elements = []
    for element_type, connectivity in zip(element_types, element_node_tags):
        node_count = gmsh.model.mesh.getElementProperties(element_type)[3]
        for i in range(0, len(connectivity), node_count):
            elements.append(
                (
                    int(element_type),
                    tuple(int(tag) for tag in connectivity[i : i + node_count]),
                )
            )

    return nodes, elements


def dist(p1, p2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def match_nodes(nodes1, nodes2, tol):
    """Map node tags in the second mesh to geometrically matching tags in the first."""
    if len(nodes1) != len(nodes2):
        print(f"[DIFF] nodes count: {len(nodes1)} vs {len(nodes2)}")
        return None

    unmatched = sorted((point, tag) for tag, point in nodes2.items())
    node_map = {}

    for tag1, point1 in sorted(nodes1.items(), key=lambda item: item[1]):
        for match_index, (point2, tag2) in enumerate(unmatched):
            if dist(point1, point2) < tol:
                node_map[tag2] = tag1
                unmatched.pop(match_index)
                break
        else:
            print(f"[DIFF] node not found: {point1}")
            return None

    return node_map


def compare_elements(elems1, elems2, node_map):
    """Compare element type and connectivity without relying on tags or ordering."""
    mapped_elems2 = []
    for element_type, connectivity in elems2:
        if any(tag not in node_map for tag in connectivity):
            print("[DIFF] element references an unmatched node")
            return False
        mapped_elems2.append(
            (element_type, tuple(sorted(node_map[tag] for tag in connectivity)))
        )

    expected = Counter(
        (element_type, tuple(sorted(connectivity)))
        for element_type, connectivity in elems1
    )
    actual = Counter(mapped_elems2)

    if expected != actual:
        print("[DIFF] element connectivity mismatch")
        missing = expected - actual
        extra = actual - expected
        if missing:
            print(f"  in file A but not in B ({sum(missing.values())}):")
            for elem, count in list(missing.items())[:10]:
                print(f"    {elem}" + (f" (x{count})" if count > 1 else ""))
        if extra:
            print(f"  in file B but not in A ({sum(extra.values())}):")
            for elem, count in list(extra.items())[:10]:
                print(f"    {elem}" + (f" (x{count})" if count > 1 else ""))
        return False

    return True


def compare_meshes(file_a: Path, file_b: Path) -> bool:
    """Compare node positions and element connectivity in two mesh files."""
    nodes1, elems1 = load_mesh(file_a)
    nodes2, elems2 = load_mesh(file_b)

    node_map = match_nodes(nodes1, nodes2, NODE_TOL)
    if node_map is None:
        return False
    return compare_elements(elems1, elems2, node_map)


# ========================
# MAIN
# ========================
def main() -> None:
    """Execute test suite against all replay test cases."""
    gmsh.initialize()

    root = Path(__file__).resolve().parent
    ok_count, ko_count, skip_count = 0, 0, 0

    for folder, _, _ in os.walk(root):
        d = Path(folder)

        replay = d / "replay.py"
        if not replay.exists():
            continue

        msh_files = [p for p in d.glob("*.msh") if not p.name.endswith("_ref.msh")]

        if not msh_files:
            print(f"[SKIP] {d} (*.msh not found)")
            skip_count += 1
            continue

        if len(msh_files) > 1:
            print(f"[SKIP] {d} (multiple meshes)")
            skip_count += 1
            continue

        msh = msh_files[0]
        ref = msh.with_name(f"{msh.stem}_ref{msh.suffix}")

        test_start = time.perf_counter()

        # sauvegarde ref
        shutil.copy2(msh, ref)

        # regen mesh
        try:
            subprocess.run(
                [sys.executable, str(replay)],
                cwd=d,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {d} replay failed")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            ko_count += 1
            continue

        if not msh.exists():
            print(f"[ERROR] {d} mesh not generated")
            ko_count += 1
            continue

        elapsed = time.perf_counter() - test_start

        if compare_meshes(ref, msh):
            print(f"[OK] {d.name} ({elapsed:.3f}s)")
            ok_count += 1
        else:
            print(f"[KO] {d.name} ({elapsed:.3f}s)")
            ko_count += 1

    gmsh.finalize()

    print(f"\nResult: OK={ok_count}, KO={ko_count}, SKIP={skip_count}")

    if ko_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
