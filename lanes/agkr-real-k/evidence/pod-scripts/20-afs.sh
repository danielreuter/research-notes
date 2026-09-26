#!/usr/bin/env bash
# agkr-real-k: A-fs (A-GKR alone on the GPU, Fiat-Shamir coins, x and W private: the weaker statement, a drill-down) at vLLM's
# reduction lengths on the #101 captured sets: the export at K (gpu.v2.export circuits --k K), bench_result.py --input-set over the
# whole set in one proof, the pinned Rust verifier (relation bf16-ampere-k<K>) on every rep.  Runs from the shipped tree after
# backends/gkr/cell.sh set the pod up (venv, env.sh).  outputs.json publishes each K's result.json as bench-result/v1.
#   SETS="<tarball under inputs/> <art id> ..." (pairs)  REPS=5  LANE=agkr-real-k
set -uo pipefail
REPO=$(pwd); RD=${RESEARCH_RUN_DIR:?}; W=/workspace; O=$RD/out; mkdir -p $O
source $W/env.sh; cd "$REPO"
export PYTHONPATH="$PYTHONPATH:$REPO/backends/gkr" PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
VB=$W/bin/verity-gkr-verify-live
( cd backends/gkr/verifier && cargo build --release 2>&1 | grep -E '^error|Finished' && cp ${CARGO_TARGET_DIR:-target}/release/verity-gkr-verify $VB )
sha256sum $VB | tee $O/verifier.sha256
set -- ${SETS:?}
i=0
while [ $# -ge 2 ]; do
  t=$1; art=$2; shift 2
  mkdir -p $RD/set/$i && tar -xf $RD/inputs/$t -C $RD/set/$i
  S=$(dirname "$(find $RD/set/$i -name manifest.json | head -1)")
  read -r K N < <($PY -c "import json,sys;m=json.load(open(sys.argv[1]+'/manifest.json'));print(m['relation']['statics']['K'], m['n'])" "$S")
  D=$W/afs/export-k$K; rm -rf $D
  $PY -m gpu.v2.export circuits --model ampere_bf16_m16n8k16 --k $K --out $D > /dev/null || exit 1
  mkdir -p $O/k$K
  echo "##### $(date -u +%H:%M:%SZ) A-fs K=$K: $N VUs of $S ($art)"
  ( cd backends/gkr && RESEARCH_RUN_DIR=$O/k$K $PY bench_result.py $D --input-set $S --input-set-art $art --vus $N --reps ${REPS:-5} \
      --warmup 1 --verifier $VB --threads $TH ) > $O/k$K/bench.log 2>&1
  echo "rc=$?"; tail -12 $O/k$K/bench.log | cut -c1-300
  i=$((i + 1))
done
rm -rf $RD/set
$PY - "$RD" "${LANE:-agkr-real-k}" <<'PY'
import json, sys
from pathlib import Path
rd, lane = Path(sys.argv[1]), sys.argv[2]
outs = []
for rj in sorted((rd / "out").glob("k*/result.json")):
    doc = json.loads(rj.read_text())
    fp = doc["workload_fingerprint"]
    doc.update(lane=lane, registered_by=lane, label=f"{lane} A-fs {fp['software']['backend']['relation']} {fp['B']} VUs (drill-down: x, W private)")
    outs.append({"name": f"afs-k{fp['K']}", "kind": "bench-result/v1", "meta": doc})
(rd / "outputs.json").write_text(json.dumps({"schema": "research/outputs/v0.1", "outputs": outs}, indent=1, default=str))
print(f"outputs.json: {len(outs)} A-fs results")
PY
