"""Serving's commit (verity_vllm.commit.serving_rows) against M0's own staging code (verity_flock.circuit at e51e2b86, read-only)
on the same rows and salts: every b || c, every root, and M0's pub/inst files byte for byte.  M0's statement binds each port's
domain to the input set; here its identity_digest is pointed at serving's agreed domain rule, and its stage_salts at serving's
salts, so M0's code computes everything else itself.
usage: m0_equal.py SET_DIR CIRCUIT_TXT PARTITION_JSON OUT_DIR [N] [--window WINDOW_DIR --index-json]"""
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
import verity.commitments.identity as ID
from verity_numerical.bench.input_sets import InputSet
from verity_flock import circuit as C
from verity_vllm.commit import serving_rows as SR

set_dir, circ, part_file, out = sys.argv[1:5]
s = InputSet.open(set_dir)
n = int(sys.argv[5]) if len(sys.argv) > 5 else s.n
text = Path(circ).read_text()
part = json.loads(Path(part_file).read_text())
run = "m0-equal/" + s.name
win = SR.Window(part["partition"], part["partition_digest"], n, run)
rows = {p: np.asarray(s.port(p, 0, n), dtype=np.uint16).reshape(n, -1) for p in SR.IN_PORTS}
outw = np.asarray(s.port("out", 0, n), dtype=np.uint16).reshape(n, -1)
t = time.perf_counter()
c = SR.commit(win, rows, outw, salt_key=None, workers=8)
t_serv = time.perf_counter() - t
SR.write(c, Path(out) / "window", {"row": 101, "run": run}, SR.index_doc([], run))
mine = SR.m0_files(Path(out) / "window", text, Path(out) / "serving", s.subcircuit.id)

salts = {p: [c.salts[p][i * 192:(i + 1) * 192] for i in range(n)] for p in SR.IN_PORTS}
orig = ID.identity_digest
def served_binding(tag, doc):
    if tag == "verity/flock-ir-frame/binding/v1":
        return c.domains[doc["port"]].binding.hex()
    return orig(tag, doc)
ID.identity_digest = served_binding
C.stage_salts = lambda input_set, lo, hi, ports, key: salts
t = time.perf_counter()
Path(out, "m0").mkdir(parents=True, exist_ok=True)
C.write(text, s, 0, n, Path(out) / "m0" / f"inst-{n}.bin", Path(out) / "m0" / f"pub-{n}.bin")
t_m0 = time.perf_counter() - t
ID.identity_digest = orig

res = {"n": n, "serving_s": round(t_serv, 3), "m0_s": round(t_m0, 3), "roots": {p: r.hex() for p, r in c.roots.items()}}
for kind in ("pub", "inst"):
    a = Path(out, "serving", f"{kind}-{n}.bin").read_bytes(); b = Path(out, "m0", f"{kind}-{n}.bin").read_bytes()
    ha, ba = a.split(b"\n", 1); hb, bb = b.split(b"\n", 1)
    ha, hb = json.loads(ha), json.loads(hb)
    diff = sorted(k for k in set(ha) | set(hb) if ha.get(k) != hb.get(k))
    res[kind] = {"body_equal": ba == bb, "body_bytes": len(ba), "body_sha512": hashlib.sha512(ba).hexdigest(),
                 "header_fields_differing": diff, "frame_v3_equal": ha["frame_v3"] == hb["frame_v3"],
                 "units_equal": ha["units"] == hb["units"], "circuit_sha512_equal": ha["circuit_sha512"] == hb["circuit_sha512"]}
res["ok"] = all(res[k]["body_equal"] and res[k]["frame_v3_equal"] and res[k]["units_equal"] and res[k]["circuit_sha512_equal"]
                and set(res[k]["header_fields_differing"]) <= {"set", "content_digest"} for k in ("pub", "inst"))
print(json.dumps(res, indent=1))
