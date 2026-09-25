#!/usr/bin/env bash
# x4-hopper-blake3: on the pinned tree (leaf.rs PINS rows committed + synced): 15-rust.sh (rebuild, cargo test, pinned batch
# verify of 01-boot-pins.sh's fixtures, FIX_RUN), then the TABLES.md sweeps (sweep_vu from 1024, --commit-per-rep, 5 reps,
# plateau rep-1 dumped + the pod's pinned ligero-verify, a producer check), then the instance-equiv/v1 document of each
# plateau n (--check re-derived), then outputs.json: every point a bench-result/v1, the plateau's proofs a run-files/v1,
# each equiv document an instance-equiv/v1 (never labelled verified here).
# research run --on vy-x4-hopper-blake3-h100 --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h \
#     --send lib.sh --send 15-rust.sh --send 50-outputs.py --send 20-pinned-sweeps.sh --env FIX_RUN=<01 run id> \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/20-pinned-sweeps.sh"'
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}
if [ -n "${FIX_RUN:-}" ]; then (bash "$IN/15-rust.sh"); echo "rust rc=$?"; fi
cd /workspace/src
source "$IN/lib.sh"
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
rc=0
mkdir -p $RD/outputs
for s in ${SWEEPS:-fp8-hopper-x4+blake3:4096:4 bf16-hopper-x4+blake3:4096:4}; do
  IFS=: read -r REL L PP <<<"$s"; tag=$(echo "$REL-l$L-p$PP" | tr '+' '_'); SD=$RD/$tag
  gpu_idle || exit 3
  echo "##### $(date -u +%H:%M:%SZ) sweep $tag"
  $PY -m backends.direct.ligero.sweep_vu --relation $REL --out-dir $SD --start ${START:-1024} --max ${MAX:-131072} --dump plateau -- \
      --zk --mode interactive --auth included-hash --commit-per-rep --batch $L --pipeline $PP --target -128 --reps ${REPS:-5} \
      --device cuda --instance-procs ${IPROCS:-16} > $SD.log 2>&1
  r=$?; [ $r -ne 0 ] && rc=$r
  echo "sweep rc=$r"; grep -E "plateau|point|stopped" $SD.log | tail -n 12 | cut -c1-300
  read -r pl n < <($PY -c "import json;d=json.load(open('$SD/sweep.json'));p=[p for p in d['points'] if p['point']==d['plateau_point']][0];print(p['dir'],p['total_vus'])") || continue
  ( cd $SD/$pl/proofs || exit 1
    $V system-digest --system system.bin > rust_digest.json 2> rust_digest.err; echo "system-digest rc=$? $(head -c 300 rust_digest.json)"
    t1=$(date +%s)
    $V batch --system system.bin --dir rep1 --jobs $NT --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1
    echo "rust batch rc=$? wall=$(( $(date +%s) - t1 ))s $(tail -n 1 rust_batch.out | cut -c1-300)"
    sha256sum $V > ligero_verify.sha256 )
  base=${REL%%+*}; E=$RD/outputs/instance-equiv-$base-$n.json
  echo "##### $(date -u +%H:%M:%SZ) instance-equiv $base n=$n"
  $PY -m verity_numerical.bench.instance_equiv --relation $base --vus $n --procs $NT --out $E 2>&1 | tail -n 3
  $PY -m verity_numerical.bench.instance_equiv --check $E --vus $n --procs $NT 2>&1 | tail -n 3
  echo "equiv check rc=${PIPESTATUS[0]}"
done
$PY "$IN/50-outputs.py" $RD x4-hopper-blake3
exit $rc
