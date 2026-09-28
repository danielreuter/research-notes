"""row_digests.py ROW_DIR --out JSON --markdown MD: `rebaseline digests` (PR #243, verity-vllm/rebaseline-digests/v1) for trees that lack it.
The functions below are #243's `_doc`, `_partition_digests`, `row_digests` and `digests`, copied unchanged (read-only: nothing is written
into the row dir).  epoch_row.sh uses the tree's own `rebaseline digests` when it exists."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any



def _doc(p: Path) -> dict:
    return json.loads(p.read_text()) if p.is_file() else {}


def _partition_digests(part: Any) -> list[str]:
    """Every partition digest a manifest's `query.partition` names: one `{object, digest}`, or `by_component` / `by_rank` of them."""
    if not isinstance(part, dict):
        return []
    if "object" in part:
        return [part["digest"]]
    return sorted(d for k in ("by_component", "by_rank") for v in (part.get(k) or {}).values() for d in _partition_digests(v))


def row_digests(d: Path) -> dict[str, Any]:
    """One row's digests from its run directory (`$SWEEP_DIR/<row>/`, row_pod.sh / tp_stage.sh's layout; a TP row's Builds under
    build/rank<r>/)."""
    ranks: dict[str, dict] = {}
    for bs in [d / "build_summary.json", *sorted(d.glob("build/rank*/build_summary.json"))]:
        s = _doc(bs)
        if s:
            ranks[bs.parent.name.removeprefix("rank") if bs.parent != d else "0"] = {
                "step": (s.get("step") or {}).get("program_digest"), "workload": (s.get("workload") or {}).get("workload_digest"),
                "requests": {k: v.get("program_digest") for k, v in sorted(s.items())
                             if (k == "request" or k.startswith("build_request")) and isinstance(v, dict)}}
    man, vd = _doc(d / "manifest.json"), _doc(d / "verdict.json")
    q = man.get("query") or {}
    return {"row": d.name, "programs": ranks, "manifest_digest": man.get("manifest_digest"), "program_digest": man.get("program_digest"),
            "query_id": q.get("query_id"), "partition_digests": _partition_digests(q.get("partition")),
            "run_roots": list(vd.get("run_roots") or []), "verdict": vd.get("outcome")}


def digests(a) -> int:
    rows = [row_digests(Path(d)) for d in a.row_dirs]
    doc = {"schema": "verity-vllm/rebaseline-digests/v1", "rows": rows}
    text = json.dumps(doc, indent=1) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    md = ["| row | verdict | step (rank 0) | workload (rank 0) | requests | manifest | partitions | run roots |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        p0 = r["programs"].get("0") or {}
        short = lambda x: (x or "-")[:16]                                   # noqa: E731
        md.append(f"| {r['row']} | {r['verdict'] or '-'} | {short(p0.get('step'))} | {short(p0.get('workload'))} | {len(p0.get('requests') or {})} "
                  f"| {short(r['manifest_digest'])} | {len(r['partition_digests'])} | {', '.join(x[:16] for x in r['run_roots']) or '-'} |")
    if a.markdown:
        Path(a.markdown).write_text("\n".join(md) + "\n")
    print(text if not a.out else "\n".join(md))
    return 0 if all(r["programs"] and r["manifest_digest"] for r in rows) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("row_dirs", nargs="+")
    ap.add_argument("--out", default=None)
    ap.add_argument("--markdown", default=None)
    sys.exit(digests(ap.parse_args()))
