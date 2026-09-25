#!/usr/bin/env python3
"""blake3-80gb: re-register measured points whose proof trees were published with manifest.json at the tree root (main's
reverify reads <tree>/proofs/manifest.json; verify-night-2 1030Z / 1100Z).  No re-proving: each old point dir (on this pod) is
hard-linked into the new run dir, published as a run-files/v1 tree holding proofs/ + result.json + bench.log, and its
result.json is re-published as a bench-result/v1 whose ref run_files is that tree.
Usage: 55-reregister.py RUN_DIR LANE POINT_DIR...   (the old ids come from the pod store's attempt record of each point's run)
"""
import json
import subprocess
import sys
from pathlib import Path

STORE = Path("/workspace/research/store/attempts")
rd, lane = Path(sys.argv[1]), sys.argv[2]
outs = []
for arg in sys.argv[3:]:
    src = Path(arg.rstrip("/"))
    assert (src / "proofs" / "manifest.json").is_file() and (src / "proofs" / "rep1").is_dir(), src
    run_id, tag, pdir = src.parts[-3], src.parts[-2], src.parts[-1]
    old = json.loads((STORE / f"{run_id}.json").read_text())["outputs"]
    key = f"{tag}-p{pdir.split('-')[0][1:]}"
    e = {"result": old[key], "tree": old[key + "-proofs"]}
    dst = rd / "points" / run_id / tag / pdir
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-al", str(src), str(dst)], check=True)
    meta = json.loads((dst / "result.json").read_text())
    point = meta.get("sweep", {}).get("point")
    plateau = bool(meta.get("sweep", {}).get("plateau"))
    name = f"{run_id}-{tag}-{pdir}"
    meta.update(lane=lane, tag=f"{run_id}/{tag}/{pdir}",
                label=f"{lane} {tag} sweep point {point} ({pdir}){' PLATEAU' if plateau else ''} [proofs/ layout]",
                reregistered={"from_result": e["result"], "from_tree": e["tree"], "measured_by": run_id,
                              "reason": "proof tree re-published with proofs/manifest.json (main reverify layout); proofs unchanged"})
    outs.append({"name": name + "-proofs", "kind": "run-files/v1", "tree": str(dst.relative_to(rd)),
                 "meta": {"lane": lane, "tag": f"{run_id}/{tag}/{pdir}", "label": f"{lane} {tag} {pdir} proof dump (proofs/ layout)",
                          "reregistered_from": e["tree"]}})
    outs.append({"name": name, "kind": "bench-result/v1", "meta": meta, "refs": {"run_files": "@" + name + "-proofs"}})
(rd / "outputs.json").write_text(json.dumps({"schema": "research/outputs/v0.1", "outputs": outs}, indent=1, default=str))
print(f"outputs.json: {len(outs)} entries: {[o['name'] for o in outs]}")
