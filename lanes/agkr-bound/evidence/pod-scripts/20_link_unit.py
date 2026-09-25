"""agkr-bound: the bit link's prime side IN the BF16 unit (tools/link_stub.extend_unit: the 2k operand columns the GKR
layers consume, 16 bits each, booleanity + recomposition), under the frame-v3 SHA-256 scaffold statement (R+sha256).
Times the extended unit against the plain one (same process, warm, REPS reps each), then the negatives the link's prime
side must catch, Python and Rust (--allow-any-circuit --require-commitment) verifiers:

  honest            bits of the operands the unit consumes                                   -> accept
  bit_flip          one bit flipped (booleanity holds, recomposition fails)                  -> reject
  non_boolean       b0 += 2, b1 -= 1 (recomposition holds, booleanity fails)                 -> reject
  alt_honest_bits   altered operand (valid unit, public words honest), bits of the frozen one -> reject: recomposition
  alt_alt_bits      altered operand with its own bits                                        -> ACCEPT: only the cross-field
                                                                                                 link (not built) closes it
    python 20_link_unit.py STMT OUT VERIFIER [N] [THREADS] [REPS]      (cwd backends/gkr)
"""
from __future__ import annotations

import hashlib
import json
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
from gpu import prover                                 # noqa: E402
from gpu.bb_export import write_rows                   # noqa: E402
from gpu.circuit import layers, parse_circuit          # noqa: E402
from gpu.run import read_chain                         # noqa: E402

S, OUT, VB = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 4096
NT = int(sys.argv[5]) if len(sys.argv) > 5 else 13
REPS = int(sys.argv[6]) if len(sys.argv) > 6 else 3
REL, LEAF = "bf16-ampere", "sha256"
dev = torch.device("cuda")
OUT.mkdir(parents=True, exist_ok=True)
man = json.loads((S / "manifest.json").read_text())
steps = man["steps"]
base_text = (S / "circuit.txt").read_text()
uc0 = parse_circuit(base_text)
names = uc0.col_names
k = (names.index("y.s") - 5) // 2
COLS = list(range(5, 5 + 2 * k))
utext = LS.extend_unit(base_text, COLS, 16)
uc = parse_circuit(utext)
ul0, ul = layers(uc0), layers(uc)
print(f"unit: {uc0.ncols} columns / {uc0.nwires} wires -> {uc.ncols} / {uc.nwires} ({len(COLS)} operand columns x 16 bits); "
      f"layers {len(ul0)} -> {len(ul)}", flush=True)
etext = CM.extend_epilogue((S / "epilogue.txt").read_text())
ec = parse_circuit(etext)
el = layers(ec)
src = Path(br.__file__).resolve().parents[2]
frozen = src / "fixtures" / "bench-instances" / "v1" / "manifest.json"

from gpu.v2.witness import Generator, Ops              # noqa: E402
from verity_numerical.checker import REAL              # noqa: E402

x, W, y0, _ = br.load_frozen(Path("/workspace/bench-instances/v1"), frozen, br.TIER, 0, N)
X = np.array(x, dtype=np.uint16)
yw = 4 if y0.dtype == np.uint32 else 2
y = np.asarray(y0).reshape(N, 1)
ops = Ops("cuda")
gen = Generator(ops, REAL)


def rows_for(xx):
    return gen.run(ops.asarray(xx), ops.asarray(W), ops.asarray(y0))


iset = CM.instance_set(REL, 0, N, src, frozen)
C = CM.commit(LEAF, REL, iset, 0, X, W, y, yw)
L = C.limb_columns()
SC = ("--allow-any-circuit", "--require-commitment")
ci = torch.tensor(COLS, device=dev)
sh = torch.arange(16, device=dev)


def bits_of(units: torch.Tensor) -> torch.Tensor:
    v = units.index_select(1, ci)
    return ((v[:, :, None] >> sh) & 1).reshape(units.shape[0], -1)


def statement(name: str):
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
    return sd, pub


def instance(sd: Path, pub, units, epi_rows, circ, lay):
    ch = read_chain(sd / "chain.txt", circ, ec, steps, [int(v) for v in pub.reshape(-1)])
    ch.commit_digest = hashlib.sha256((sd / "commitment.txt").read_bytes()).digest()
    epi = torch.cat([epi_rows, torch.from_numpy(L).to(dev)], 1)
    return prover.Instance([prover.Segment("unit", circ, lay, units, circ.hash), prover.Segment("epilogue", ec, el, epi, ec.hash)], ch)


def prove(inst, sd: Path | None = None):
    torch.cuda.synchronize(dev)
    t0 = time.perf_counter()
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize(dev)
    tp = time.perf_counter() - t0
    try:
        prover.verify(inst, proof, True)
        py = "accept"
    except prover.VerifyError as e:
        py = f"reject ({str(e)[:90]})"
    data = proof.to_bytes()
    if sd is not None:
        (sd / "proof.bin").write_bytes(data)
    return py, tp, st, len(data)


def rust(sd: Path):
    out = sd / "verify_sc.json"
    r = subprocess.run([VB, "verify", "--dir", str(sd), "--proof", str(sd / "proof.bin"), "--vus", str(N), "--threads", str(NT),
                        "--json", str(out), *SC], capture_output=True, text=True)
    doc = json.loads(out.read_text()) if out.is_file() else {}
    return bool(doc.get("accepted")) and r.returncode == 0, doc.get("error") or r.stderr[-200:] or None, doc


results, ok = {}, True
honest_rows = rows_for(X)
assert int(honest_rows.bad.sum()) == 0
hb = bits_of(honest_rows.units)
sd, pub = statement("honest")

timing = {}
for label, circ, lay, units in (("plain", uc0, ul0, honest_rows.units), ("link", uc, ul, torch.cat([honest_rows.units, hb], 1))):
    inst = instance(sd, pub, units, honest_rows.epilogue, circ, lay)
    runs = []
    for rep in range(REPS + 1):
        py, tp, st, nbytes = prove(inst, sd if label == "link" and rep == REPS else None)
        runs.append({"rep": rep - 1, "prove_s": tp, "python": py, "t_commit": st.t_commit, "t_lookup": st.t_lookup, "t_arith": st.t_arith,
                     "t_open": st.t_open, "committed_elements": st.committed_elements, "ligero_rows": st.ligero_rows,
                     "sequential_depth": st.sequential_depth(True), "proof_bytes": nbytes, "peak_mem_bytes": st.peak_mem})
        print(f"{label} rep {rep - 1}: prove {tp:.4f} s python {py} commit {st.t_commit:.4f} lookup {st.t_lookup:.4f} arith {st.t_arith:.4f} "
              f"open {st.t_open:.4f} committed {st.committed_elements} rows {st.ligero_rows} depth {st.sequential_depth(True)} bytes {nbytes}", flush=True)
    timing[label] = runs
    del inst
med = {lab: float(np.median([r["prove_s"] for r in runs[1:]])) for lab, runs in timing.items()}
print(f"median prove: plain {med['plain']:.4f} s, link-in-unit {med['link']:.4f} s (+{100 * (med['link'] / med['plain'] - 1):.0f}%)", flush=True)
got, err, doc = rust(sd)
results["honest"] = {"rust": got, "err": err, "python": timing["link"][-1]["python"], "ok": got and timing["link"][-1]["python"] == "accept"}
ok &= results["honest"]["ok"]
print(f"honest            rust={'accept' if got else 'reject'} ({err}) python={results['honest']['python']}", flush=True)


def case(name, units, epi_rows, want):
    global ok
    sd, pub = statement(name)
    py, _tp, _st, _n = prove(instance(sd, pub, units, epi_rows, uc, ul), sd)
    got, err, _ = rust(sd)
    good = got == want and (py == "accept") == want
    results[name] = {"rust": got, "err": err, "python": py, "expected": "accept" if want else "reject", "ok": good}
    ok &= good
    print(f"{name:17s} rust={'accept' if got else 'reject'} ({err}) python={py} -> {'OK' if good else 'UNEXPECTED'}", flush=True)


u = 7 * steps + 3
b = hb.clone(); b[u, 5] ^= 1
case("bit_flip", torch.cat([honest_rows.units, b], 1), honest_rows.epilogue, False)
b = hb.clone(); j = next(i for i in range(0, hb.shape[1], 16) if int(hb[u, i + 1]) == 1)
b[u, j] += 2; b[u, j + 1] -= 1
case("non_boolean", torch.cat([honest_rows.units, b], 1), honest_rows.epilogue, False)

alt = None
zero = (0x0000, 0x8000)
for tried, (v, t) in enumerate((v, int(t)) for v in range(N) for t in np.nonzero(np.isin(W[v], zero))[0]):
    if tried >= 12:
        break
    xx = X.copy()
    xx[v, t] ^= 1
    rows = rows_for(xx)
    if int(rows.bad.sum()) == 0:
        alt = (v, t, rows)
        break
if alt is None:
    raise SystemExit("no altered operand keeps the public words honest")
v, t, alt_rows = alt
print(f"altered operand: VU {v} word {t} x {int(X[v, t]):#x} -> {int(X[v, t]) ^ 1:#x} (w {int(W[v, t]):#x})", flush=True)
case("alt_honest_bits", torch.cat([alt_rows.units, hb], 1), alt_rows.epilogue, False)
case("alt_alt_bits", torch.cat([alt_rows.units, bits_of(alt_rows.units)], 1), alt_rows.epilogue, True)

(OUT / "link_unit.json").write_text(json.dumps({"relation": C.relation, "vus": N, "unit_columns": [uc0.ncols, uc.ncols],
                                                "unit_wires": [uc0.nwires, uc.nwires], "operand_columns": COLS, "timing": timing,
                                                "median_prove_s": med, "altered": {"vu": v, "word": t}, "cases": results, "ok": bool(ok)},
                                               indent=1, default=str))
print("LINK-UNIT OK" if ok else "LINK-UNIT FAILED", flush=True)
sys.exit(0 if ok else 1)
