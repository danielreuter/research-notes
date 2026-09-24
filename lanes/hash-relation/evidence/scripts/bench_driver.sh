#!/usr/bin/env bash
# Lane hash-relation: the fp8-ada bare / committed / tile benches on vy-hash-relation (RTX 4090), one `research run` each,
# launched sequentially (the pod is --exclusive); state polled from the pod's status.json.  K=1536, 4096 VUs, l=16384, 3 reps, rep 1 dumped.
set -uo pipefail
cd ~/projects/verity-main-wt/hash-relation
set -a; source ~/.config/verity/r2.env; set +a
POD="ssh -o StrictHostKeyChecking=no -p 40035 root@213.192.2.94"
PYPATH=packages/verity/src:backends/numerical/python:.
launch() {  # name, then the bench-vu args
  local name=$1; shift
  local out
  out=$(uv run --no-sync research run --on vy-hash-relation --project verity --campaign r23-hash-relation --source . --tool bench_vu_fp8 \
        --scratch triton --exclusive --require-result --stage S --env PYTHONPATH=$PYPATH -- \
        /workspace/venv312/bin/python -m backends.direct.ligero.run "$@" --target -128 --device cuda --instance-procs 16 \
        --instances-cache /workspace/instances-cache --out '$RESEARCH_RUN_DIR/result.json' --dump-dir '$RESEARCH_RUN_DIR/proofs' --dump-reps 1 2>&1)
  local id; id=$(echo "$out" | grep -o 'r2026[0-9]*-[0-9]*-[0-9a-f]*' | head -1)
  echo "[$(date -u +%H:%M:%SZ)] $name -> $id"
  if [ -z "$id" ]; then echo "$out"; return 1; fi
  for i in $(seq 1 120); do
    sleep 10
    local st; st=$($POD "python3 -c \"import json;print(json.load(open('/workspace/research/runs/$id/status.json'))['state'])\"" 2>/dev/null)
    case "$st" in done|failed|timed_out|killed) break;; esac
  done
  echo "[$(date -u +%H:%M:%SZ)] $name $id state=$st"
  $POD "tail -2 /workspace/research/runs/$id/stdout.log | cut -c1-400; grep -m3 -i 'error\|Traceback' /workspace/research/runs/$id/stderr.log | cut -c1-300"
  echo "$name $id $st" >> ~/.research/notes/lanes/hash-relation/evidence/runs.txt
}
ADA="--relation fp8-ada bench-vu --batch 16384 --total-vus 4096 --reps 3"
H="--auth included-hash"
T="--auth included-hash --tile 64x64"
# bare-int-zk r20260923-080502-e138 / bare-fs-zk r20260923-080538-bc48 / bare-nonzk-int r20260923-080108-ca9c: launched by hand
launch hash-nonzk-int     $ADA --mode interactive $H
launch hash-int-zk        $ADA --zk --mode interactive $H
launch hash-fs-zk         $ADA --zk --mode fiat-shamir $H
launch tile-nonzk-int     $ADA --mode interactive $T
launch tile-int-zk        $ADA --zk --mode interactive $T
launch tile-fs-zk         $ADA --zk --mode fiat-shamir $T
launch bf16h-hash-int-zk  --relation bf16-hopper bench-vu --batch 16384 --total-vus 4096 --reps 3 --zk --mode interactive $H
launch fp8h-hash-int-zk   --relation fp8-hopper bench-vu --batch 16384 --total-vus 4096 --reps 3 --zk --mode interactive $H
launch bf16h-bare-int-zk  --relation bf16-hopper bench-vu --batch 16384 --total-vus 4096 --reps 3 --zk --mode interactive
launch fp8h-bare-int-zk   --relation fp8-hopper bench-vu --batch 16384 --total-vus 4096 --reps 3 --zk --mode interactive
echo DRIVER_DONE
