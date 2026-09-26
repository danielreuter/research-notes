#!/usr/bin/env bash
# agkr-real-k: the cell runs left after the 09:10Z spend pause, ready to launch the moment the coordinator lifts it.
# Run from the verity checkout on branch cursor/agkr-real-k-f806 (committed and pushed: research run ships HEAD), in a
# shell with the cloud-lane environment (RESEARCH_NOTES, RESEARCH_MACHINES_D, RESEARCH_WRITE_THROUGH=1).
#
#   bash $RESEARCH_NOTES/lanes/agkr-real-k/evidence/pod-scripts/launch-cells.sh [k2048] [k8192] [afs]      (default: k2048 afs)
#
#   k2048  A-route-a on art:123dc234 (#101 captured, K = 2048), sizes 1024 2048 4096 6272 with the scatter_terms fix (b98d5feb):
#          the 09:0xZ cell art:95fdd0ae stopped at 4,096 on that bug; the gate reruns with the K-aware Flock replay
#   k8192  A-route-a on art:927a4c3a (K = 8192), sizes 256 512 1024 1920 (only if the 09:0xZ K = 8192 cell did not finish)
#   afs    A-fs (A-GKR alone, Fiat-Shamir, x and W private: a drill-down) on both sets, whole set per proof (20-afs.sh)
#
# Pods: an A100-SXM4-80GB prover (secure) and a verifier in the same datacenter (a CPU pod when one is in stock there, else a
# second A100: US-MD-1 had no CPU stock at 08:25Z), both registered with the idle guard; drained and terminated at the end.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 2
[ "$(git rev-parse --abbrev-ref HEAD)" = cursor/agkr-real-k-f806 ] || { echo "not on cursor/agkr-real-k-f806"; exit 2; }
git diff --quiet HEAD -- backends || { echo "uncommitted changes under backends/: research run ships HEAD"; exit 2; }
R="uv run research"; E=$(dirname "$0"); LANE=agkr-real-k; P=vy-$LANE-a100; V=vy-$LANE-ver
WHAT=${*:-k2048 afs}
say() { echo "##### $(date -u +%H:%M:%SZ) $*"; }
ck() { $R notes checkpoint $LANE open "$*" | tail -1; }

# ---- pods ---------------------------------------------------------------------------------------------------------------------
DC=""
for dc in ${DCS:-US-MD-1 US-KS-2 US-TX-3 CA-MTL-1 EU-RO-1 EUR-IS-1}; do
  say "prover A100 in $dc"
  $R pods create --name $P --gpu "NVIDIA A100-SXM4-80GB" --cloud SECURE --data-center $dc --disk 150 --register --project verity \
    --guard 45 > /tmp/$LANE-create-p.log 2>&1
  grep -q REGISTERED /tmp/$LANE-create-p.log && { DC=$dc; break; }
  tail -1 /tmp/$LANE-create-p.log
done
[ -n "$DC" ] || { echo "no A100-SXM4-80GB in ${DCS:-the list}"; exit 5; }
for spec in "cpu3c 16" "cpu5c 16" "cpu3c 8" "cpu3g 16" "cpu5g 16" "gpu NVIDIA A100-SXM4-80GB"; do
  set -- $spec
  if [ $1 = gpu ]; then shift; A=(--gpu "$*" --cloud SECURE); else A=(--cpu $1 --vcpu $2); fi
  say "verifier ${A[*]} in $DC"
  $R pods create --name $V "${A[@]}" --data-center $DC --disk 60 --expose-port 7200 --register --project verity --guard 45 \
    > /tmp/$LANE-create-v.log 2>&1
  grep -q REGISTERED /tmp/$LANE-create-v.log && break
  tail -1 /tmp/$LANE-create-v.log
done
grep -q REGISTERED /tmp/$LANE-create-v.log || { echo "no verifier pod in $DC"; $R pods terminate $P; exit 5; }
read -r VIP VSSH VSES < <($R pods list | python3 -c "
import ast, re, sys
for line in sys.stdin:
    if '$V-' in line or line.split()[1:2] == ['$V']:
        ip = re.search(r'ip=(\S+)', line).group(1); ports = ast.literal_eval(re.search(r'ports=(\{.*\})', line).group(1))
        print(ip, ports['22'], ports['7200'])")
[ -n "${VSES:-}" ] || { echo "no public mapping for $V's session port"; exit 5; }
ck "pause lifted: pods $P + $V in $DC (verifier $VIP:$VSES, sshd $VSSH); launching: $WHAT"

# ---- one A-route-a cell: plan, verifier first, prover, wait, stop the verifier's unserved sizes, register ------------------
wait_run() {  # $1 = run id: until the run's status is terminal
  while :; do
    $R fetch $1 > /dev/null 2>&1
    s=$(python3 -c "import json;print(json.load(open('$HOME/.research/runs/$1/status.json'))['transitions'][-1]['state'])" 2>/dev/null)
    case "$s" in done|failed|timed_out|cancelled) echo "$s"; return ;; esac
    sleep 60
  done
}
cell() {  # $1 = K, $2 = set art, $3 = sizes
  local plan=.bench-cell/$LANE-k$1-$(date -u +%H%M).json
  $R env --source . > /dev/null 2>&1
  uv run python -m verity_numerical.bench.cell plan --backend A-route-a --statement gemm-coordinate/k$1/sm80-mma-bf16+frame-v3/blake3-keyed \
    --input-set $2 --prover $P --verifier $V --verifier-addr $VIP:$VSES --rtt-target $VIP:$VSSH --campaign $LANE --lane $LANE \
    --points "$3" --out $plan > /dev/null || { echo "plan K=$1 failed"; return 1; }
  local runs; runs=$(uv run python -m verity_numerical.bench.cell run --cell $plan | python3 -c "
import json, sys
t = sys.stdin.read(); d = json.loads(t[:t.rindex(']') + 1]); print(' '.join(r['run'] or '-' for r in d))")
  set -- $runs; local vr=$1 pr=$2
  ck "WAITING K=$1 cell: ver $vr on $V, prover $pr on $P"
  say "prover $pr: $(wait_run $pr)"
  # the verifier serves its sizes in order; the ones the prover's sweep never reached end its run early (it then writes outputs.json)
  $R pods ssh $V -- "for p in \$(pgrep -f 'cell-serve --listen 0.0.0.0:7200'); do [ \"\$(cat /proc/\$p/comm)\" = flock-link-live ] && kill -TERM \$p; done" \
    > /dev/null 2>&1
  say "verifier $vr: $(wait_run $vr)"
  uv run python -m verity_numerical.bench.cell check --cell $plan --prover-run $pr --verifier-run $vr | tail -4
  uv run python -m verity_numerical.bench.cell register --cell $plan --prover-run $pr --verifier-run $vr --work .bench-cell/work | tail -3
}

sets() { $R data fetch $1 | tail -1; }
for w in $WHAT; do
  case $w in
    k2048) cell 2048 art:123dc234 "1024 2048 4096 6272" ;;
    k8192) cell 8192 art:927a4c3a "256 512 1024 1920" ;;
    afs)
      T=(); for a in art:123dc234 art:927a4c3a; do
        d=$(sets $a); n=$(python3 -c "import json;print(json.load(open('$d/manifest.json'))['set'])")
        t=.bench-cell/sets/afs-$n.tar.xz; [ -f $t ] || tar -cJf $t -C $(dirname $d) $(basename $d) --transform "s|^$(basename $d)|$n|"
        T+=("$t" "$a")
      done
      rid=$($R run --on $P --project verity --source . --cwd source --custody-r2 --custody-ttl 8h --stage agkr.afs --exclusive \
              --campaign $LANE --send ${T[0]} --send ${T[2]} --send $E/20-afs.sh \
              --env "SETS=$(basename ${T[0]}) ${T[1]} $(basename ${T[2]}) ${T[3]}" --env LANE=$LANE \
              -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/20-afs.sh' 2>&1 | grep -oE 'r[0-9]{8}-[0-9]{6}-[0-9a-f]{4}' | head -1)
      ck "WAITING A-fs $rid on $P"
      say "A-fs $rid: $(wait_run $rid)"; $R fetch $rid > /dev/null 2>&1; tail -20 $HOME/.research/runs/$rid/stdout.log 2>/dev/null ;;
  esac
done

# ---- drain and terminate ----------------------------------------------------------------------------------------------------
for pod in $P $V; do
  $R pods drain $pod | tail -3
done
$R pods list | grep -E "$P|$V" || echo "both pods gone"
ck "cell runs done ($WHAT); pods drained and terminated"
