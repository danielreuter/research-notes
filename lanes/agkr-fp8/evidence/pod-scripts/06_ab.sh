#!/usr/bin/env bash
# agkr-fp8: A/B of the prover on the current /workspace/src ($1 = fp8-ada | fp8-hopper, $2 = VUs): 5 proves of the recipe batch
# (first untimed), Stats per prove and the proof sha256 (must equal the recorded cell's for a byte-identical change).
# BF16=1 also runs bench_result --relation bf16-hopper (1 rep, Rust verifier) to compare with the recorded BF16 H100 proof bytes.
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-hopper}; N=${2:-4096}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
REL=$REL N=$N H=${H:-/workspace/agkr-fp8/$REL} $PY - <<'EOF' 2>&1 | grep -v -i -E "warn|searchsorted"
import gc, hashlib, json, os, statistics, time
from pathlib import Path

import torch

import bench_result as br
from gpu import prover
from gpu.circuit import layers, load_circuit
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
ul, el = layers(uc), layers(ec)
rows = gen.run(ops.asarray(x), ops.asarray(w), ops.asarray(y))
inst = prover.Instance([prover.Segment("unit", uc, ul, rows.units, uc.hash),
                        prover.Segment("epilogue", ec, el, rows.epilogue, ec.hash)],
                       read_chain(d / "chain.txt", uc, ec, man["steps"], [int(v) for v in y]))
KEYS = ("t_mults", "t_commit", "t_lookup", "t_arith", "t_witness_wires", "t_open_acc", "t_open_wq", "t_open_cols")
tots, shas = [], set()
for i in range(5):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize()
    tt = time.perf_counter() - t0
    b = proof.to_bytes()
    shas.add(hashlib.sha256(b).hexdigest())
    if i == 0:
        gc.collect()
        gc.freeze()
        prover.verify(inst, proof, True)
        continue
    tots.append(tt)
    print(f"prove {i}: {tt:.4f}s  " + "  ".join(f"{k[2:]}={getattr(st, k):.4f}" for k in KEYS), flush=True)
print(f"median prove {statistics.median(tots):.4f}s  proof sha256 {sorted(shas)}  bytes {len(b)}", flush=True)
EOF
if [ -n "${BF16:-}" ]; then
  B=/workspace/agkr-fp8/bf16-hopper
  [ -d $B/stmt ] || $PY -m gpu.v2.export circuits --model hopper_bf16_m16n8k16 --out $B/stmt > /dev/null
  rm -rf $B/ab
  RESEARCH_RUN_DIR=$B/ab $PY bench_result.py $B/stmt --relation bf16-hopper --vus 4096 --reps 1 --warmup 1 \
      --verifier /workspace/bin/verity-gkr-verify --threads 16 > $B/ab.log 2>&1
  echo "bf16-hopper bench rc=$?"
  grep -E '^\{"rep"|verify rep|"status"' $B/ab.log | grep -o -E '"t_total": [0-9.]+|"proof_sha256": "[0-9a-f]+"|verify rep.*|"status": "[a-z]+"'
fi
