"""agkr-bound: the bit link's dense GF(2^128) check folded into the real in-unit A-GKR proof (scaffold, pod script only:
the link protocol is NOT built and no cell counts).  A-GKR batches every residual claim into one materialised functional
<a, X> = b opened once by Ligero (gpu/prover.py Acc, ligero.prove_open); the dense check is one more term of it:

  r in GF(2^128)^m from the transcript, eq_i = eq(r, i) over the link bits in unit order (tools/link_stub.extend_unit);
  prover: S_t = sum_i bit_t(eq_i) b_i per plane, u_t = floor(S_t / 2) absorbed (a stand-in for u_t's own commitment,
  0.032 s / 471 KB measured in 21), rho_t in BabyBear^6 from the transcript, a[pos(i)] += c_i = sum_t rho_t bit_t(eq_i);
  verifier: the same c_i into its a (O(N)), b += sum_t rho_t (2 u_t + z_t) with z the binary side's value (a stand-in:
  computed from the honest message bits, the Flock side is not built), u_t < 2^29.

Wraps ligero.prove_open / verify_open, so nothing in the repo changes.  Times prove and the Python verifier with and without
the term on bf16-ampere+sha256 (4,096 VUs, A100) and runs honest -> accept, gap_alt_operand with its own bits -> reject.
    [REL=bf16-ampere LEAF=sha256] python 28_link_dense.py STMT OUT [N] [THREADS] [REPS]      (cwd backends/gkr)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch
import triton
import triton.language as tl

sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import bench_result as br                              # noqa: E402
import link_stub as LS                                 # noqa: E402
from gpu import commit as CM                           # noqa: E402
from gpu import ligero                                 # noqa: E402
from gpu import prover                                 # noqa: E402
from gpu.bb_export import write_rows                   # noqa: E402
from gpu.circuit import layers, parse_circuit          # noqa: E402
from gpu.field import e_add, e_scale, ZERO             # noqa: E402
from gpu.run import read_chain                         # noqa: E402

S, OUT = Path(sys.argv[1]), Path(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
NT = int(sys.argv[4]) if len(sys.argv) > 4 else 13
REPS = int(sys.argv[5]) if len(sys.argv) > 5 else 3
REL, LEAF = os.environ.get("REL", "bf16-ampere"), os.environ.get("LEAF", "sha256")
FP8 = REL.startswith("fp8")
BITS = 8 if FP8 else 16
P = 2**31 - 2**27 + 1
MASK = (1 << 128) - 1
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
yw = 4 if y0.dtype == np.uint32 else 2
y = np.asarray(y0).reshape(N, 1)
ops = Ops("cuda")
gen = Generator(ops, params)
iset = CM.instance_set(REL, 0, N, src, frozen)
C = CM.commit(LEAF, REL, iset, 0, X, W, y, yw)
L = C.limb_columns()
ci = torch.tensor(COLS, device=dev)
sh = torch.arange(BITS, device=dev)
NB_UNIT = len(COLS) * BITS


def rows_for(xx):
    return gen.run(ops.asarray(xx), ops.asarray(W), ops.asarray(y0))


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


def instance(sd: Path, pub, units, epi_rows):
    ch = read_chain(sd / "chain.txt", uc, ec, steps, [int(v) for v in pub.reshape(-1)])
    ch.commit_digest = hashlib.sha256((sd / "commitment.txt").read_bytes()).digest()
    epi = torch.cat([epi_rows, torch.from_numpy(L).to(dev)], 1)
    return prover.Instance([prover.Segment("unit", uc, ul, units, uc.hash), prover.Segment("epilogue", ec, el, epi, ec.hash)], ch)


# ---- the dense check -------------------------------------------------------------------------------------------------

def gmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 128:
            a = (a & MASK) ^ 0x87
    return r


def split(val: int):
    s = lambda z: z - (1 << 64) if z >> 63 else z
    return s(val & ((1 << 64) - 1)), s(val >> 64)


@triton.jit
def eq_level(T, TB, TAB, h, BLOCK: tl.constexpr):
    i = tl.program_id(0).to(tl.int64) * BLOCK + tl.arange(0, BLOCK).to(tl.int64)
    m = i < h
    lo = tl.zeros([BLOCK], dtype=tl.int64)
    hi = tl.zeros([BLOCK], dtype=tl.int64)
    for kk in tl.static_range(16):
        b = tl.load(TB + i * 16 + kk, mask=m, other=0).to(tl.int64)
        lo ^= tl.load(TAB + (kk * 256 + b) * 2, mask=m, other=0)
        hi ^= tl.load(TAB + (kk * 256 + b) * 2 + 1, mask=m, other=0)
    tl.store(T + (i + h) * 2, lo, mask=m)
    tl.store(T + (i + h) * 2 + 1, hi, mask=m)
    tl.store(T + i * 2, tl.load(T + i * 2, mask=m, other=0) ^ lo, mask=m)
    tl.store(T + i * 2 + 1, tl.load(T + i * 2 + 1, mask=m, other=0) ^ hi, mask=m)


@triton.jit
def planes_k(TB, B, SP, n, BLOCK: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    i = pid * BLOCK + tl.arange(0, BLOCK).to(tl.int64)
    m = i < n
    j = tl.arange(0, 128)
    byte = tl.load(TB + i[:, None] * 16 + (j[None, :] // 8), mask=m[:, None], other=0).to(tl.int32)
    bit = tl.load(B + i, mask=m, other=0).to(tl.int32)
    tl.store(SP + pid * 128 + j, tl.sum(((byte >> (j[None, :] % 8)) & 1) * bit[:, None], 0))


@triton.jit
def scatter_k(TB, R8, WC, A, n, per_unit, ncols, col0, p, BLOCK: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    i = pid * BLOCK + tl.arange(0, BLOCK).to(tl.int64)
    m = i < n
    j = tl.arange(0, 128)
    byte = tl.load(TB + i[:, None] * 16 + (j[None, :] // 8), mask=m[:, None], other=0).to(tl.int32)
    b = ((byte >> (j[None, :] % 8)) & 1).to(tl.int8)
    r8 = tl.load(R8 + j[:, None] * 32 + tl.arange(0, 32)[None, :])
    lm = tl.dot(b, r8, out_dtype=tl.int32).to(tl.int64)
    base = ((i // per_unit) * ncols + col0 + i % per_unit) * 6
    for e in tl.static_range(6):
        w = tl.load(WC + e * 32 + tl.arange(0, 32))
        ce = tl.sum(lm * w[None, :], 1) % p
        old = tl.load(A + base + e, mask=m, other=0).to(tl.int64)
        tl.store(A + base + e, ((old + ce) % p).to(A.dtype.element_ty), mask=m)


WC = torch.zeros((6, 32), dtype=torch.int64)
for e in range(6):
    for q in range(5):
        WC[e, e * 5 + q] = pow(128, q, P)
WC = WC.to(dev)
LINK: dict = {"on": False}
BLK = 256
BYTESEL = ((np.arange(256)[:, None] >> np.arange(8)[None, :]) & 1).astype(bool)


def challenges(tr, nb: int):
    m = math.ceil(math.log2(nb))
    seed = hashlib.sha256(repr(tr.challenge()).encode()).digest()
    r = [int.from_bytes(hashlib.sha256(seed + j.to_bytes(4, "little")).digest()[:16], "little") for j in range(m)]
    tabs = np.zeros((m, 16, 256, 2), dtype=np.int64)
    for jj in range(m):
        basis, val = np.zeros((128, 2), dtype=np.int64), r[jj]
        for s in range(128):
            basis[s] = split(val)
            val = ((val << 1) & MASK) ^ (0x87 if val >> 127 else 0)
        basis = basis.reshape(16, 8, 2)
        for q in range(8):
            tabs[jj] ^= np.where(BYTESEL[None, :, q, None], basis[:, None, q, :], 0)
    tabs = torch.from_numpy(tabs).to(dev)
    T = torch.zeros((1 << m, 2), dtype=torch.int64, device=dev)
    T[0, 0] = 1
    tb = T.view(torch.uint8).view(1 << m, 16)
    for jj in range(m):
        h = 1 << jj
        eq_level[(triton.cdiv(h, 1024),)](T, tb, tabs[jj], h, BLOCK=1024)
    return T, tb


def plane_sums(tb, bits_flat, nb):
    nblk = triton.cdiv(nb, BLK)
    sp = torch.empty((nblk, 128), dtype=torch.int32, device=dev)
    planes_k[(nblk,)](tb, bits_flat, sp, nb, BLOCK=BLK)
    return sp.sum(0, dtype=torch.int64)


def add_c(tb, rho, a, nb):
    r8 = torch.zeros((128, 32), dtype=torch.int64)
    rh = torch.tensor(rho, dtype=torch.int64)
    for e in range(6):
        for q in range(5):
            r8[:, e * 5 + q] = (rh[:, e] >> (7 * q)) & 127
    r8 = r8.to(torch.int8).to(dev)
    scatter_k[(triton.cdiv(nb, BLK),)](tb, r8, WC, a, nb, NB_UNIT, LINK["ncols"], LINK["col0"], P, BLOCK=BLK)


_prove_open, _verify_open = ligero.prove_open, ligero.verify_open


def prove_open(cm, a, tr, timers=None):
    if not LINK["on"]:
        return _prove_open(cm, a, tr, timers)
    torch.cuda.synchronize(dev)
    t0 = time.perf_counter()
    nb = LINK["bits"].numel()
    T, tb = challenges(tr, nb)
    S_t = plane_sums(tb, LINK["bits"], nb)
    u = (S_t >> 1).tolist()
    LINK["u"] = u
    tr.absorb(b"".join(int(v).to_bytes(4, "little") for v in u))
    rho = tr.challenges(128)
    add_c(tb, rho, a, nb)
    del T, tb
    torch.cuda.synchronize(dev)
    LINK["t_prove"] = time.perf_counter() - t0
    return _prove_open(cm, a, tr, timers)


def verify_open(root, params, length, a, b, op, tr, device):
    if not LINK["on"]:
        return _verify_open(root, params, length, a, b, op, tr, device)
    torch.cuda.synchronize(dev)
    t0 = time.perf_counter()
    nb = LINK["honest_bits"].numel()
    T, tb = challenges(tr, nb)
    t1 = time.perf_counter()
    z = (plane_sums(tb, LINK["honest_bits"], nb) & 1).tolist()      # the binary side's value: a stand-in
    torch.cuda.synchronize(dev)
    t2 = time.perf_counter()
    u = LINK["u"]
    if len(u) != 128 or any(not 0 <= v < (1 << 29) for v in u):
        raise prover.VerifyError("link: u_t out of range")
    tr.absorb(b"".join(int(v).to_bytes(4, "little") for v in u))
    rho = tr.challenges(128)
    add_c(tb, rho, a, nb)
    extra = ZERO
    for t in range(128):
        extra = e_add(extra, e_scale(rho[t], (2 * u[t] + z[t]) % P))
    del T, tb
    torch.cuda.synchronize(dev)
    LINK["t_verify"] = time.perf_counter() - t2 + (t1 - t0)
    LINK["t_binary_z"] = t2 - t1
    return _verify_open(root, params, length, a, e_add(b, extra), op, tr, device)


ligero.prove_open, ligero.verify_open = prove_open, verify_open
prover.ligero.prove_open, prover.ligero.verify_open = prove_open, verify_open

# ---- runs ------------------------------------------------------------------------------------------------------------

honest_rows = rows_for(X)
assert int(honest_rows.bad.sum()) == 0
hb = bits_of(honest_rows.units)
LINK.update(ncols=uc.ncols, col0=uc0.ncols, honest_bits=hb.reshape(-1).to(torch.uint8).contiguous())
sd, pub = statement("honest")
inst = instance(sd, pub, torch.cat([honest_rows.units, hb], 1), honest_rows.epilogue)


def run(label: str, on: bool, bits_flat):
    LINK["on"] = on
    LINK["bits"] = bits_flat
    out = []
    for rep in range(REPS + 1):
        torch.cuda.synchronize(dev)
        t0 = time.perf_counter()
        proof, st = prover.prove(inst, True)
        torch.cuda.synchronize(dev)
        tp = time.perf_counter() - t0
        t1 = time.perf_counter()
        try:
            prover.verify(inst, proof, True)
            py = "accept"
        except prover.VerifyError as e:
            py = f"reject ({str(e)[:90]})"
        torch.cuda.synchronize(dev)
        tv = time.perf_counter() - t1
        rec = {"rep": rep - 1, "prove_s": tp, "verify_py_s": tv, "python": py, "t_open": st.t_open, "t_open_acc": st.t_open_acc,
               "link_prove_s": LINK.get("t_prove") if on else None, "link_verify_s": LINK.get("t_verify") if on else None,
               "binary_z_s": LINK.get("t_binary_z") if on else None, "proof_bytes": len(proof.to_bytes())}
        out.append(rec)
        print(f"{label} rep {rep - 1}: prove {tp:.4f} s (link term {rec['link_prove_s']}) verify {tv:.3f} s (link term "
              f"{rec['link_verify_s']}) python {py} open {st.t_open:.4f}", flush=True)
    return out


timing = {"in_unit": run("in-unit", False, None), "in_unit+dense": run("in-unit+dense", True, LINK["honest_bits"])}
med = {lab: {f: float(np.median([r[f] for r in rs[1:]])) for f in ("prove_s", "verify_py_s")} for lab, rs in timing.items()}
med["in_unit+dense"]["link_prove_s"] = float(np.median([r["link_prove_s"] for r in timing["in_unit+dense"][1:]]))
med["in_unit+dense"]["link_verify_s"] = float(np.median([r["link_verify_s"] for r in timing["in_unit+dense"][1:]]))
print(f"median prove {med['in_unit']['prove_s']:.4f} -> {med['in_unit+dense']['prove_s']:.4f} s; Python verify "
      f"{med['in_unit']['verify_py_s']:.3f} -> {med['in_unit+dense']['verify_py_s']:.3f} s", flush=True)
ok = all(r["python"] == "accept" for rs in timing.values() for r in rs)
del inst

zero = (0x00, 0x80) if FP8 else (0x0000, 0x8000)
cands = ((v, int(t)) for v in range(N) for t in np.nonzero(np.isin(W[v], zero))[0] if not (FP8 and (int(X[v, t]) & 0x7F) >= 0x7E))
alt = None
for tried, (v, t) in enumerate(cands):
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
ab = bits_of(alt_rows.units)
sd, pub = statement("gap_alt_operand")
cases = {}
for name, on in (("gap_alt_operand_in_unit", False), ("gap_alt_operand_dense", True)):
    inst = instance(sd, pub, torch.cat([alt_rows.units, ab], 1), alt_rows.epilogue)
    LINK["on"], LINK["bits"] = on, ab.reshape(-1).to(torch.uint8).contiguous()
    proof, _st = prover.prove(inst, True)
    try:
        prover.verify(inst, proof, True)
        py = "accept"
    except prover.VerifyError as e:
        py = f"reject ({str(e)[:90]})"
    want = "accept" if not on else "reject"
    cases[name] = {"python": py, "expected": want, "ok": py.startswith(want)}
    ok &= cases[name]["ok"]
    print(f"{name:24s} python={py} -> {'OK' if cases[name]['ok'] else 'UNEXPECTED'}", flush=True)
    del inst, proof

(OUT / "link_dense.json").write_text(json.dumps({"relation": C.relation, "vus": N, "link_bits": int(hb.numel()), "timing": timing,
                                                 "median": med, "altered": {"vu": v, "word": t}, "cases": cases, "ok": bool(ok)},
                                                indent=1, default=str))
print("LINK-DENSE OK" if ok else "LINK-DENSE FAILED", flush=True)
sys.exit(0 if ok else 1)
