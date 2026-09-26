"""verify-bligero-real-k: non-producer check of the 16 real-K PINS rows in backends/ligero-verify/src/leaf.rs.

Compiles every (<fold>-k<K>, leaf) system from this checkout, digests it with this checkout's release ligero-verify,
and compares against (a) the PINS rows parsed from leaf.rs source text, (b) the binary's own pin lookup
(pinned_relation), (c) Python's protocol.system_id, (d) the Rust at_k! steps/tag vs Python's relation, and finally
(e) the producer's pins-vm-compile.json as a third reading.  Usage: python pins_check.py OUT [producer.json]
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

from backends.direct.ligero.relations import relation, REAL_KS
from backends.direct.ligero import hashchain, protocol
from backends.direct.ligero.serialize import system_bytes

ROOT = Path.cwd()
V = Path(os.environ.get("VBRK_VERIFIER") or ROOT / "backends/ligero-verify/target/release/ligero-verify")
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
producer = {(r["relation"], r["leaf"]): r for r in json.loads(Path(sys.argv[2]).read_text())} if len(sys.argv) > 2 else {}

leaf_rs = (ROOT / "backends/ligero-verify/src/leaf.rs").read_text()
pins_block = leaf_rs[leaf_rs.index("pub static PINS"):]
pins_block = pins_block[:pins_block.index("];")]
row_re = re.compile(r'\("([^"]+)",\s*"([^"]+)",\s*"([0-9a-f]{64})",\s*"([0-9a-f]{64})"\)', re.S)
pins = {}
for r, l, s, t in row_re.findall(pins_block):
    assert (r, l) not in pins, f"duplicate PINS row {(r, l)}"
    pins[(r, l)] = (s, t)

rel_rs = (ROOT / "backends/ligero-verify/src/relation.rs").read_text()
atk = {m[0]: (m[1], m[2]) for m in re.findall(r'at_k!\("([^"]+)",\s*\w+,\s*b"([^"]*)",\s*(\d+)\)', rel_rs)}

FOLDS = ("bf16-ampere-x4", "bf16-hopper-x4", "fp8-ada-x4", "fp8-hopper-x4")
LEAVES = ("blake3-xob", "sha256")
assert tuple(REAL_KS) == (2048, 8192), REAL_KS
rows, bad = [], []
for fold in FOLDS:
    for K in REAL_KS:
        rel = relation(f"{fold}-k{K}")
        tag_rs, steps_rs = atk[rel.name]
        steps_py = rel.vu_k // rel.k
        for leaf in LEAVES:
            t0 = time.time()
            hr = hashchain.compose(rel, leaf)
            d = out / f"{rel.name}+{leaf}"; d.mkdir(exist_ok=True)
            sb = system_bytes(hr.sys)
            (d / "system.bin").write_bytes(sb)
            dg = json.loads(subprocess.run([str(V), "system-digest", "--system", str(d / "system.bin")],
                                           capture_output=True, text=True, check=True).stdout)
            pin = pins.get((rel.name, leaf))
            prod = producer.get((rel.name, leaf))
            checks = {
                "pin_row_present": pin is not None,
                "sys_id_eq_pin": pin is not None and dg["sys_id"] == pin[0],
                "table_digest_eq_pin": pin is not None and dg["table_digest"] == pin[1],
                "binary_pinned_relation": dg["pinned_relation"] == f"{rel.name}+{leaf}",
                "python_system_id": protocol.system_id(hr.sys).hex() == dg["sys_id"],
                "rust_steps_eq_K_over_k": int(steps_rs) == steps_py == K // rel.k,
                "rust_tag_eq_python": tag_rs.encode() == rel.tag,
                "producer_json_eq": prod is None or (prod["sys_id"], prod["table_digest"]) == (dg["sys_id"], dg["table_digest"]),
            }
            row = {"relation": rel.name, "leaf": leaf, "K": K, "k": rel.k, "steps": steps_py, "m": dg["m"],
                   "sys_id": dg["sys_id"], "table_digest": dg["table_digest"], "pinned_relation": dg["pinned_relation"],
                   "system_bytes": len(sb), "seconds": round(time.time() - t0, 1), "checks": checks,
                   "ok": all(checks.values())}
            print(json.dumps({k: row[k] for k in ("relation", "leaf", "sys_id", "pinned_relation", "ok", "seconds")}), flush=True)
            rows.append(row)
            if not row["ok"]:
                bad.append((rel.name, leaf, [k for k, v in checks.items() if not v]))

real_k_pins = sorted(k for k in pins if re.search(r"-k(2048|8192)$", k[0]))
summary = {"checked": len(rows), "ok": sum(r["ok"] for r in rows), "bad": bad,
           "pins_rows_total": len(pins), "real_k_pin_rows": len(real_k_pins),
           "unchecked_real_k_pin_rows": [k for k in real_k_pins if k not in {(r["relation"], r["leaf"]) for r in rows}]}
(out / "pins-check.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
print(json.dumps(summary))
sys.exit(0 if not bad and len(rows) == 16 and not summary["unchecked_real_k_pin_rows"] else 1)
