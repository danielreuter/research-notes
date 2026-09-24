#!/usr/bin/env bash
# Lane hash-compose: one `research run` (bench_vu_fp8) on vy-hash-compose per invocation, polled to completion.
#   usage: launch.sh NAME -- <run.py args>       (the --root/--target/--device/--out/--dump flags are appended here)
set -uo pipefail
cd ~/projects/verity-main-wt/hash-compose
set -a; source ~/.config/verity/r2.env; set +a
POD=~/.research/notes/lanes/hash-compose/evidence/scripts/ssh.sh
PYPATH=packages/verity/src:backends/numerical/python:.
MACHINE=${MACHINE:-vy-hash-compose}
name=$1; shift; [ "$1" = "--" ] && shift
out=$(uv run --no-sync research run --on $MACHINE --project verity --campaign r23-hash-compose --source . --tool ${TOOL:-bench_vu_fp8} \
      --scratch triton --exclusive --require-result --stage S --env PYTHONPATH=$PYPATH -- \
      /workspace/venv312/bin/python -m backends.direct.ligero.run "$@" --target -128 --device cuda \
      --out '$RESEARCH_RUN_DIR/result.json' --dump-dir '$RESEARCH_RUN_DIR/proofs' --dump-reps 1 2>&1)
id=$(echo "$out" | grep -o 'r2026[0-9]*-[0-9]*-[0-9a-f]*' | head -1)
echo "[$(date -u +%H:%M:%SZ)] $name -> $id"
if [ -z "$id" ]; then echo "$out"; exit 1; fi
for i in $(seq 1 180); do
  sleep 10
  st=$($POD "python3 -c \"import json;print(json.load(open('/workspace/research/runs/$id/status.json'))['state'])\"" 2>/dev/null)
  case "$st" in done|failed|timed_out|killed) break;; esac
done
echo "[$(date -u +%H:%M:%SZ)] $name $id state=$st"
$POD "tail -2 /workspace/research/runs/$id/stdout.log | cut -c1-400; grep -m3 -i 'error\|Traceback' /workspace/research/runs/$id/stderr.log | cut -c1-300"
echo "$name $id $st" >> ~/.research/notes/lanes/hash-compose/evidence/runs.txt
