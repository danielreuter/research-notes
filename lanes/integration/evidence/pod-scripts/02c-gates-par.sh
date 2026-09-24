#!/usr/bin/env bash
# integration merge-val-3 (b): the remaining gate cells of 02-gates.sh, same command, in parallel runners (gates are
# CPU-bound; the sequential loop would not finish in the window). Usage: 02c-gates-par.sh cell... (cell = rel-{bare,hash,shared})
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/integration/gates; mkdir -p $O
run() {  # name, relation, extra args...
  local name=$1 rel=$2; shift 2
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel gate-vu --vus 4096 --batch 16384 --zk --mode interactive \
      --out $O/$name.json "$@" > $O/$name.log 2>&1
  local rc=$?
  echo "$name rc=$rc $(( $(date +%s) - t0 ))s :: $(grep -E 'gate: .* failures' $O/$name.log | tail -1)" | tee -a $O/summary.txt
}
for cell in "$@"; do
  rel=${cell%-*}; kind=${cell##*-}
  case $kind in
    bare) if [ $rel = fp8-ada-v3x4 ]; then run $cell $rel --batch 4096; else run $cell $rel; fi ;;
    hash) run $cell $rel --auth included-hash ;;
    shared) run $cell $rel --auth included-hash-shared --tile 64x64 ;;
  esac
done
echo "RUNNER_DONE $*" | tee -a $O/summary.txt
