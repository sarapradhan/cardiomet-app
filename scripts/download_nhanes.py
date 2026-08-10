"""
scripts/download_nhanes.py — Downloads NHANES 2017-2018 XPT files.

Source: CDC NHANES public data files (2017-2018 cycle, suffix _J).
URL scheme: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/<FILE>.XPT
Variable reference: docs/DATA_DICTIONARY.md

Each download is validated as a real XPORT file (not an HTML error page) before
it is kept — the older /Nchs/Nhanes/2017-2018/ path now returns a 200 HTML
"Page Not Found", so a naive download silently saves garbage.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles"
DEST = Path(__file__).resolve().parent.parent / "data" / "raw"

# XPORT files begin with this exact ASCII header record.
_XPORT_MAGIC = b"HEADER RECORD*******LIBRARY HEADER RECORD"

FILES = {
    "DEMO_J.XPT":   "SEQN, RIDAGEYR, RIAGENDR, RIDRETH3, WTMEC2YR",
    "TCHOL_J.XPT":  "LBXTC",
    "HDL_J.XPT":    "LBDHDD",
    "TRIGLY_J.XPT": "LBDLDL, LBXTR",
    "GHB_J.XPT":    "LBXGH (HbA1c - required)",
    "GLU_J.XPT":    "LBXGLU",
    "FASTQX_J.XPT": "PHAFSTHR (fasting hours)",
    "BPX_J.XPT":    "BPXOSY1-3, BPXODI1-3",
    "BMX_J.XPT":    "BMXBMI",
    "BPQ_J.XPT":    "BPQ050A, BPQ090D",
    "DIQ_J.XPT":    "DIQ050, DIQ070",
}


def _is_valid_xport(path: Path) -> bool:
    """True if the file starts with the XPORT library header record."""
    try:
        with open(path, "rb") as fh:
            return fh.read(len(_XPORT_MAGIC)) == _XPORT_MAGIC
    except OSError:
        return False


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    for fname, variables in FILES.items():
        dest = DEST / fname
        if dest.exists() and _is_valid_xport(dest):
            print(f"  SKIP (valid, exists): {fname}")
            continue

        url = f"{BASE}/{fname}"
        print(f"  Downloading {fname}  [{variables}]")
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as exc:  # noqa: BLE001
            print(f"    ERROR: {exc}")
            errors.append(fname)
            continue

        if not _is_valid_xport(dest):
            print("    ERROR: not a valid XPORT file (HTML/error page?)")
            dest.unlink(missing_ok=True)
            errors.append(fname)
            continue

        print(f"    Saved: {dest} ({dest.stat().st_size // 1024} KB)")

    print()
    if errors:
        print(f"Failed: {', '.join(errors)}")
        print("The app still runs in demo mode without these files (deterministic synthetic cohort).")
        return 1
    print(f"All files saved to {DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
