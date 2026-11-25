"""Test suite for hexamsh: validates mesh generation against reference outputs."""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import gmsh


# ========================
# UTILS
# ========================
def load_mesh(filename):
    """Load volume element count and types from a mesh file."""
    gmsh.clear()
    gmsh.open(str(filename))

    element_types, element_tags, _ = gmsh.model.mesh.getElements(dim=3)
    element_count = sum(len(tags) for tags in element_tags)
    type_names = [
        gmsh.model.mesh.getElementProperties(element_type)[0]
        for element_type in element_types
    ]
    return element_count, type_names


def compare_meshes(file_a: Path, file_b: Path) -> bool:
    """Compare volume element counts and ensure both meshes contain only hexahedra."""
    count_a, types_a = load_mesh(file_a)
    count_b, types_b = load_mesh(file_b)

    if count_a != count_b:
        print(f"[DIFF] elements count: {count_a} vs {count_b}")
        return False

    if count_a == 0:
        print("[DIFF] no volume elements found")
        return False

    for filename, element_types in ((file_a, types_a), (file_b, types_b)):
        for element_type in element_types:
            if not element_type.startswith("Hexahedron"):
                print(f"[DIFF] non-hexahedral element in {filename}: {element_type}")
                return False

    return True


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
