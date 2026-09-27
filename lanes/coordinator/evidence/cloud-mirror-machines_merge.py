#!/usr/bin/env python3
"""Merge two machines.d directories by each registration's `registered_at` (never by file mtime): for every <machine>.toml, the
copy with the later registered_at wins and is written into both directories.  A file only one side has is copied to the other.
Prints `<name> -> store|pod` for every copy made.  Usage: machines_merge.py STORE_DIR POD_DIR"""
from __future__ import annotations

import re
import sys
from pathlib import Path

AT = re.compile(r'^registered_at\s*=\s*"([^"]*)"', re.M)


def stamp(p: Path) -> str:
    """registered_at (ISO, sortable), or '' when the file has none (an older registration format loses to any stamped one)."""
    m = AT.search(p.read_text(errors="replace"))
    return m.group(1) if m else ""


def merge(store: Path, pod: Path) -> list[str]:
    out = []
    for name in sorted({p.name for d in (store, pod) for p in d.glob("*.toml")}):
        s, p = store / name, pod / name
        if s.exists() and p.exists():
            if s.read_bytes() == p.read_bytes():
                continue
            src, dst, where = (s, p, "pod") if stamp(s) >= stamp(p) else (p, s, "store")
        else:
            src, dst, where = (s, p, "pod") if s.exists() else (p, s, "store")
        dst.write_bytes(src.read_bytes())
        out.append(f"{name} -> {where}")
    return out


if __name__ == "__main__":
    for line in merge(Path(sys.argv[1]), Path(sys.argv[2])):
        print(line)
