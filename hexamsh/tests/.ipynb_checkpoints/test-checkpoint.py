import difflib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def compare_text_files(a: Path, b: Path) -> bool:
    txt_a = a.read_text(encoding="utf-8", errors="replace").splitlines()
    txt_b = b.read_text(encoding="utf-8", errors="replace").splitlines()
    if txt_a == txt_b:
        return True

    print(f"[DIFF] {a.parent}")
    return False


def main() -> None:
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
            print(f"[SKIP] {d} (multiple *.msh found: {[p.name for p in msh_files]})")
            skip_count += 1
            continue

        msh = msh_files[0]
        ref = msh.with_name(f"{msh.stem}_ref{msh.suffix}")
        test_start = time.perf_counter()

        shutil.copy2(msh, ref)

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
            print(f"[ERROR] {d} (replay.py failed with exit code {e.returncode})")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            print(f"[TIME] {d} ({time.perf_counter() - test_start:.3f}s)")
            ko_count += 1
            continue

        if not msh.exists():
            print(f"[ERROR] {d} ({msh.name} not generated)")
            print(f"[TIME] {d} ({time.perf_counter() - test_start:.3f}s)")
            ko_count += 1
            continue

        if compare_text_files(ref, msh):
            print(f"[OK] {d}")
            ok_count += 1
        else:
            ko_count += 1

        print(f"[TIME] {d} ({time.perf_counter() - test_start:.3f}s)")

    print(f"\nResult: OK={ok_count}, KO={ko_count}, SKIP={skip_count}")

    if ko_count > 0:
        sys.exit(1)  # fail CI job


if __name__ == "__main__":
    main()
