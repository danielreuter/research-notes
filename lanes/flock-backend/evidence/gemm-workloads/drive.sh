# usage: drive.sh PROVER_MACHINE VERIFIER_MACHINE VERIFIER_IP:PORT7400 VERIFIER_IP:PORT22 SM QUEUEFILE
# QUEUEFILE lines: TAG|SEND(or -)|ARGS...   (ARGS shared by both roles, e.g. REL=... SET=... PER=... POINTS=...)
cd /workspace
source /tmp/lane_env.sh >/dev/null
PM=$1; VM=$2; V=$3; RT=$4; SM=$5; Q=$6
L="uv run research run --project verity --source . --cwd source --custody-r2 --custody-ttl 8h --campaign flock-backend"
state() { uv run research fetch $1 2>&1 | tail -1 | sed -E 's/.*Z: ([a-z]+) .*/\1/'; }
launch() { local out; out=$("$@" 2>&1); echo "$out" | grep -oE 'run r[0-9]{8}-[0-9]{6}-[0-9a-f]{4} launched' | awk '{print $2}'; }
exec 3< $Q
while IFS='|' read -r -u 3 TAG SEND ARGS; do
  [ -z "$TAG" ] && continue
  S=(); [ "$SEND" != - ] && S=(--send "$SEND")
  eval "A=($ARGS)"
  vid=$(launch $L --on $VM "${S[@]}" -- bash backends/flock/pod/30-cell.sh ROLE=verifier OPERATOR=flock-backend-verifier-pod "${A[@]}")
  sleep 30
  pid=$(launch $L --on $PM "${S[@]}" -- bash backends/flock/pod/30-cell.sh ROLE=prover SM=$SM VERIFIER=$V RTT_TARGET=$RT LOOPBACK=1 "${A[@]}")
  echo "$(date -u +%H:%MZ) $TAG prover=$pid verifier=$vid"
  [ -z "$pid" ] || [ -z "$vid" ] && { echo "$TAG launch failed"; continue; }
  while :; do s=$(state $pid); [ "$s" = running ] || [ "$s" = submitted ] || [ "$s" = claimed ] || break; sleep 60; done
  for i in $(seq 1 10); do s=$(state $vid); [ "$s" = running ] || [ "$s" = submitted ] || break; sleep 30; done
  uv run research pods ssh $VM -- 'pkill -f "[v]erity_flock.bench"; pkill -f "[f]lock-pure-gpu"' >/dev/null 2>&1
  echo "$(date -u +%H:%MZ) $TAG prover $(state $pid) verifier $(state $vid)"
  bash /tmp/fp/reg.sh $pid $vid $TAG 2>&1 | tail -2
done
echo "$(date -u +%H:%MZ) QUEUE DONE"
