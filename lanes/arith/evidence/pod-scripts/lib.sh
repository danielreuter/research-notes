#!/usr/bin/env bash
# arith: shared pod runner. One heavy job at a time; timings only with an empty GPU (nvidia-smi compute apps).
#   /workspace/src      the lane tree (research pods sync; commit in .research-source.json)
source /workspace/env.sh
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
A=/workspace/arith; O=$A/runs; LOG=$A/runs.txt; mkdir -p $O
SRC=${SRC:-/workspace/src}
TIP=$(python3 -c 'import json; print(json.load(open("'$SRC'/.research-source.json"))["commit"])' 2>/dev/null || echo unknown)

gpu_idle() {  # wait up to ${1:-120} s for an empty GPU
  for i in $(seq $(( ${1:-120} / 2 ))); do
    [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2
  done
  echo "GPU NOT IDLE: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader | tr '\n' ' ')" | tee -a $LOG; return 1
}

line() {  # one summary line of a result.json
  $PY - "$1" <<'PYX' 2>/dev/null
import json, sys
r = json.load(open(sys.argv[1]))
m = {x.get("name"): x.get("value") for x in r.get("measurements", []) if isinstance(x, dict)}
if not m:
    found = {}
    def walk(x):
        if isinstance(x, dict):
            n = x.get("name") or x.get("metric")
            if isinstance(n, str) and n.startswith("t.") and n not in found:
                found[n] = x.get("value", x.get("median"))
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(r); m = found
keys = ["t.total", "t.arithmetic", "t.encoding_commitment", "t.witness", "t.serialization", "t.zk_additional"]
c = (r.get("contention") or {}).get("contended")
print(" ".join(f"{k[2:]}={m[k]:.4f}" if isinstance(m.get(k), (int, float)) else f"{k[2:]}=?" for k in keys) + f" contended={c}")
PYX
}

# run TAG REL BATCH DEPTH REPS [extra args...]   (genuine coins, local verifier, rep 1 dumped)
run() {
  local tag=$1 rel=$2 batch=$3 depth=$4 reps=$5; shift 5
  local d=$O/$tag; rm -rf $d; mkdir -p $d
  gpu_idle 1200 || return 1
  local t0=$(date +%s)
  (cd $SRC && PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC" \
     RESEARCH_GIT_COMMIT=${COMMIT:-$TIP} \
     $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $batch --pipeline $depth \
       --total-vus 4096 --target -128 --reps $reps --out $d/result.json --dump-dir $d/proofs --dump-reps 1 "$@" > $d/log 2>&1)
  local rc=$? t1=$(date +%s)
  echo "$(date -u +%H:%M:%SZ) $tag src=${SRC#/workspace/} commit=${COMMIT:-$TIP} rel=$rel l=$batch p=$depth reps=$reps rc=$rc wall=$((t1-t0))s $(line $d/result.json) $*" | tee -a $LOG
}

# prof TAG REL BATCH DEPTH [extra args...]   (torch.profiler over the 3rd pipelined pass; no dump; 3 reps)
prof() {
  local tag=$1 rel=$2 batch=$3 depth=$4; shift 4
  local d=$A/prof/$tag; rm -rf $d; mkdir -p $d
  gpu_idle 1200 || return 1
  (cd $SRC && PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC" \
     $PY $A/scripts/prof.py $d --profile-call ${CALL:-3} -- --relation $rel bench-vu --zk --mode interactive --batch $batch \
       --pipeline $depth --total-vus 4096 --target -128 --reps 3 --out $d/result.json "$@" > $d/log 2>&1)
  echo "$(date -u +%H:%M:%SZ) prof $tag rel=$rel l=$batch p=$depth rc=$? $(line $d/result.json) :: $(head -1 $d/kernels.txt 2>/dev/null)" | tee -a $LOG
}
