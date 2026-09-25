"""agkr-bound: the built sigma-form link (gpu/link.py + verifier/src/link.rs, lane/agkr-bound) on the in-unit
statement: timing against the same in-unit proof without the link, and the red team's prime-side negatives, each
against the Python verifier and the Rust verifier (VB, --allow-any-circuit --require-commitment; the Rust verifier
derives root_b and y itself: root_b from commitment.txt, z from x.bin / w.bin checked against the public digests).  The binary side is a STAND-IN: the
verifier's own copy of the operand words gives y; results are drill-down only (reason L), no cell counts.

  honest               -> accept                     bit_flip         one link bit flipped -> reject
  non_boolean          b0 += 2, b1 -= 1 -> reject     alt_alt_bits     altered operand with its own bits -> reject
  sigma_range          sigma_0 + n_cells + 2 (parity kept, out of range) -> reject
  sigma_plus2          sigma_0 + 2 (parity kept, in range) -> reject
  root_b_changed       the prover's root_b differs from the statement's (the points must change) -> reject
  z_differs            the verifier's z has one word altered, honest prover -> reject (Rust: x.bin altered, which
                       no longer hashes to the public digest -> statement reject)
  S dup_cell           two link columns with one name -> setup reject
  S no_booleanity      one booleanity assertion dropped -> setup reject

    [REL=bf16-ampere LEAF=sha256] python 31_link_rust.py STMT OUT N THREADS REPS VB      (cwd backends/gkr)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import bench_result as br                              # noqa: E402
import link_stub as LS                                 # noqa: E402
from gpu import commit as CM                           # noqa: E402
from gpu import link as LK                             # noqa: E402
from gpu import prover                                 # noqa: E402
from gpu.bb_export import write_rows                   # noqa: E402
from gpu.circuit import layers, parse_circuit          # noqa: E402
from gpu.run import read_chain                         # noqa: E402

S, OUT = Path(sys.argv[1]), Path(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
NT = int(sys.argv[4]) if len(sys.argv) > 4 else 13
REPS = int(sys.argv[5]) if len(sys.argv) > 5 else 3
VB = sys.argv[6]
REL, LEAF = os.environ.get("REL", "bf16-ampere"), os.environ.get("LEAF", "sha256")
FP8 = REL.startswith("fp8")
BITS = 8 if FP8 else 16
dev = torch.device("cuda")
OUT.mkdir(parents=True, exist_ok=True)
man = json.loads((S / "manifest.json").read_text())
steps = man["steps"]
base_text = (S / "circuit.txt").read_text()
uc0 = parse_circuit(base_text)
k = (uc0.col_names.index("y.s") - 5) // 2
COLS = list(range(5, 5 + 2 * k))
utext = LS.extend_unit(base_text, COLS, BITS)
uc = parse_circuit(utext)
ul = layers(uc)
etext = CM.extend_epilogue((S / "epilogue.txt").read_text())
ec = parse_circuit(etext)
el = layers(ec)
src = Path(br.__file__).resolve().parents[2]
frozen = src / "fixtures" / "bench-instances" / "v1" / "manifest.json"

from gpu.v2.fp8 import relation_params                 # noqa: E402
from gpu.v2.witness import Generator, Ops              # noqa: E402

if REL == "bf16-ampere":
    from verity_numerical.checker import REAL          # noqa: E402

    x, W, y0, _ = br.load_frozen(Path("/workspace/bench-instances/v1"), frozen, br.TIER, 0, N)
    params = REAL
else:
    x, W, y0, rel = br.load_relation(REL, src, 0, N, NT)
    params = relation_params(rel)[0]
X = np.array(x, dtype=np.uint16)
Wn = np.array(W, dtype=np.uint16).reshape(N, -1)
K = X.shape[1]
yw = 4 if y0.dtype == np.uint32 else 2
y = np.asarray(y0).reshape(N, 1)
ops = Ops("cuda")
gen = Generator(ops, params)
iset = CM.instance_set(REL, 0, N, src, frozen)
C = CM.commit(LEAF, REL, iset, 0, X, W, y, yw)
L = C.limb_columns()
ci = torch.tensor(COLS, device=dev)
sh = torch.arange(BITS, device=dev)
ROOT_B = LK.standin_root_b(C.text().encode())


def rows_for(xx):
    return gen.run(ops.asarray(xx), ops.asarray(W), ops.asarray(y0))


def bits_of(units: torch.Tensor) -> torch.Tensor:
    v = units.index_select(1, ci)
    return ((v[:, :, None] >> sh) & 1).reshape(units.shape[0], -1)


def statement(name: str, root_b: bytes = ROOT_B):
    sd = OUT / name
    if sd.exists():
        shutil.rmtree(sd)
    br.write_statement(S, sd, [0] * N)
    (sd / "circuit.txt").write_text(utext)
    (sd / "epilogue.txt").write_text(etext)
    (sd / "chain.txt").write_text(CM.extend_chain((S / man.get("chain_file", "chain.txt")).read_text()))
    pub = np.concatenate([np.asarray(y, dtype=np.int64), L], 1)
    write_rows(pub.tolist(), sd / "public.bin")
    (sd / "commitment.txt").write_text(C.text())
    (sd / "link.txt").write_text(f"link sigma-gf2_256/v1\nroot_b {root_b.hex()}\n")
    (sd / "x.bin").write_bytes(X.astype("<u2").tobytes())
    (sd / "w.bin").write_bytes(Wn.astype("<u2").tobytes())
    return sd, pub


t0 = time.perf_counter()
LAY = LK.derive(uc, N, steps, K, BITS)
t_derive = time.perf_counter() - t0
print(f"{REL}+{LEAF}: layout {LAY} cells {LAY.n_cells} m {LAY.m}; derive {t_derive:.2f} s", flush=True)


def instance(sd: Path, pub, units, epi_rows, link=True, root_b=ROOT_B, zx=None):
    ch = read_chain(sd / "chain.txt", uc, ec, steps, [int(v) for v in pub.reshape(-1)])
    ch.commit_digest = hashlib.sha256((sd / "commitment.txt").read_bytes()).digest()
    epi = torch.cat([epi_rows, torch.from_numpy(L).to(dev)], 1)
    lk = LK.Link(LAY, root_b, X if zx is None else zx, Wn) if link else None
    return prover.Instance([prover.Segment("unit", uc, ul, units, uc.hash), prover.Segment("epilogue", ec, el, epi, ec.hash)], ch,
                           link=lk)


def verdict(inst, proof) -> str:
    try:
        prover.verify(inst, proof, True)
        return "accept"
    except prover.VerifyError as e:
        return f"reject ({str(e)[:100]})"


honest_rows = rows_for(X)
assert int(honest_rows.bad.sum()) == 0
hb = bits_of(honest_rows.units)
hunits = torch.cat([honest_rows.units, hb], 1)
sd, pub = statement("honest")
timing = {}
for label, on in (("in_unit", False), ("in_unit+link", True)):
    inst = instance(sd, pub, hunits, honest_rows.epilogue, link=on)
    runs = []
    for rep in range(REPS + 1):
        torch.cuda.synchronize(dev)
        ta = time.perf_counter()
        proof, st = prover.prove(inst, True)
        torch.cuda.synchronize(dev)
        tp = time.perf_counter() - ta
        tb = time.perf_counter()
        py = verdict(inst, proof)
        torch.cuda.synchronize(dev)
        tv = time.perf_counter() - tb
        data = proof.to_bytes()
        runs.append({"rep": rep - 1, "prove_s": tp, "verify_py_s": tv, "python": py, "t_link": st.t_link, "t_open": st.t_open,
                     "proof_bytes": len(data), "msgs": len(proof.msgs), "peak_mem_bytes": st.peak_mem})
        print(f"{label} rep {rep - 1}: prove {tp:.4f} s (link {st.t_link:.4f}) verify {tv:.3f} s python {py} bytes {len(data)} "
              f"peak {st.peak_mem / 2**30:.1f} GiB", flush=True)
        if on and rep == REPS:
            (sd / "proof.bin").write_bytes(data)
        if not on and rep == REPS:
            sdn, _ = statement("honest_nolink")
            (sdn / "link.txt").unlink()
            (sdn / "proof.bin").write_bytes(data)
    timing[label] = runs
    del inst, proof
med = {lab: {f: float(np.median([r[f] for r in rs[1:]])) for f in ("prove_s", "verify_py_s", "t_link")} for lab, rs in timing.items()}
print(f"median prove {med['in_unit']['prove_s']:.4f} -> {med['in_unit+link']['prove_s']:.4f} s (link {med['in_unit+link']['t_link']:.4f}); "
      f"Python verify {med['in_unit']['verify_py_s']:.3f} -> {med['in_unit+link']['verify_py_s']:.3f} s", flush=True)
results = {"honest": {"python": timing["in_unit+link"][-1]["python"], "expected": "accept"}}
ok = all(r["python"] == "accept" for rs in timing.values() for r in rs)


def case(name, units, epi_rows, want="reject", prover_kw=None, verifier_kw=None):
    global ok
    sdc, pubc = statement(name)
    inst_p = instance(sdc, pubc, units, epi_rows, **(prover_kw or {}))
    proof, _ = prover.prove(inst_p, True)
    inst_v = instance(sdc, pubc, units, epi_rows, **(verifier_kw or {})) if (prover_kw or verifier_kw) else inst_p
    py = verdict(inst_v, proof)
    good = py.startswith(want)
    results[name] = {"python": py, "expected": want, "ok": good}
    ok &= good
    print(f"{name:16s} python={py} -> {'OK' if good else 'UNEXPECTED'}", flush=True)
    (sdc / "proof.bin").write_bytes(proof.to_bytes())
    if verifier_kw and "zx" in verifier_kw:
        (sdc / "x.bin").write_bytes(verifier_kw["zx"].astype("<u2").tobytes())
    del inst_p, inst_v, proof

u = 7 * steps + 3
b = hb.clone(); b[u, 5] ^= 1
case("bit_flip", torch.cat([honest_rows.units, b], 1), honest_rows.epilogue)
b = hb.clone(); j = next(i for i in range(0, hb.shape[1], BITS) if int(hb[u, i + 1]) == 1)
b[u, j] += 2; b[u, j + 1] -= 1
case("non_boolean", torch.cat([honest_rows.units, b], 1), honest_rows.epilogue)

zero = (0x00, 0x80) if FP8 else (0x0000, 0x8000)
cands = ((v, int(t)) for v in range(N) for t in np.nonzero(np.isin(Wn[v], zero))[0] if not (FP8 and (int(X[v, t]) & 0x7F) >= 0x7E))
alt = None
for tried, (v, t) in enumerate(cands):
    if tried >= 12:
        break
    xx = X.copy()
    xx[v, t] ^= 1
    rows = rows_for(xx)
    if int(rows.bad.sum()) == 0:
        alt = (v, t, xx, rows)
        break
if alt is None:
    raise SystemExit("no altered operand keeps the public words honest")
v, t, xalt, alt_rows = alt
case("alt_alt_bits", torch.cat([alt_rows.units, bits_of(alt_rows.units)], 1), alt_rows.epilogue)
del alt_rows

_ps = LK.plane_sums
TAMPER = {"d": 0}


def tampered(T, lay, bv, ident):
    s = _ps(T, lay, bv, ident)
    if not ident and TAMPER["d"]:
        s = [s[0] + TAMPER["d"]] + s[1:]
    return s


LK.plane_sums = tampered
for name, d in (("sigma_range", LAY.n_cells + 2 if LAY.n_cells % 2 == 0 else LAY.n_cells + 1), ("sigma_plus2", 2)):
    TAMPER["d"] = d
    sdc, pubc = statement(name)
    inst = instance(sdc, pubc, hunits, honest_rows.epilogue)
    proof, _ = prover.prove(inst, True)
    TAMPER["d"] = 0
    py = verdict(inst, proof)
    good = py.startswith("reject")
    results[name] = {"python": py, "expected": "reject", "ok": good}
    ok &= good
    print(f"{name:16s} python={py} -> {'OK' if good else 'UNEXPECTED'}", flush=True)
    (sdc / "proof.bin").write_bytes(proof.to_bytes())
    del inst, proof
LK.plane_sums = _ps

case("root_b_changed", hunits, honest_rows.epilogue, prover_kw={"root_b": hashlib.sha256(b"another binary root").digest()})
zx = X.copy(); zx[v, t] ^= 1
case("z_differs", hunits, honest_rows.epilogue, verifier_kw={"zx": zx})

for name, text in (("dup_cell", utext.replace(f"link.b{COLS[0]}.1\n", f"link.b{COLS[0]}.0\n", 1)),
                   ("no_booleanity", re.sub(rf"assert link\.bool{COLS[0]}\.3 .*", f"assert link.bool{COLS[0]}.3 0 0", utext, count=1))):
    try:
        LK.derive(parse_circuit(text), N, steps, K, BITS)
        got = "accept"
    except (prover.VerifyError, Exception) as e:
        got = f"reject ({str(e)[:100]})"
    good = got.startswith("reject")
    results[name] = {"setup": got, "expected": "reject", "ok": good}
    ok &= good
    print(f"S {name:14s} setup={got} -> {'OK' if good else 'UNEXPECTED'}", flush=True)
    sdc = OUT / f"S_{name}"
    shutil.rmtree(sdc, ignore_errors=True)
    shutil.copytree(sd, sdc)
    (sdc / "circuit.txt").write_text(text)


def rust(sdc: Path):
    out = sdc / "rust.json"
    r = subprocess.run([VB, "verify", "--dir", str(sdc), "--proof", str(sdc / "proof.bin"), "--vus", str(N), "--threads", str(NT),
                        "--allow-any-circuit", "--require-commitment", "--json", str(out)], capture_output=True, text=True)
    doc = json.loads(out.read_text()) if out.is_file() else {}
    got = "accept" if doc.get("accepted") and r.returncode == 0 else f"reject ({str(doc.get('error') or r.stderr[-200:])[:120]})"
    return got, doc


rust_runs = {}
for name in ["honest_nolink", "honest", "honest"] + [n for n in results if n != "honest"]:
    sdc = OUT / (f"S_{name}" if "setup" in results.get(name, {}) else name)
    got, doc = rust(sdc)
    want = "accept" if name.startswith("honest") else "reject"
    good = got.startswith(want)
    ok &= good
    if name.startswith("honest"):
        rust_runs.setdefault(name, []).append({k: doc.get(k) for k in ("verify_seconds", "t_link", "t_link_derive", "t_transcript", "t_functional_value",
                                                                       "t_rows_linear_test", "t_rows_fill_cpu", "msgs", "slots", "peak_rss_bytes")})
    results.setdefault(name, {})["rust"] = got
    results[name]["ok"] = results[name].get("ok", True) and good
    print(f"rust {name:16s} {got} -> {'OK' if good else 'UNEXPECTED'}; verify {doc.get('verify_seconds')} s link {doc.get('t_link')} "
          f"derive {doc.get('t_link_derive')}", flush=True)

(OUT / "link_build.json").write_text(json.dumps({"relation": C.relation, "vus": N, "layout": LAY.__dict__, "derive_s": t_derive,
                                                 "timing": timing, "median": med, "rust_honest": rust_runs, "altered": {"vu": v, "word": t}, "cases": results,
                                                 "ok": bool(ok)}, indent=1, default=str))
print("LINK-BUILD OK" if ok else "LINK-BUILD FAILED", flush=True)
sys.exit(0 if ok else 1)
