"""Run C of the serving-commit GPU check, on the pod from run B's serving-rows window:
1. the served rows at the 1,024 captured #101 heads (art:16825154, run r20260925-233347-8515) equal the capture byte for byte;
2. M0's own write() (verity_flock.circuit at e51e2b86, read-only) over every served row, with serving's salts and domains, equals
   serving's pub-N.bin / inst-N.bin byte for byte (bodies, frame_v3, units, circuit pin);
3. the circuit M0 composes over the agreed partition has the pin the e2e lane named;
4. serving's overhead: the hook's seconds beside the Commit stage's wall.
usage: sc_compare.py WINDOW_DIR SET_DIR PARTITION_JSON OUT_DIR STAGES_TXT"""
import hashlib, json, os, sys, time
from pathlib import Path

import numpy as np
import verity.commitments.identity as ID
from verity_numerical.bench.input_sets import InputSet
from verity_flock import circuit as C
from verity_vllm.commit import serving_rows as SR

PIN = os.environ.get("EXPECT_PIN") or "cdcbd876d413897b9c9388750113305d6f492362c93a564f8e48baff9e96b4826c946e512cf34717ab5bc155e99cdb66fee93442e2fc2a1bfb609770a1be0de2"
wd, set_dir, part_file, out, stages = (Path(a) for a in sys.argv[1:6])
out.mkdir(parents=True, exist_ok=True)
res: dict = {}
win = json.loads((wd / "window.json").read_text())
rec = json.loads((wd / "registration.json").read_text())
idx = json.loads((wd / "index.json").read_text())
n = int(win["n"])
W = {p: w for p, w in win["ports"]}
ow = win["out_ports"][0][1]
priv = np.frombuffer((wd / "private.bin").read_bytes(), dtype=np.uint8)
row_b = 2 * sum(W.values())
rows = priv[:n * row_b].view("<u2").reshape(n, -1)
served = {"x": rows[:, :W["x"]], "cs": rows[:, W["x"]:]}
salts_all = priv[n * row_b:].reshape(n, len(W), SR.SALT_BYTES)
pub = np.frombuffer((wd / "public.bin").read_bytes(), dtype=np.uint8)
served["out"] = pub[n * len(W) * SR.BC_BYTES:].view("<u2").reshape(n, ow)

# 1. the captured heads
s = InputSet.open(str(set_dir))
cidx = json.loads((set_dir / "index.json").read_text())
col = {c: i for i, c in enumerate(cidx["columns"])}
by_key = {(e[2], int(e[3]), e[5], int(e[7]), int(e[1]) - int(e[0])): int(e[0]) for e in idx["rows"]}
units, missing = [], []
for r in cidx["rows"]:
    k = (r[col["request"]], int(r[col["engine_step"]]), r[col["op_path"]], int(r[col["row"]]), int(r[col["sub"]]["NHEADS"]))
    (units.append(by_key[k] + int(r[col["sub"]]["head"])) if k in by_key else missing.append(k))
cap = {p: np.asarray(s.port(p, 0, s.n), dtype=np.uint16).reshape(s.n, -1) for p in ("x", "cs", "out")}
eq = {p: (bool(np.array_equal(served[p][units], cap[p])) if not missing else False) for p in cap}
res["captured"] = {"n": s.n, "located": len(units), "missing": missing[:4], "equal": eq,
                   "bytes_compared": int(sum(cap[p].nbytes for p in cap)), "ok": not missing and all(eq.values())}

# 3. the circuit over the agreed partition
part = json.loads(part_file.read_text())
low = C.lowering_for_set(s)
text = C.compose(low, s.subcircuit, partition=part["partition_digest"], program=part["partition"]["program"])
res["circuit"] = {"pin": C.digest(text), "pin_agreed": C.digest(text) == PIN, "class": C.class_digest(text)}

# serving's own M0 files
t = time.perf_counter()
mine = SR.m0_files(wd, text, out / "serving", s.subcircuit.id)
res["m0_files_s"] = round(time.perf_counter() - t, 3)

# 2. M0's write() over the served rows with serving's salts and domains
class Served:
    name, content_digest, subcircuit = f"served/{rec['commitment']['source']['run']}", win["index_sha512"], s.subcircuit
    def port(self, p, lo, hi):
        return served[p][lo:hi]
salts = {p: [bytes(salts_all[i, k]) for i in range(n)] for k, p in enumerate(W)}
bind = {p: v for p, v in win["frame_v3"]["bindings"].items()}
orig = ID.identity_digest
ID.identity_digest = lambda tag, doc: bind[doc["port"]] if tag == "verity/flock-ir-frame/binding/v1" else orig(tag, doc)
C.stage_salts = lambda input_set, lo, hi, ports, key: salts
(out / "m0").mkdir(exist_ok=True)
t = time.perf_counter()
# M0's write() builds the prover body with np.concatenate inside its per-instance loop (quadratic in n: about an hour at
# 183,680).  Its public file comes from write() itself (path=None skips that loop); the prover file is write()'s header
# (its return value) and write()'s body expression with the concatenation hoisted, byte for byte the same.
head = C.write(text, Served(), 0, n, None, out / "m0" / f"pub-{n}.bin")
ports = [C.Port(nm, w) for nm, w, _ in json.loads(text.split("\n", 2)[1][5:])["ports"]]
cat = np.concatenate([served[p.name] for p in ports], axis=1).astype("<u2")
private = b"".join(cat[i].tobytes() for i in range(n)) + b"".join(salts[p.name][i] for i in range(n) for p in ports)
m0_pub_body = (out / "m0" / f"pub-{n}.bin").read_bytes().split(b"\n", 1)[1]
(out / "m0" / f"inst-{n}.bin").write_bytes(json.dumps(head, sort_keys=True).encode() + b"\n" + private + m0_pub_body)
res["m0_write_s"] = round(time.perf_counter() - t, 3)
res["m0_inst_note"] = "M0's write() prover body is quadratic in n; built here from write()'s header and its body expression, concatenation hoisted"
ID.identity_digest = orig
for kind in ("pub", "inst"):
    a = (out / "serving" / f"{kind}-{n}.bin").read_bytes(); b = (out / "m0" / f"{kind}-{n}.bin").read_bytes()
    ha, ba = a.split(b"\n", 1); hb, bb = b.split(b"\n", 1)
    ha, hb = json.loads(ha), json.loads(hb)
    res[kind] = {"file_equal": a == b, "body_equal": ba == bb, "body_bytes": len(ba), "body_sha512": hashlib.sha512(ba).hexdigest(),
                 "header_fields_differing": sorted(k for k in set(ha) | set(hb) if ha.get(k) != hb.get(k)),
                 "file_sha512": hashlib.sha512(a).hexdigest()}
res["roots"] = rec["roots"]
res["registration_roots_are_the_files"] = rec["roots"] == win["frame_v3"]["roots"] and rec["domains"] == win["frame_v3"]["domain_ids"]

# 4. overhead
res["serving_rows_seconds"] = win["seconds"]
res["stages"] = stages.read_text().splitlines() if stages.is_file() else None
res["ok"] = (res["captured"]["ok"] and res["circuit"]["pin_agreed"] and res["registration_roots_are_the_files"]
             and all(res[k]["file_equal"] for k in ("pub", "inst")))
(out / "compare.json").write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps({k: v for k, v in res.items() if k != "stages"}, indent=1))
print("SC-COMPARE", "OK" if res["ok"] else "FAIL")
