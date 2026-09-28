#!/bin/bash
# launch_row.sh N|canary [main|alt]: row N (or the canary, canary_pod.sh): its pod, its cap guard and its detached run (VM side; section-1
# environment of cloud-lane-setup.md).
#   refuses: no GO in lanes/vllm-epoch-run/; the epoch worktree is not clean at the recorded sha; the row's status is not `ok` (wave2 needs
#   ALLOW_WAVE2=1 once its fix is on main); even its 1-pair estimate ends after 17:30Z (defer); its estimate doesn't fit its cap; the lane's
#   committed spend plus its cap passes $250.
#   pairs: 3 (the records' n_runs 6) unless rows.json pins them (#101: 1); a 3-pair estimate ending after 17:30Z falls back to PAIRS=1.
#   offers, in order (coordinator 09:13Z): the row's shape on secure; then, for sm_89 rows only, L40 secure, L40S community, L40 community,
#   each on-demand and at or below the row's secure rate.  Each created pod is checked before any stage: driver runs CUDA >= 12.9 and the
#   host RAM meets the row's floor, else it is terminated at once and the next offer is tried (evidence/attempts-N.txt).
#   then: pod `vyv-rf-epoch-N` (--register --project verity --guard 90); a guard over exactly that pod (--pod-max-hours = cap / rate);
#   `research run` of epoch_row.sh with custody (--timeout = the cap's hours less 25 min, and no later than 17:50Z; POD_START for the
#   pod-side 15-minute fail-fast).  Appends a line to evidence/spend.tsv (with cloud and driver) and prints the WAIT checkpoint.
set -u
N=${1:?row number}; SHAPE=${2:-main}
H=$(cd "$(dirname "$0")" && pwd)
LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
ls "$STORE"/internal/lanes/vllm-epoch-run/*GO* "$LANE"/*GO* >/dev/null 2>&1 || { echo "REFUSED: no GO in lanes/vllm-epoch-run/"; exit 2; }
EPOCH_SHA=$(cat "$LANE/evidence/epoch_sha" 2>/dev/null) || { echo "REFUSED: evidence/epoch_sha not recorded"; exit 2; }
WT=/workspace-wt/epoch-${EPOCH_SHA:0:8}
[ "$(git -C "$WT" rev-parse HEAD 2>/dev/null)" = "$EPOCH_SHA" ] && [ -z "$(git -C "$WT" status --porcelain)" ] \
  || { echo "REFUSED: $WT is not a clean checkout of $EPOCH_SHA"; exit 2; }

eval "$(python3 - "$H/rows.json" "$N" "$SHAPE" "$LANE/evidence/spend.tsv" <<'EOF'
import json, math, os, shlex, sys, time, calendar
cfg, n, shape, ledger = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3], sys.argv[4]
r = dict(cfg["rows"][n]) if n != "canary" else dict(cfg["canary"], key="-", status="ok", est3_h=None, env={"PAIRS": "1"}, **{"class": "-"})
if shape == "alt":
    alt = r["alt"]; r.update({k: v for k, v in alt.items() if k != "env"}); r["env"] = {**r["env"], **alt.get("env", {})}
def die(msg):
    print(f"echo {shlex.quote('REFUSED: #' + n + ' ' + msg)}; exit 3"); sys.exit()
if r["status"] == "wave2" and os.environ.get("ALLOW_WAVE2") != "1":
    die(f"wave 2: needs {r.get('needs')} on main (ALLOW_WAVE2=1 once it is)")
if r["status"] == "deferred":
    die("deferred: " + r.get("note", ""))
if r["status"] == "ask" and os.environ.get("COORD_OK") != "1":
    die("waits for the coordinator (" + r.get("note", "") + ")")
def price(gpu, count, secure):
    sys.path.insert(0, "/workspace/tools/research/src")
    from research.pods import runpod
    q = '{ gpuTypes(input:{id:"%s"}) { lowestPrice(input:{gpuCount:%d, secureCloud:%s}) { uninterruptablePrice } } }' % (gpu, count, "true" if secure else "false")
    try:
        return ((runpod._graphql(q)["data"]["gpuTypes"] or [{}])[0].get("lowestPrice") or {}).get("uninterruptablePrice")
    except Exception:
        return None
shapes = [(r["count"], r["min_ram"])] + [(x["count"], x["min_ram"]) for x in r.get("alt_shapes", [])]
offers = [(r["gpu"], "SECURE", r["count"], r["min_ram"])]
for i, (cnt, ram) in enumerate(shapes):
    if r["gpu"] not in cfg["substitutes"]:
        break
    if i > 0:                                       # fewer GPUs of the row's own secure shape: a lower rate by construction
        offers.append((r["gpu"], "SECURE", cnt, ram))
    cands = [(g, "SECURE") for g in cfg["substitutes"][r["gpu"]]] + [(r["gpu"], "COMMUNITY")] + [(g, "COMMUNITY") for g in cfg["substitutes"][r["gpu"]]]
    for gpu, cloud in cands:
        p = price(gpu, cnt, cloud == "SECURE")
        if p is not None and p <= r["rate"] + 1e-9:
            offers.append((gpu, cloud, cnt, ram))
now = time.time()
end = calendar.timegm(time.strptime(cfg["last_end_utc"], "%Y-%m-%dT%H:%MZ"))
hard = calendar.timegm(time.strptime("2026-09-28T17:50Z", "%Y-%m-%dT%H:%MZ"))
env = dict(r["env"])
pairs, note, est = env.get("PAIRS", "3"), "", r["est_h"]
if pairs == "3":
    if now + r["est3_h"] * 3600 <= end:
        est = r["est3_h"]
    else:
        pairs, note = "1", "PAIRS=1: the 3-pair estimate ends after 17:30Z (n_runs 6 -> 2)"
if now + est * 3600 > end:
    die(f"estimate {est} h at {pairs} pair(s) ends after {cfg['last_end_utc']}: defer")
env["PAIRS"] = pairs
committed = 0.0
if os.path.exists(ledger):
    for ln in open(ledger):
        f = ln.rstrip("\n").split("\t")
        if len(f) >= 9 and f[0] != "row":
            committed += float(f[8]) if f[7] in ("", "live") else float(f[7])     # a live row counts its cap, a finished one its spend
if committed + r["cap"] > cfg["lane_cap_usd"]:
    die(f"committed ${committed:.2f} + cap ${r['cap']} passes the lane's ${cfg['lane_cap_usd']}")
max_h = r["cap"] / r["rate"]
timeout = int(min(max_h * 3600 - 25 * 60, hard - now))
ttl = min(24, math.ceil(timeout / 3600 + 1.5))
if est > max_h - 0.4:
    die(f"estimate {est} h at {pairs} pair(s) does not fit the ${r['cap']} cap ({max_h:.2f} h): ask the coordinator")
out = {"KEY": r["key"], "CLASS": r["class"], "GPU": r["gpu"], "COUNT": r["count"], "MINRAM": r["min_ram"], "DISK": r["disk"],
       "RATE": r["rate"], "CAP": r["cap"], "EST": est, "PAIRS": pairs, "NOTE": note, "MAXH": f"{max_h:.2f}", "TIMEOUT": timeout, "TTL": ttl,
       "ENVARGS": " ".join(f"--env {shlex.quote(k + '=' + v)}" for k, v in sorted(env.items())),
       "PCOUNT": r["count"], "END_S": int(end), "HARD_S": int(hard), "EST1": r["est_h"], "EST3": r["est3_h"] or r["est_h"],
       "OFFERS": " ".join(f"{g.replace(' ', '_')}@{c}@{k}@{m}" for g, c, k, m in offers)}
print("; ".join(f"{k}={shlex.quote(str(v))}" for k, v in out.items()))
EOF
)"
POD=vyv-rf-epoch-$N
echo "#$N $KEY: $COUNT x $GPU, >= $MINRAM GB/GPU, cap \$$CAP (max ${MAXH} h at \$$RATE/h), $PAIRS pair(s), est ${EST} h, timeout ${TIMEOUT} s, custody ${TTL} h${NOTE:+; $NOTE}"

ATT=$LANE/evidence/attempts-$N.txt
gone() { for i in $(seq 1 18); do $R pods list 2>/dev/null | grep -q " $POD-veritor-campaign " || return 0; sleep 5; done; return 1; }
PODID=""; CLOUD=""; DRIVER=""
for offer in $OFFERS; do
  IFS=@ read -r G C COUNT MINRAM <<< "$offer"; G=${G//_/ }
  T0=$(date -u +%FT%TZ); T0S=$(date +%s)
  out=$(PYTHONPATH=/workspace/tools/research/src RESEARCH_MACHINES_D=$RESEARCH_MACHINES_D timeout 600 python3 "$H/create_cuda.py" 12.9,13.0 \
    --name "$POD" --gpu "$G" --gpu-count "$COUNT" --min-ram "$MINRAM" --disk "$DISK" --cloud "$C" --register --project verity --guard 90 2>&1)
  rc=$?
  if [ "$rc" = 5 ]; then echo "$T0 $COUNT x $G $C: no stock" >> "$ATT"; continue; fi
  if [ "$rc" != 0 ]; then   # a pod left under the name (sshd never answered within 10 min, registration failed) is terminated
    left=$($R pods list 2>/dev/null | grep " $POD-veritor-campaign " | grep -o '^[a-z0-9]*' | head -n 1)
    echo "$T0 $COUNT x $G $C: create rc=$rc $(echo "$out" | tail -n 1 | cut -c1-160)${left:+; pod $left left behind, terminated}" >> "$ATT"
    [ -n "$left" ] && { $R pods terminate "$left" > /dev/null 2>&1; $R pods unregister "$POD" > /dev/null 2>&1; gone || echo "  $POD still listed after 90 s" >> "$ATT"; }
    continue
  fi
  id=$($R pods list 2>/dev/null | grep " $POD-veritor-campaign " | grep -o '^[a-z0-9]*' | head -n 1)
  info=$($R pods ssh "$POD" -- 'echo "CUDA=$(nvidia-smi 2>/dev/null | grep -o "CUDA Version: [0-9.]*" | head -n 1 | grep -o "[0-9.]*$")"; \
    echo "DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n 1)"; \
    m=$(cat /sys/fs/cgroup/memory.max 2>/dev/null || cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null); \
    t=$(awk "/MemTotal/{print \$2*1024}" /proc/meminfo); case "$m" in ""|max) m=$t;; esac; [ "$m" -gt "$t" ] && m=$t; echo "RAMGB=$((m / 1000000000))"; echo "VCPU=$(nproc)"' 2>/dev/null)
  cuda=$(echo "$info" | sed -n 's/^CUDA=//p'); drv=$(echo "$info" | sed -n 's/^DRV=//p'); ramgb=$(echo "$info" | sed -n 's/^RAMGB=//p'); vcpu=$(echo "$info" | sed -n 's/^VCPU=//p')
  okc=$(python3 -c "v='${cuda:-0}'.split('.');print(int((int(v[0]),int(v[1]) if len(v)>1 else 0)>=(12,9)))" 2>/dev/null)
  okr=$(python3 -c "print(int(${ramgb:-0} >= 0.93 * $COUNT * $MINRAM))")
  if [ "$okc" = 1 ] && [ "$okr" = 1 ]; then
    act=$($R pods list 2>/dev/null | grep "^$id " | grep -o '\$[0-9.]*/h' | tr -d '$/h' | head -n 1)
    PRATE=${act:-$(python3 -c "print(round($RATE * $COUNT / $PCOUNT, 2))")}        # the pod's own rate: cap hours, timeout and spend follow it
    read -r MAXH TIMEOUT TTL < <(python3 -c "
import math, time
mh = $CAP / $PRATE; t = int(min(mh * 3600 - 1500, $HARD_S - time.time()))
print(f'{mh:.2f}', t, min(24, math.ceil(t / 3600 + 1.5)))")
    if [ "$COUNT" -lt "$PCOUNT" ]; then   # a fewer-GPU offer: size the estimate by its vCPUs (coordinator 10:02Z)
      read -r EST PAIRS2 FIT < <(python3 -c "
import time
f = 0.5 + 0.5 * max(1.0, 16 * $PCOUNT / max(1, ${vcpu:-1}))
e3, e1 = $EST3 * f, $EST1 * f
now = time.time()
p = '$PAIRS'
if p == '3' and now + e3 * 3600 > $END_S: p = '1'
e = e3 if p == '3' else e1
print(f'{e:.2f}', p, int(now + e * 3600 <= $END_S and e <= $MAXH - 0.4))")
      if [ "$FIT" != 1 ]; then
        echo "$T0 $COUNT x $G $C: pod $id has $vcpu vCPU: estimate ${EST} h misses 17:30Z or the cap; terminated" >> "$ATT"
        $R pods terminate "$id" > /dev/null 2>&1; $R pods unregister "$POD" > /dev/null 2>&1; gone; continue
      fi
      [ "$PAIRS2" != "$PAIRS" ] && { PAIRS=$PAIRS2; NOTE="PAIRS=1: the 3-pair estimate at $vcpu vCPU ends after 17:30Z (n_runs 6 -> 2)"; ENVARGS=$(echo "$ENVARGS" | sed 's/--env PAIRS=3/--env PAIRS=1/'); }
    fi
    PODID=$id; CLOUD=$C; DRIVER=$drv; GPU=$G; VCPU=$vcpu; RATE=$PRATE
    echo "$T0 $COUNT x $G $C: accepted pod $id driver $drv (CUDA $cuda) host ${ramgb} GB, $vcpu vCPU, est ${EST} h at $PAIRS pair(s)" >> "$ATT"; break
  fi
  echo "$T0 $COUNT x $G $C: REFUSED pod $id driver ${drv:-?} (CUDA ${cuda:-?}) host ${ramgb:-?} GB (floor $((COUNT * MINRAM)) GB); terminated" >> "$ATT"
  $R pods terminate "$id" > /dev/null 2>&1; $R pods unregister "$POD" > /dev/null 2>&1; gone || echo "  $POD still listed after 90 s" >> "$ATT"
done
tail -n 4 "$ATT" 2>/dev/null | sed "s/^/  /"
[ -n "$PODID" ] || { echo "NO SHAPE for #$N among: $OFFERS (evidence/attempts-$N.txt); retry while its latest start holds"; exit 5; }
$R pods guard --prefix "$POD-" --pod-max-hours "$MAXH" --detach > "$LANE/evidence/guard-$N.txt" 2>&1
echo "cap guard: $(tail -n 1 "$LANE/evidence/guard-$N.txt") (max ${MAXH} h at \$$RATE/h, timeout ${TIMEOUT} s, custody ${TTL} h)"

SEND=(--send "$H/epoch_row.sh" --send "$H/strict_word.py" --send "$H/store_build.sh" --send "$H/failfast_bootstrap.sh"); CMD='exec bash "$RESEARCH_RUN_DIR/inputs/epoch_row.sh"'
[ "$N" = canary ] && { SEND=(--send "$H/canary_pod.sh" --send "$H/failfast_bootstrap.sh"); CMD='exec bash "$RESEARCH_RUN_DIR/inputs/canary_pod.sh"'; }
run=$($R run --on "$POD" --project verity --campaign vllm-rebaseline-epoch --custody-r2 --custody-ttl "${TTL}h" --timeout "$TIMEOUT" \
  --source "$WT" --cwd source/integrations/vllm "${SEND[@]}" \
  --env ROW="$KEY" --env ROWNUM="$N" --env CLASS="$CLASS" --env EPOCH_SHA="$EPOCH_SHA" --env POD="$POD" --env POD_START="$T0S" --env POD_CLOUD="$CLOUD" $ENVARGS \
  -- bash -c "$CMD" 2>&1 | tee "$LANE/evidence/launch-$N.txt" | grep -o 'r20[0-9]\{6\}-[0-9]\{6\}-[0-9a-f]\{4\}' | head -n 1)
[ -n "$run" ] || { echo "launch failed (evidence/launch-$N.txt)"; exit 6; }
[ -f "$LANE/evidence/spend.tsv" ] || printf 'row\tpod\tpod_id\trun\tstart_utc\tend_utc\trate\tspent\tcap\tpairs\tcloud\tdriver\tgpus\tvcpus\n' > "$LANE/evidence/spend.tsv"
printf '%s\t%s\t%s\t%s\t%s\t\t%s\tlive\t%s\t%s\t%s\t%s\t%s\t%s\n' "$N" "$POD" "$PODID" "$run" "$T0" "$RATE" "$CAP" "$PAIRS" "$CLOUD" "$DRIVER" "$COUNT" "$VCPU" >> "$LANE/evidence/spend.tsv"
back=$(date -u -d "+$(python3 -c "print(int($EST*60))") min" +%H:%MZ)
echo "WAIT $POD ($CLOUD, $COUNT x $GPU, driver $DRIVER) $run check-back $back agent bc-75fd4007: #$N Build/Match/word check/Commit/store (${PAIRS} pair(s), est ${EST} h, cap \$$CAP)${NOTE:+; $NOTE}"
