#!/usr/bin/env python3
"""(from b-ligero-sha256 / blake3-80gb) write $RESEARCH_RUN_DIR/outputs.json (research/outputs/v0.1) for every sweep under the run dir, so the runner
publishes each sweep point as a bench-result/v1 output of the attempt (the plateau point with ref run_files = its proof tree:
rep1 + system.bin + manifest + the pod's Rust producer check).  Usage: 50-outputs.py RUN_DIR LANE
"""
import json
import sys
from pathlib import Path

rd, lane = Path(sys.argv[1]), sys.argv[2]
outs = []
for sj in sorted(rd.glob("*/sweep.json")):
    sw = json.loads(sj.read_text())
    tag = sj.parent.name
    for p in sw["points"]:
        rj = sj.parent / p["dir"] / "result.json"
        if p.get("vu_per_second") is None or not rj.is_file():
            continue
        meta = json.loads(rj.read_text())
        plateau = p["point"] == sw["plateau_point"]
        meta.update(lane=lane, tag=f"{tag}/{p['dir']}", label=f"{lane} {tag} sweep point {p['point']} ({p['total_vus']} VUs)"
                    + (" PLATEAU" if plateau else ""))
        name = f"{tag}-p{p['point']}"
        proofs = sj.parent / p["dir"] / "proofs"
        ent = {"name": name, "kind": "bench-result/v1", "meta": meta}
        if plateau and (proofs / "rep1").is_dir():
            outs.append({"name": name + "-proofs", "kind": "run-files/v1", "tree": str(proofs.relative_to(rd)),
                         "meta": {"lane": lane, "tag": f"{tag}/{p['dir']}/proofs", "label": f"{lane} {tag} plateau proof dump"}})
            ent["refs"] = {"run_files": "@" + name + "-proofs"}
        outs.append(ent)
for f in sorted((rd / "outputs").glob("instance-equiv-*.json")):
    doc = json.loads(f.read_text())
    doc.update(lane=lane)
    outs.append({"name": f.stem, "kind": "instance-equiv/v1", "file": str(f.relative_to(rd)), "meta": doc})
(rd / "outputs.json").write_text(json.dumps({"schema": "research/outputs/v0.1", "outputs": outs}, indent=1, default=str))
print(f"outputs.json: {len(outs)} entries: {[o['name'] for o in outs]}")
