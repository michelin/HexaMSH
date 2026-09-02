from pathlib import Path


def remove_ref_msh_files(root: Path) -> int:
    removed = 0
    for file_path in root.rglob("*_ref.msh"):
        if file_path.is_file():
            file_path.unlink()
            removed += 1
    return removed


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    count = remove_ref_msh_files(base_dir)
    print(f"Removed {count} *_ref.msh file(s)")
