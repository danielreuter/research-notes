#!/usr/bin/env bash
# agkr-table: A-GKR at the bf16-hopper relation (HOPPER_BF16_M16N8K16: one group of 16, 26-bit adder, floor -133; the
# H100 BF16 row), developed on the A100 (the Table 2 cell itself needs an H100):
#  1. the statement files at Params.from_model(HOPPER_BF16_M16N8K16)
#  2. the device witness generator vs the export's rows on 64 recipe VUs (model accumulators cross-checked per unit)
#  3. bench_result --relation bf16-hopper on the frozen recipe set [0, 4096), 2 reps, Python + Rust verifiers
#  4. negatives on the same 4096-VU batch: one VU's claimed word +1 ulp / -1 ulp / sign-flipped -> both verifiers reject
#  5. regression of the default path (frozen vu-k1536, Ampere circuits) through the restructured bench_result, 1 rep
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
H=/workspace/agkr-table/hopper
rm -rf $H; mkdir -p $H
echo "== 1. circuits"
$PY -m gpu.v2.export circuits --model hopper_bf16_m16n8k16 --out $H/stmt | cut -c1-300
echo "== 2. recipe parity"
$PY -m gpu.v2.witness recipe --relation bf16-hopper --vus 64 --procs 15 2>&1 | grep -v -i warn | head -20
echo "== 3. bench_result --relation bf16-hopper"
RESEARCH_RUN_DIR=$H/dev $PY bench_result.py $H/stmt --relation bf16-hopper --vus 4096 --reps 2 --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads 15 > $H/dev.log 2>&1
echo "bench_result rc=$?"
grep -E '^\{"(rep|warmup)"|verify rep|"t_total"|"status"|contract_problems|soundness_log2|Error|error' $H/dev.log | cut -c1-220 | tail -14
echo "== 4. negatives"
$PY - <<'EOF' 2>&1 | grep -v -i warn
import json, subprocess
from pathlib import Path

import numpy as np
import torch

import bench_result as br
from gpu import prover
from gpu.circuit import layers, load_circuit
from gpu.run import read_chain
from gpu.v2.witness import Generator, Ops

H = Path("/workspace/agkr-table/hopper")
d = H / "stmt"
man = json.loads((d / "manifest.json").read_text())
x, w, y, rel = br.load_relation("bf16-hopper", Path("/workspace/src"), 0, 4096, 15)
ops = Ops("cuda")
gen = Generator(ops, rel.params)
uc, ec = load_circuit(d / "circuit.txt"), load_circuit(d / "epilogue.txt")
ul, el = layers(uc), layers(ec)


def case(name, yy):
    rows = gen.run(ops.asarray(x), ops.asarray(w), ops.asarray(yy))
    bad = int(rows.bad.sum())
    inst = prover.Instance([prover.Segment("unit", uc, ul, rows.units, uc.hash),
                            prover.Segment("epilogue", ec, el, rows.epilogue, ec.hash)],
                           read_chain(d / "chain.txt", uc, ec, man["steps"], [int(v) for v in yy]))
    proof, _st = prover.prove(inst, True)
    try:
        prover.verify(inst, proof, True)
        py = "accept"
    except prover.VerifyError as e:
        py = f"reject ({str(e)[:70]})"
    sd = H / "neg" / name
    br.write_statement(d, sd, yy)
    (sd / "proof.bin").write_bytes(proof.to_bytes())
    out = sd / "verify.json"
    r = subprocess.run(["/workspace/bin/verity-gkr-verify", "verify", "--dir", str(sd), "--proof", str(sd / "proof.bin"),
                        "--vus", "4096", "--threads", "15", "--json", str(out)], capture_output=True, text=True)
    doc = json.loads(out.read_text()) if out.is_file() else {}
    rust = "accept" if (doc.get("accepted") and r.returncode == 0) else f"reject ({str(doc.get('error'))[:70]})"
    print(f"{name:14s} generator_bad={bad} python={py} rust={rust}", flush=True)
    return py == "accept", rust == "accept"


ok = case("honest", y) == (True, True)
for name, vu, f in (("ulp_plus", 5, lambda v: (v + 1) & 0xFFFF), ("ulp_minus", 17, lambda v: (v - 1) & 0xFFFF),
                    ("sign_flip", 33, lambda v: v ^ 0x8000)):
    yy = y.copy()
    yy[vu] = f(int(yy[vu]))
    ok &= case(name, yy) == (False, False)
print("NEGATIVES OK" if ok else "NEGATIVES FAILED", flush=True)
EOF
echo "== 5. default-path regression"
RESEARCH_RUN_DIR=$H/regress $PY bench_result.py /workspace/agkr-table/bb/stmt --instances /workspace/bench-instances/v1 --vus 4096 \
    --reps 1 --warmup 1 --verifier /workspace/bin/verity-gkr-verify --threads 15 > $H/regress.log 2>&1
echo "regress rc=$?"
grep -E '^\{"rep"|verify rep|"status"|contract_problems' $H/regress.log | cut -c1-160
cmp -s $H/regress/proofs/rep0.bin /workspace/research/runs/r20260924-071929-6745/proofs/rep0.bin && echo "regress: proof identical to r20260924-071929-6745" || echo "regress: PROOF DIFFERS"
