"""agkr-bound negatives of the operands-committed statement (gpu/commit.py, verifier commitments.rs), SCAFFOLD stage:
the digest columns are public words the verifier checks against the pinned frame-v3 roots, but no circuit layer binds
them to the operand columns yet.

usage (cwd <tree>/backends/gkr): python 10_commit_neg.py REL LEAF EXPORT_DIR OUT VERIFIER [N] [THREADS]
  REL: bf16-ampere (frozen vu-k1536, /workspace/bench-instances/v1) | bf16-hopper | fp8-ada | fp8-hopper | fp4-nvf4
  LEAF: sha256 | blake3.  The verifier must have REL+LEAF's root pin compiled in (commitments.rs PINS).

Cases (SC = --allow-any-circuit --require-commitment: no circuit set is pinned for REL+LEAF until the hash layers):
  honest            honest witness, honest digests, SC                                  -> accept, commitment pinned
  honest_as_RL      the same claimed --relation REL+LEAF                                -> reject (no circuit pin)
  honest_as_R       the same claimed --relation REL                                     -> reject
  wrong_digest      re-proved with VU v's x digest = VU v+1's (a consistent proof), SC -> reject (tree a); python accepts
  wrong_digest_up   the same, SC + --allow-unpinned-commitment                          -> accept (the root pin is what rejects)
  swap_w            re-proved with VU 0 / 1 W digests swapped, SC                       -> reject (tree b: ranks are VUs)
  y_word            honest proof, one y public word +1 in public.bin, SC                -> reject
  limb_range        honest proof, one limb set to 2^16 in public.bin, SC                -> reject (malformed)
  spec_manifest     commitment.txt with another instance-set digest, SC                 -> reject
  spec_leaf         commitment.txt naming the other leaf (and relation suffix), SC      -> reject
  no_commitment     the extended statement without commitment.txt, SC                   -> reject (--require-commitment)
  gap_alt_operand   altered operand word (w = +-0: public words honest) with the HONEST digests, SC
                                                                                        -> ACCEPT: the gap the hash layers close
  gap_structural    no gate, assertion or query of epilogue.txt reads a digest column   -> true until the hash layers
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch

import bench_result as br
from gpu import commit as CM
from gpu import prover
from gpu.bb_export import write_rows
from gpu.circuit import layers, load_circuit, parse_circuit
from gpu.run import read_chain

REL, LEAF, S, OUT, VB = sys.argv[1], sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5]
N = int(sys.argv[6]) if len(sys.argv) > 6 else 4096
NT = int(sys.argv[7]) if len(sys.argv) > 7 else 13
dev = torch.device("cuda")
OUT.mkdir(parents=True, exist_ok=True)
man = json.loads((S / "manifest.json").read_text())
steps = man["steps"]
uc = load_circuit(S / "circuit.txt")
ul = layers(uc)
etext = CM.extend_epilogue((S / "epilogue.txt").read_text())
ec = parse_circuit(etext)
el = layers(ec)
src = Path(br.__file__).resolve().parents[2]
frozen = src / "fixtures" / "bench-instances" / "v1" / "manifest.json"

if REL == "fp4-nvf4":
    from gpu.nvf4.circuit import statement as nvf4_statement
    from gpu.nvf4.witness import NVF4Generator, public_words

    A8, B8, Y32, _r, _c = br.load_nvf4(0, N, NT)
    gen = NVF4Generator(nvf4_statement(), dev)
    y = public_words(torch.from_numpy(Y32)).numpy().reshape(N, -1)
    X, W, yw = A8.reshape(N, -1).copy(), B8.reshape(N, -1), 4

    def rows_for(xx):
        return gen.run(torch.from_numpy(xx.reshape(A8.shape)).to(dev).long(), torch.from_numpy(B8).to(dev).long(),
                       torch.from_numpy(Y32).to(dev))

    def candidates():
        for v in range(N):
            for s in range(steps):
                for t in range(64):
                    if (int(W[v, 68 * s + t]) & 7) == 0:
                        yield v, 68 * s + t
else:
    from gpu.v2.fp8 import is_fp8, relation_params
    from gpu.v2.witness import Generator, Ops

    if REL == "bf16-ampere":
        from verity_numerical.checker import REAL

        x, W, y0, _ = br.load_frozen(Path("/workspace/bench-instances/v1"), frozen, br.TIER, 0, N)
        params = REAL
    else:
        x, W, y0, rel = br.load_relation(REL, src, 0, N, NT)
        params = relation_params(rel)[0]
    X = np.array(x, dtype=np.uint16)
    fp8 = is_fp8(params)
    yw = 4 if y0.dtype == np.uint32 else 2
    y = np.asarray(y0).reshape(N, 1)
    ops = Ops("cuda")
    gen = Generator(ops, params)

    def rows_for(xx):
        return gen.run(ops.asarray(xx), ops.asarray(W), ops.asarray(y0))

    def candidates():
        zero = (0x00, 0x80) if fp8 else (0x0000, 0x8000)
        for v in range(N):
            for t in np.nonzero(np.isin(W[v], zero))[0]:
                if fp8 and (int(X[v, t]) & 0x7F) >= 0x7E:
                    continue
                yield v, int(t)

iset = CM.instance_set(REL, 0, N, src, frozen, nvf4_k=X.shape[1] if REL == "fp4-nvf4" else None)
C = CM.commit(LEAF, REL, iset, 0, X, W, y, yw)
RL = C.relation
SC = ("--allow-any-circuit", "--require-commitment")
print(f"{RL}: roots a {C.roots['a'].hex()[:16]} b {C.roots['b'].hex()[:16]} y {C.roots['y'].hex()[:16]}", flush=True)


def statement(name: str, limb_cols: np.ndarray, commitment_text: str | None = C.text()):
    sd = OUT / name
    if sd.exists():
        shutil.rmtree(sd)
    br.write_statement(S, sd, [0] * N)
    (sd / "epilogue.txt").write_text(etext)
    (sd / "chain.txt").write_text(CM.extend_chain((S / man.get("chain_file", "chain.txt")).read_text()))
    pub = np.concatenate([np.asarray(y, dtype=np.int64), limb_cols], 1)
    write_rows(pub.tolist(), sd / "public.bin")
    if commitment_text is not None:
        (sd / "commitment.txt").write_text(commitment_text)
    return sd, pub


def prove(sd: Path, rows, limb_cols: np.ndarray, pub: np.ndarray):
    ch = read_chain(sd / "chain.txt", uc, ec, steps, [int(v) for v in pub.reshape(-1)])
    ct = sd / "commitment.txt"
    ch.commit_digest = hashlib.sha256(ct.read_bytes()).digest() if ct.is_file() else None
    epi = torch.cat([rows.epilogue, torch.from_numpy(limb_cols).to(dev)], 1)
    inst = prover.Instance([prover.Segment("unit", uc, ul, rows.units, uc.hash),
                            prover.Segment("epilogue", ec, el, epi, ec.hash)], ch)
    proof, _st = prover.prove(inst, True)
    try:
        prover.verify(inst, proof, True)
        py = "accept"
    except prover.VerifyError as e:
        py = f"reject ({str(e)[:80]})"
    (sd / "proof.bin").write_bytes(proof.to_bytes())
    return py


def rust(sd: Path, tag: str, *flags, proof: Path | None = None):
    out = sd / f"verify_{tag}.json"
    r = subprocess.run([VB, "verify", "--dir", str(sd), "--proof", str(proof or sd / "proof.bin"), "--vus", str(N), "--threads", str(NT),
                        "--json", str(out), *flags], capture_output=True, text=True)
    doc = json.loads(out.read_text()) if out.is_file() else {}
    return bool(doc.get("accepted")) and r.returncode == 0, doc.get("error") or r.stderr[-200:] or None, doc


results = {}


def record(name, want_rust, got, err, py=None, want_py=None, **kw):
    ok = got == want_rust and (want_py is None or (py == "accept") == want_py)
    results[name] = {"rust": "accept" if got else "reject", "rust_error": err, "python": py,
                     "expected_rust": "accept" if want_rust else "reject", "ok": ok, **kw}
    print(f"{name:18s} rust={'accept' if got else 'reject'} ({err}) python={py} -> {'OK' if ok else 'UNEXPECTED'}", flush=True)
    return ok


ok = True
honest_rows = rows_for(X)
assert int(honest_rows.bad.sum()) == 0
L = C.limb_columns()

sd, pub = statement("honest", L)
py = prove(sd, honest_rows, L, pub)
got, err, doc = rust(sd, "sc", *SC)
pinned = (doc.get("commitment") or {}).get("pinned")
ok &= record("honest", True, got, err, py, True, commitment_pinned=pinned, committed=doc.get("operands_committed"))
ok &= bool(pinned)
honest = sd
got, err, _ = rust(sd, "as_rl", "--relation", RL)
ok &= record("honest_as_RL", False, got, err)
got, err, _ = rust(sd, "as_r", "--relation", REL)
ok &= record("honest_as_R", False, got, err)

L2 = L.copy()
L2[17, :16] = L[18, :16]
sd, pub = statement("wrong_digest", L2)
py = prove(sd, honest_rows, L2, pub)
got, err, _ = rust(sd, "sc", *SC)
ok &= record("wrong_digest", False, got, err, py, True)
got, err, _ = rust(sd, "up", *SC, "--allow-unpinned-commitment")
ok &= record("wrong_digest_up", True, got, err)

L3 = L.copy()
L3[[0, 1], 16:] = L[[1, 0], 16:]
sd, pub = statement("swap_w", L3)
py = prove(sd, honest_rows, L3, pub)
got, err, _ = rust(sd, "sc", *SC)
ok &= record("swap_w", False, got, err, py, True)

ny = y.shape[1]
for name, col, val in (("y_word", 0, None), ("limb_range", ny + 3, 1 << 16)):
    sd, pub = statement(name, L)
    p2 = pub.copy()
    p2[5, col] = val if val is not None else (int(p2[5, col]) + 1) % (1 << (8 * yw))
    write_rows(p2.tolist(), sd / "public.bin")
    got, err, _ = rust(sd, "sc", *SC, proof=honest / "proof.bin")
    ok &= record(name, False, got, err)

other = "blake3" if LEAF == "sha256" else "sha256"
for name, text in (("spec_manifest", re.sub(r"(instances \S+ \S+ )[0-9a-f]{64}", lambda m: m.group(1) + "cd" * 32, C.text())),
                   ("spec_leaf", C.text().replace(f"leaf {LEAF}", f"leaf {other}").replace(CM.SUFFIX[LEAF], CM.SUFFIX[other])),
                   ("no_commitment", None)):
    sd, pub = statement(name, L, text)
    got, err, _ = rust(sd, "sc", *SC, proof=honest / "proof.bin")
    ok &= record(name, False, got, err)

alt = None
for tried, (v, t) in enumerate(candidates()):
    if tried >= 12:
        break
    xx = X.copy()
    xx[v, t] ^= 1
    rows = rows_for(xx)
    bad = int(rows.bad.sum())
    print(f"candidate VU {v} word {t}: x {int(X[v, t]):#x} -> {int(xx[v, t]):#x} (w {int(W[v, t]):#x}); generator bad = {bad}", flush=True)
    if bad == 0:
        alt = (v, t, xx, rows)
        break
    del rows
if alt is None:
    raise SystemExit("no altered operand keeps the public words honest")
v, t, xalt, alt_rows = alt
where = {"vu": v, "word": t, "x_frozen": int(X[v, t]), "x_altered": int(xalt[v, t]), "w": int(W[v, t])}
sd, pub = statement("gap_alt_operand", L)
py = prove(sd, alt_rows, L, pub)
got, err, _ = rust(sd, "sc", *SC)
ok &= record("gap_alt_operand", True, got, err, py, True, **where, note="EXPECTED ACCEPT until hash layers bind the digest columns")

dcols = {ec.col_index(n) for n in CM.DIGEST_COLS}
dwires = {i for i, w in enumerate(ec.wires) if w[0] == "in" and w[1] in dcols}
wire_refs = {i for w in ec.wires if w[0] == "prod" for lin in w[2:4] for i, _ in lin.terms}
wire_refs |= {i for _, lin in ec.asserts for i, _ in lin.terms}
col_refs = {i for q in ec.queries for lin in q.cols for i, _ in lin.terms}
free = not (dwires & wire_refs) and not (dcols & col_refs)
results["gap_structural"] = {"digest_columns_free": free, "digest_wires": sorted(dwires), "ok": len(dwires) == 32}
ok &= len(dwires) == 32
print(f"gap_structural     digest columns referenced by no gate / assertion / query: {free} ({len(dwires)} digest wires)", flush=True)

(OUT / "negatives.json").write_text(json.dumps({"relation": RL, "vus": N, "altered": where, "roots": {k: r.hex() for k, r in C.roots.items()},
                                                 "cases": results, "ok": bool(ok)}, indent=1))
print("NEGATIVES OK" if ok else "NEGATIVES FAILED", flush=True)
sys.exit(0 if ok else 1)
