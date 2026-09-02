"""Test suite for hexamsh: validates mesh generation against reference outputs."""

import math
import os
import shutil
import subprocess
import sys
import time
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
    """Load mesh from file and extract nodes and elements."""
    gmsh.clear()
    gmsh.open(str(filename))

    # ---- Nodes ----
    _, coords, _ = gmsh.model.mesh.getNodes()
    nodes = [
        (coords[i], coords[i + 1], coords[i + 2]) for i in range(0, len(coords), 3)
    ]

    # ---- Elements ----
    _, elem_tags, elem_node_tags = gmsh.model.mesh.getElements()

    elements = []
    for etype_nodes in elem_node_tags:
        # each element = block of N nodes
        # transform to sorted tuple to ignore orientation
        # dynamic chunk → depends on element type
        # infer from first block
        # gmsh returns flattened → we cut into fixed chunks
        # -> safer: get size via element type
        # but here robust simplification:

        chunk_size = None

        # guess size by looking at length / number of elements
        # robust fallback
        if len(elem_tags) > 0 and len(elem_tags[0]) > 0:
            n_elem = len(elem_tags[0])
            chunk_size = len(etype_nodes) // n_elem

        if chunk_size is None or chunk_size == 0:
            continue

        for i in range(0, len(etype_nodes), chunk_size):
            elem = tuple(sorted(etype_nodes[i : i + chunk_size]))
            elements.append(elem)

    return nodes, elements


def dist(p1, p2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def compare_nodes(nodes1, nodes2, tol):
    """
    Compare node positions between two meshes with geometric matching.
    Order-independent and tolerant.
    """

    nodes1 = sorted(nodes1)
    nodes2 = sorted(nodes2)

    if len(nodes1) != len(nodes2):
        print(f"[DIFF] nodes count: {len(nodes1)} vs {len(nodes2)}")
        return False

    # On travaille avec une copie modifiable
    unmatched = list(nodes2)

    for n1 in nodes1:
        found = False

        for i, n2 in enumerate(unmatched):
            if dist(n1, n2) < tol:
                # match trouvé → on enlève ce nœud pour éviter double usage
                unmatched.pop(i)
                found = True
                break

        if not found:
            print(f"[DIFF] node not found: {n1}")
            return False

    return True


def compare_elements(elems1, elems2):
    """Compare element connectivity between two meshes."""
    if len(elems1) != len(elems2):
        print(f"[DIFF] elements count: {len(elems1)} vs {len(elems2)}")
        return False

    # comparer comme ensembles
    set1 = set(elems1)
    set2 = set(elems2)

    if set1 != set2:
        missing = set1 - set2
        extra = set2 - set1
        print("[DIFF] element connectivity mismatch")
        if missing:
            print(f"  in file A but not in B ({len(missing)}):")
            for elem in list(missing)[:10]:
                print(f"    {elem}")
            if len(missing) > 10:
                print(f"    ... and {len(missing) - 10} more")
        if extra:
            print(f"  in file B but not in A ({len(extra)}):")
            for elem in list(extra)[:10]:
                print(f"    {elem}")
            if len(extra) > 10:
                print(f"    ... and {len(extra) - 10} more")
        return False

    return True


def compare_meshes(file_a: Path, file_b: Path) -> bool:
    """Compare two mesh files for node and element equality."""
    nodes1, elems1 = load_mesh(file_a)
    nodes2, elems2 = load_mesh(file_b)

    ok_nodes = compare_nodes(nodes1, nodes2, NODE_TOL)
    ok_elems = compare_elements(elems1, elems2)

    return ok_nodes and ok_elems


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
