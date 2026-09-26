import json, subprocess, sys, time
from pathlib import Path
from backends.direct.ligero.relations import relation
from backends.direct.ligero import hashchain, protocol
from backends.direct.ligero.serialize import system_bytes
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
V = "backends/ligero-verify/target/release/ligero-verify"
rows = []
for base in ("bf16-ampere-x4", "bf16-hopper-x4", "fp8-ada-x4", "fp8-hopper-x4"):
    for K in (2048, 8192):
        for leaf in sys.argv[2].split(","):
            rel = relation(f"{base}-k{K}")
            t0 = time.time()
            hr = hashchain.compose(rel, leaf)
            d = out / f"{rel.name}+{leaf}"; d.mkdir(exist_ok=True)
            (d / "system.bin").write_bytes(system_bytes(hr.sys))
            r = subprocess.run([V, "system-digest", "--system", str(d / "system.bin")], capture_output=True, text=True, check=True)
            dg = json.loads(r.stdout)
            assert dg["sys_id"] == protocol.system_id(hr.sys).hex()
            row = {"relation": rel.name, "leaf": leaf, "sys_id": dg["sys_id"], "table_digest": dg["table_digest"], "rows": hr.sys.m,
                   "digest_elems": hr.leaf.digest_elems, "n_chunks_max": getattr(hr.leaf, "n_chunks_max", None),
                   "pinned_relation": dg.get("pinned_relation"), "seconds": round(time.time() - t0, 1)}
            print(json.dumps(row), flush=True); rows.append(row)
(out / "pins.json").write_text(json.dumps(rows, indent=1))
