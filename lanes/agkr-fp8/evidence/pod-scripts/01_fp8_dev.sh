#!/usr/bin/env bash
# agkr-fp8: A-GKR at an E4M3 relation, development pass on the pod ($1 = fp8-ada | fp8-hopper, $2 = VUs, default 4096):
#  0. the independent Rust verifier (backends/gkr/verifier) -> /workspace/bin/verity-gkr-verify
#  1. the statement files at the model's adder-side view (gpu.v2.export circuits)
#  2. the device witness generator vs the export's rows on 64 recipe VUs (silicon-model accumulators checked per unit)
#  3. bench_result --relation $1 on the frozen recipe set [0, $2), 2 reps, Python + Rust verifiers
#  4. negatives on the same batch: one VU's claimed packed word +1 / -1 / sign-flipped -> both verifiers reject
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-ada}; N=${2:-4096}
case $REL in fp8-ada) MODEL=ada_e4m3_m16n8k32;; fp8-hopper) MODEL=hopper_e4m3_wgmma_k32;; *) echo "bad relation"; exit 2;; esac
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
H=/workspace/agkr-fp8/$REL
mkdir -p $H /workspace/bin
T=$(nproc)
echo "== 0. verifier build ($(date -u +%H:%M:%S))"
if [ ! -x /workspace/bin/verity-gkr-verify ] || [ -n "${REBUILD:-}" ]; then
  ( cd verifier && cargo build --release 2>&1 | tail -2 ) && cp $CARGO_TARGET_DIR/release/verity-gkr-verify /workspace/bin/
fi
sha256sum /workspace/bin/verity-gkr-verify
echo "== 1. circuits ($(date -u +%H:%M:%S))"
rm -rf $H/stmt
$PY -m gpu.v2.export circuits --model $MODEL --out $H/stmt | cut -c1-400
echo "== 2. recipe parity ($(date -u +%H:%M:%S))"
$PY -m gpu.v2.witness recipe --relation $REL --vus 64 --procs 16 2>&1 | grep -v -i warn | head -24
echo "== 3. bench_result --relation $REL --vus $N ($(date -u +%H:%M:%S))"
rm -rf $H/dev
RESEARCH_RUN_DIR=$H/dev $PY bench_result.py $H/stmt --relation $REL --vus $N --reps 2 --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads 16 > $H/dev.log 2>&1
echo "bench_result rc=$? ($(date -u +%H:%M:%S))"
grep -E '^\{"(rep|warmup)"|verify rep|"t_total"|"status"|contract_problems|soundness_log2|Error|error|Traceback' $H/dev.log | cut -c1-400 | tail -16
tail -5 $H/dev.log | cut -c1-400
[ -n "${SKIP_NEG:-}" ] && exit 0
echo "== 4. negatives ($(date -u +%H:%M:%S))"
REL=$REL N=$N H=$H $PY - <<'PYEOF' 2>&1 | grep -v -i warn
import json, os, subprocess
from pathlib import Path

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
                        "--vus", str(N), "--threads", "16", "--json", str(out)], capture_output=True, text=True)
    doc = json.loads(out.read_text()) if out.is_file() else {}
    rust = "accept" if (doc.get("accepted") and r.returncode == 0) else f"reject ({str(doc.get('error'))[:70]})"
    print(f"{name:14s} generator_bad={bad} python={py} rust={rust}", flush=True)
    return py == "accept", rust == "accept"


ok = case("honest", y) == (True, True)
M22 = (1 << 22) - 1
for name, vu, f in (("word_plus", 5, lambda v: (v + 1) & M22), ("word_minus", 17, lambda v: (v - 1) & M22),
                    ("sign_flip", 33, lambda v: v ^ (1 << 21)), ("exp_plus", 49, lambda v: (v + (1 << 13)) & M22)):
    yy = y.copy()
    yy[vu] = f(int(yy[vu]))
    ok &= case(name, yy) == (False, False)
print("NEGATIVES OK" if ok else "NEGATIVES FAILED", flush=True)
PYEOF
echo "== done ($(date -u +%H:%M:%S))"
