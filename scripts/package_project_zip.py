"""Packages the entire GreenHope COP31 Investor Intelligence & KAG/RAG project into a clean downloadable ZIP archive."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ZIP_FILENAME = "greenhope_cop31_investor_ai_project.zip"
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "node_modules"}


def build_project_zip(output_path: Path | None = None) -> Path:
    dest = (output_path or (PROJECT_ROOT / ZIP_FILENAME)).resolve()
    tmp_dest = dest.with_suffix(".zip.tmp")

    file_count = 0
    with zipfile.ZipFile(tmp_dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
            for fname in sorted(files):
                fpath = Path(root) / fname
                if fpath.resolve() in {dest, tmp_dest} or fname.endswith(".pyc"):
                    continue
                arcname = Path("greenhope_cop31_investor_ai") / fpath.relative_to(PROJECT_ROOT)
                zf.write(fpath, arcname=str(arcname))
                file_count += 1

    tmp_dest.replace(dest)
    size_kb = dest.stat().st_size / 1024.0
    print(f"Packaged project ZIP -> {dest} ({file_count} files, {size_kb:.1f} KB)")
    return dest


if __name__ == "__main__":
    build_project_zip()
