#!/usr/bin/env bash
# agkr-real-k: #101's route (a) cells on an L40S prover (the served GPU), K = 2048 and 8192 on the captured sets, the verifier in
# the same datacenter on ANOTHER physical machine (RunPod machine ids compared; bench.cell plan checks them again, PR #74).
# US-NC-1 with global networking (kb live-verifier.md): the prover reaches the verifier's podnet1 address 10.x on its inner port.
#   [DC=US-NC-1] [VGPU=<verifier GPU type>] [CELLS="k2048 k8192"] [K2048_ARGS=] [K8192_ARGS=GATE=0] bash launch-l40s.sh
#       (after an L40S prover vy-agkr-l40s exists in DC: create-pod.py ... --dc US-NC-1 --global-net).  The RTT probe times the
#       verifier's echo on 7201 (cell.sh), one open connection; an L40S gate at K=2048 passed in r20260926-123236-c272
set -uo pipefail
cd "$(git -C /workspace rev-parse --show-toplevel)" || exit 2
R="uv run research"; E=$(cd "$(dirname "$0")" && pwd); C=$RESEARCH_NOTES/lanes/flock-l40s-101/evidence/pod-scripts
P=vy-agkr-l40s; V=vy-agkr-l40s-ver; DC=${DC:-US-NC-1}
say() { echo "##### $(date -u +%H:%M:%SZ) $*"; }
podjson() { uv run python -c "
import json, sys
from research.pods import runpod
full = sys.argv[1] + '-veritor-campaign'
live = [p for p in runpod._request('GET', '/pods') or [] if p.get('name') == full and p.get('desiredStatus') != 'TERMINATED']
print(json.dumps({k: live[0].get(k) for k in ('id', 'machineId', 'publicIp', 'costPerHr', 'globalNetworking')} if live else {}))" "$1"; }
PJ=$(podjson $P); PID=$(echo "$PJ" | python3 -c "import json,sys;print(json.load(sys.stdin).get('id') or '')")
[ -n "$PID" ] || { echo "no live $P"; exit 5; }
PM=$(echo "$PJ" | python3 -c "import json,sys;print(json.load(sys.stdin).get('machineId') or '')")
say "prover $PID machine $PM"
$R pods register $P --pod-id $PID --project verity --guard 45 --replace | tail -1
for attempt in 1 2 3; do
  VJ=$(podjson $V); VID=$(echo "$VJ" | python3 -c "import json,sys;print(json.load(sys.stdin).get('id') or '')")
  if [ -z "$VID" ]; then
    say "verifier in $DC (attempt $attempt)"
    if [ -n "${VGPU:-}" ]; then   # e.g. VGPU="NVIDIA H200": the one GPU type the DC still has (US-NC-1 at 13:10Z, no CPU pods)
      uv run python $C/create-pod.py $V --gpu "$VGPU" --cloud SECURE --dc $DC --port 7200 --min-vcpu 8 --global-net 2>&1 | grep -v '^$' | tail -1
    else
      uv run python $C/create-pod.py $V --gpu "NVIDIA RTX A5000" --gpu "NVIDIA RTX A4000" --gpu "NVIDIA RTX 4000 Ada Generation" --gpu "NVIDIA L4" \
        --gpu "NVIDIA RTX A6000" --gpu "NVIDIA A40" --gpu "NVIDIA L40S" --cloud SECURE --dc $DC --port 7200 --min-vcpu 8 --global-net 2>&1 | grep -v '^$' | tail -1
    fi
    VJ=$(podjson $V); VID=$(echo "$VJ" | python3 -c "import json,sys;print(json.load(sys.stdin).get('id') or '')")
    if [ -z "$VID" ] && [ -z "${VGPU:-}" ]; then   # flock-l40s-101's US-NC-1 verifier box; alone, so an enum refusal of it cannot sink the cheap list
      uv run python $C/create-pod.py $V --gpu "NVIDIA RTX PRO 6000 Blackwell Server Edition" --cloud SECURE --dc $DC --port 7200 \
        --min-vcpu 8 --global-net 2>&1 | grep -v '^$' | tail -1
      VJ=$(podjson $V); VID=$(echo "$VJ" | python3 -c "import json,sys;print(json.load(sys.stdin).get('id') or '')")
    fi
  fi
  [ -n "$VID" ] || { echo "no verifier pod in $DC"; exit 5; }
  sleep 20; VJ=$(podjson $V); VM=$(echo "$VJ" | python3 -c "import json,sys;print(json.load(sys.stdin).get('machineId') or '')")
  say "verifier $VID machine $VM"
  [ -n "$VM" ] && [ -n "$PM" ] && [ "$VM" != "$PM" ] && break
  say "the verifier shares the prover's machine (or has no machine id yet): terminate and retry"; $R pods terminate $VID | tail -1; VID=""
done
[ -n "$VID" ] || exit 5
$R pods register $V --pod-id $VID --project verity --guard 45 --replace | tail -1
VIP=""; for i in $(seq 30); do
  VIP=$($R pods ssh $V -- "ip -4 -o addr show podnet1 2>/dev/null | awk '{print \$4}' | cut -d/ -f1" 2>/dev/null | grep -E '^10\.' | tail -1); [ -n "$VIP" ] && break; sleep 10
done
[ -n "$VIP" ] || { echo "the verifier has no podnet1 address (global networking)"; exit 5; }
say "verifier podnet1 $VIP; route test from the prover"
ok=""; for i in $(seq 12); do $R pods ssh $P -- "timeout 4 bash -c '</dev/tcp/$VIP/22' && echo REACH" 2>/dev/null | grep -q REACH && { ok=1; break; }; sleep 10; done
[ -n "$ok" ] || { echo "the prover cannot reach $VIP:22 over global networking"; exit 5; }
CELLS=${CELLS:-k2048 k8192}
$R notes checkpoint agkr-real-k open "L40S pods: $P $PID (machine $PM) + $V $VID (machine $VM) in $DC, global net $VIP; launching $CELLS" | tail -1
P=$P V=$V DC_ADOPT=$DC VADDR=$VIP:7200 VRTT=$VIP:7201 K2048_POINTS="1024 2048 4096" K8192_POINTS="256 512 1024" \
  K2048_ARGS=${K2048_ARGS-} K8192_ARGS=${K8192_ARGS-GATE=0} ALLOW_UNPUSHED=${ALLOW_UNPUSHED:-} bash $E/launch-cells.sh $CELLS
