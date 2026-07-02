#!/usr/bin/env python3
"""File PM Planning PDFs from ~/Downloads into references/client-docs/.

Finds every "*PM Planning*.pdf" in ~/Downloads and copies any that aren't
already filed into <project-root>/references/client-docs/. Copies (never
moves or deletes) — the Downloads original is untouched. Idempotent: run
it as many times a day as you like.

Usage:
    python3 scripts/file_pm_planning.py            # file anything new
    python3 scripts/file_pm_planning.py --dry-run  # show what would happen

Authorized by D-017 (utility script, non-money-touching, Micro-app rigor).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

DOWNLOADS = Path.home() / "Downloads"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEST = PROJECT_ROOT / "references" / "client-docs"
PATTERN = "*PM Planning*.pdf"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report without copying")
    args = parser.parse_args()

    if not DOWNLOADS.is_dir():
        print(f"ERROR: Downloads folder not found at {DOWNLOADS}", file=sys.stderr)
        return 1
    DEST.mkdir(parents=True, exist_ok=True)

    candidates = sorted(DOWNLOADS.glob(PATTERN))
    if not candidates:
        print(f"No files matching '{PATTERN}' in {DOWNLOADS}. Nothing to do.")
        return 0

    already = {p.name for p in DEST.glob("*.pdf")}
    new = [p for p in candidates if p.name not in already]

    if not new:
        print(f"Checked {len(candidates)} matching file(s) — all already filed. Nothing to do.")
        return 0

    for src in new:
        if args.dry_run:
            print(f"would file: {src.name}")
        else:
            shutil.copy2(src, DEST / src.name)
            print(f"filed: {src.name}")

    verb = "Would file" if args.dry_run else "Filed"
    print(f"{verb} {len(new)} new PDF(s) -> {DEST.relative_to(PROJECT_ROOT)}/ "
          f"({len(candidates) - len(new)} already present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
