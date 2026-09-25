"""agkr-bound negatives: a wrong operand word with the honest public words.

usage (cwd <tree>/backends/gkr): python 03_negatives.py REL EXPORT_DIR OUT VERIFIER [N] [THREADS]
  REL: vu-k1536 (the frozen BF16 tier, /workspace/bench-instances/v1) | bf16-hopper | fp8-ada | fp8-hopper | fp4-nvf4

One VU's x word at a position whose w word is +-0 has its lowest bit flipped (same exponent field, still finite), so the
product stays 0 and the frozen public words stay honest: the device generator accepts the altered operands (bad == 0)
and an honest proof of THEM exists.  Cases (each proved from the altered witness unless noted):
  honest        bound statement, frozen x.bin, the frozen witness                          -> accept (both verifiers)
  unbound_alt   no bind.txt (the old statement): the altered witness                       -> ACCEPT: the gap being closed
  bound_alt     bound statement, frozen x.bin (pinned)                                      -> reject (both verifiers)
  alt_xbin      bound statement whose x.bin IS the altered words (not the frozen set)       -> reject (pin);
                the same with --allow-unpinned-instances                                    -> accept (the functional is consistent)
  mutate        verity-gkr-verify mutate --sample 2 on the honest bound proof (incl. a frozen x word changed) -> all rejected
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch

import bench_result as br
from gpu import bind as BD
from gpu import prover
from gpu.circuit import layers, load_circuit
from gpu.field import P
from gpu.run import read_chain

REL, S, OUT, VB = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
N = int(sys.argv[5]) if len(sys.argv) > 5 else 4096
NT = int(sys.argv[6]) if len(sys.argv) > 6 else 13
dev = torch.device("cuda")
OUT.mkdir(parents=True, exist_ok=True)
man = json.loads((S / "manifest.json").read_text())
steps = man["steps"]
uc, ec = load_circuit(S / "circuit.txt"), load_circuit(S / "epilogue.txt")
ul, el = layers(uc), layers(ec)
src = Path(br.__file__).resolve().parents[2]

if REL == "fp4-nvf4":
    from gpu.nvf4.circuit import statement as nvf4_statement
    from gpu.nvf4.witness import NVF4Generator, public_words

    A8, B8, Y32, _r, _c = br.load_nvf4(0, N, NT)
    gen = NVF4Generator(nvf4_statement(), dev)
    y = public_words(torch.from_numpy(Y32)).numpy()
    X, W, xdt, ydt = A8.reshape(N, -1).copy(), B8.reshape(N, -1), "u8", "u32"

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

    if REL == "vu-k1536":
        from verity_numerical.checker import REAL

        x, W, y, _ = br.load_frozen(Path("/workspace/bench-instances/v1"), src / "fixtures" / "bench-instances" / "v1" / "manifest.json",
                                    REL, 0, N)
        params = REAL
    else:
        x, W, y, rel = br.load_relation(REL, src, 0, N, NT)
        params = relation_params(rel)[0]
    X = np.array(x, dtype=np.uint16)
    fp8 = is_fp8(params)
    xdt, ydt = "u16", ("u32" if y.dtype == np.uint32 else "u16")
    ops = Ops("cuda")
    gen = Generator(ops, params)

    def rows_for(xx):
        return gen.run(ops.asarray(xx), ops.asarray(W), ops.asarray(y))

    def candidates():
        zero = (0x00, 0x80) if fp8 else (0x0000, 0x8000)
        for v in range(N):
            for t in np.nonzero(np.isin(W[v], zero))[0]:
                if fp8 and (int(X[v, t]) & 0x7F) >= 0x7E:
                    continue                                   # 0x7F / 0xFF is E4M3 NaN
                yield v, int(t)

public = [int(v) for v in np.asarray(y).reshape(-1)]


def statement(name: str, xx, bound: bool):
    sd = OUT / name
    br.write_statement(S, sd, y)
    if not bound:
        return sd, None
    (sd / "bind.txt").write_text(BD.spec_text(BD.derive(uc, man)))
    spec = BD.read_spec(sd / "bind.txt", uc)
    BD.write_instances(sd, REL, 0, xx, W, np.asarray(public, dtype=np.int64), xdt, ydt)
    return sd, prover.Bind(spec.cols, BD.digests(sd), torch.from_numpy(BD.values(spec, xx, W, steps, P)).to(dev))


def prove(rows, bind):
    ch = read_chain(S / man.get("chain_file", "chain.txt"), uc, ec, steps, public)
    ch.bind = bind
    inst = prover.Instance([prover.Segment("unit", uc, ul, rows.units, uc.hash),
                            prover.Segment("epilogue", ec, el, rows.epilogue, ec.hash)], ch)
    proof, _st = prover.prove(inst, True)
    try:
        prover.verify(inst, proof, True)
        py = "accept"
    except prover.VerifyError as e:
        py = f"reject ({str(e)[:80]})"
    clear = None
    if bind is not None:
        try:
            prover.verify(inst, proof, False)
            clear = "accept"
        except prover.VerifyError as e:
            clear = f"reject ({str(e)[:80]})"
    return proof.to_bytes(), py, clear


def rust(sd: Path, pf: Path, tag: str, *flags) -> tuple[bool, str | None]:
    out = sd / f"verify_{tag}.json"
    r = subprocess.run([VB, "verify", "--dir", str(sd), "--proof", str(pf), "--vus", str(N), "--threads", str(NT),
                        "--json", str(out), *flags], capture_output=True, text=True)
    doc = json.loads(out.read_text()) if out.is_file() else {}
    return bool(doc.get("accepted")) and r.returncode == 0, doc.get("error") or r.stderr[-200:] or None


results = {}


def record(name, want_rust, got_rust, err, py=None, want_py=None, clear=None, **kw):
    ok = got_rust == want_rust and (want_py is None or (py == "accept") == want_py)
    results[name] = {"rust": "accept" if got_rust else "reject", "rust_error": err, "python": py, "python_clear": clear,
                     "expected_rust": "accept" if want_rust else "reject", "ok": ok, **kw}
    print(f"{name:22s} rust={'accept' if got_rust else 'reject'} ({err}) python={py} clear={clear} -> {'OK' if ok else 'UNEXPECTED'}", flush=True)
    return ok


honest_rows = rows_for(X)
assert int(honest_rows.bad.sum()) == 0
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

ok = True
sd, bd = statement("honest", X, True)
data, py, clear = prove(honest_rows, bd)
(sd / "proof.bin").write_bytes(data)
got, err = rust(sd, sd / "proof.bin", "require_bound", "--require-bound")
ok &= record("honest", True, got, err, py, True, clear)
honest_dir = sd

sd, _ = statement("unbound_alt", X, False)
data, py, _ = prove(alt_rows, None)
(sd / "proof.bin").write_bytes(data)
got, err = rust(sd, sd / "proof.bin", "plain")
ok &= record("unbound_alt", True, got, err, py, True, **where)
got, err = rust(sd, sd / "proof.bin", "require_bound", "--require-bound")
ok &= record("unbound_alt_required", False, got, err)

sd, bd = statement("bound_alt", X, True)
data, py, clear = prove(alt_rows, bd)
(sd / "proof.bin").write_bytes(data)
got, err = rust(sd, sd / "proof.bin", "require_bound", "--require-bound")
ok &= record("bound_alt", False, got, err, py, False, clear, **where)

sd, bd = statement("alt_xbin", xalt, True)
data, py, clear = prove(alt_rows, bd)
(sd / "proof.bin").write_bytes(data)
got, err = rust(sd, sd / "proof.bin", "require_bound", "--require-bound")
ok &= record("alt_xbin", False, got, err, py, True, clear, **where)
got, err = rust(sd, sd / "proof.bin", "unpinned", "--require-bound", "--allow-unpinned-instances")
ok &= record("alt_xbin_unpinned", True, got, err)

r = subprocess.run([VB, "mutate", "--dir", str(honest_dir), "--proof", str(honest_dir / "proof.bin"), "--vus", str(N),
                    "--threads", str(NT), "--sample", "2", "--json", str(OUT / "mutate.json")], capture_output=True, text=True)
print(r.stdout[-1200:], flush=True)
mj = json.loads((OUT / "mutate.json").read_text()) if (OUT / "mutate.json").is_file() else {}
mok = r.returncode == 0 and mj.get("rejected") == mj.get("total") and mj.get("groups", {}).get("statement", {}).get("total") == 3
results["mutate"] = {"rejected": mj.get("rejected"), "total": mj.get("total"), "groups": mj.get("groups"), "ok": mok}
ok &= mok
(OUT / "negatives.json").write_text(json.dumps({"relation": REL, "vus": N, "altered": where, "cases": results, "ok": bool(ok)}, indent=1))
print("NEGATIVES OK" if ok else "NEGATIVES FAILED", flush=True)
sys.exit(0 if ok else 1)
