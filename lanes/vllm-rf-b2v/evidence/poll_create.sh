#!/bin/bash
# Create an L40S pod on a CUDA >= 12.9 host (torch 2.13.0+cu129 sees no device on driver 550), SECURE then COMMUNITY, every 2 min
# until it exists or N tries pass.  usage: poll_create.sh NAME GPU_COUNT DISK [N]   (create_cuda.py = f56's, copied beside this)
NAME=$1; GC=$2; DISK=$3; N=${4:-15}
E=$(dirname "$0")
PY="env RESEARCH_MACHINES_D=$HOME/.research/notes/machines.d PYTHONPATH=$HOME/projects/verity-main-wt/cli/tools/research/src $HOME/projects/verity-main-wt/main/.venv/bin/python"
for i in $(seq 1 "$N"); do
  if research pods list 2>/dev/null | grep -q " $NAME-veritor-campaign "; then echo "exists $(date -u +%H:%M:%SZ)"; exit 0; fi
  for c in SECURE COMMUNITY; do
    out=$( ( [ -f "$HOME/.config/verity/r2.env" ] && { set -a; . "$HOME/.config/verity/r2.env"; set +a; }; $PY "$E/create_cuda.py" 12.9,13.0 --name "$NAME" --gpu "NVIDIA L40S" --gpu-count "$GC" --min-vcpu 8 --min-ram 60 --disk "$DISK" --cloud $c ) 2>&1 | tail -4)
    if ! grep -q "PodError\|HTTP 4\|Traceback" <<< "$out"; then echo "created on $c $(date -u +%H:%M:%SZ)"; echo "$out"; exit 0; fi
  done
  echo "try $i $(date -u +%H:%M:%SZ): $(grep -o '\"error\":\"[^\"]*\"\|HTTP [0-9]*: .\{0,160\}\|[A-Za-z]*Error.\{0,160\}' <<< "$out" | head -1)"
  sleep 120
done
echo "gave up $(date -u +%H:%M:%SZ)"; exit 1
