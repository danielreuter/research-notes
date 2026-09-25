#!/usr/bin/env bash
# agkr-fp8: lookup negatives on a merged FP8 statement ($H/stmt, one LK table): one unit's column read by an LK query is
# changed by +1 (a T_OP / SHIFT / TNORM output, an R5 key term) and the prover is handed the *honest* multiplicities
# (logup.multiplicities patched), and runs from a copy of the prover whose LogUp self-check ("fractional sum is not zero")
# is a no-op, so the proof is what a cheating prover would send (root claimed (0, q)); Python and Rust must both reject.
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-ada}; N=${2:-4096}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
NS=/workspace/agkr-fp8/negsrc
rm -rf $NS && mkdir -p $NS && cd /workspace/src/backends/gkr && cp -r *.py gpu packed tensor tools $NS/
sed -i 's/raise ValueError("LogUp: fractional sum is not zero (a query is not in its table)")/pass  # cheating prover/' \
    $NS/gpu/logup_packed.py $NS/gpu/logup.py
grep -c "pass  # cheating prover" $NS/gpu/logup_packed.py $NS/gpu/logup.py
cd $NS
export PYTHONPATH=$NS:$PYTHONPATH
REL=$REL N=$N H=${H:-/workspace/agkr-fp8/$REL} $PY - <<'EOF' 2>&1 | grep -v -i -E "warn|searchsorted"
import json, os, subprocess
from pathlib import Path

import bench_result as br
from gpu import logup, prover
from gpu.circuit import P, layers, load_circuit
from gpu.run import read_chain
from gpu.v2.fp8 import relation_params
from gpu.v2.witness import Generator, Ops

REL, N, H = os.environ["REL"], int(os.environ["N"]), Path(os.environ["H"])
d = H / "stmt"
man = json.loads((d / "manifest.json").read_text())
x, w, y, rel = br.load_relation(REL, Path("/workspace/src"), 0, N, 16)
p, _ = relation_params(rel)
ops = Ops("cuda")
gen = Generator(ops, p)
uc, ec = load_circuit(d / "circuit.txt"), load_circuit(d / "epilogue.txt")
assert [t.name for t in uc.tables] == ["LK"], [t.name for t in uc.tables]
ul, el = layers(uc), layers(ec)
rows = gen.run(ops.asarray(x), ops.asarray(w), ops.asarray(y))
chain = read_chain(d / "chain.txt", uc, ec, man["steps"], [int(v) for v in y])


def inst_of(units):
    return prover.Instance([prover.Segment("unit", uc, ul, units, uc.hash),
                            prover.Segment("epilogue", ec, el, rows.epilogue, ec.hash)], chain)


honest = inst_of(rows.units)
dev = honest.device
real_mults = logup.multiplicities
m_honest = {t.name: real_mults(t, logup.table_rows(t, dev), [v for v in prover.seg_query_values(honest, t.name) if v is not None])
            for t in honest.tables}
logup.multiplicities = lambda t, trows, vals: m_honest[t.name].clone()

first = {}
for q in uc.queries:
    first.setdefault(q.cols[1].konst, q)
import tempfile
from gpu.v2 import export as EX
MODEL = {"fp8-ada": "ada_e4m3_m16n8k32", "fp8-hopper": "hopper_e4m3_wgmma_k32"}[REL]
with tempfile.TemporaryDirectory() as td:
    EX.circuits(Path(td), MODEL, merge=False)
    names = sorted({q.table for q in load_circuit(Path(td) / "circuit.txt").queries})
tags = {name: i for i, name in enumerate(names, 1)}
rng = next(n for n in names if n.startswith("R"))
print("tags", tags, flush=True)


def out_col(q):
    return next(l.terms[0][0] for l in reversed(q.cols[2:]) if l.terms)


cases = {"t_op_out": out_col(first[tags["T_OP"]]), "shift_out": out_col(first[tags["SHIFT"]]),
         "tnorm_out": out_col(first[tags["TNORM"]]), f"{rng.lower()}_key": first[tags[rng]].cols[0].terms[0][0]}
U = 7 * man["steps"] + 3
ok = True
for name, col in cases.items():
    units = rows.units.clone()
    units[U, col] = (units[U, col] + 1) % P
    inst = inst_of(units)
    proof, _st = prover.prove(inst, True)
    try:
        prover.verify(inst, proof, True)
        py = "accept"
    except prover.VerifyError as e:
        py = f"reject ({str(e)[:80]})"
    sd = H / "lookup_neg" / name
    br.write_statement(d, sd, y)
    (sd / "proof.bin").write_bytes(proof.to_bytes())
    out = sd / "verify.json"
    r = subprocess.run(["/workspace/bin/verity-gkr-verify", "verify", "--dir", str(sd), "--proof", str(sd / "proof.bin"),
                        "--vus", str(N), "--threads", "10", "--json", str(out)], capture_output=True, text=True)
    doc = json.loads(out.read_text()) if out.is_file() else {}
    rust = "accept" if (doc.get("accepted") and r.returncode == 0) else f"reject ({str(doc.get('error'))[:80]})"
    print(f"{name:10s} unit={U} col={col} ({uc.col_names[col]}) python={py} rust={rust}", flush=True)
    ok &= py != "accept" and rust != "accept"
print("LOOKUP NEGATIVES OK" if ok else "LOOKUP NEGATIVES FAILED", flush=True)
EOF
