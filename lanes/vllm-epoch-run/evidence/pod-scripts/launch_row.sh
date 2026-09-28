#!/bin/bash
# launch_row.sh N|canary [main|alt]: row N (or the canary, canary_pod.sh)'s pod, its cap guard and its detached run (VM side; section-1 environment of cloud-lane-setup.md).
#   refuses: no GO in lanes/vllm-epoch-run/; the epoch worktree is not clean at the recorded sha; the row's status is not `ok` (wave2 needs
#   ALLOW_WAVE2=1 once its fix is on main); even its 1-pair estimate ends after 17:30Z (defer); the lane's committed spend plus its cap
#   passes $250; GPU_SUB names a shape that is not an allowed substitute or costs more.
#   pairs: 3 (the records' n_runs 6) unless rows.json pins them (#101: 1); a 3-pair estimate ending after 17:30Z falls back to PAIRS=1.
#   then: pod `vyv-rf-epoch-N` (secure cloud, CUDA >= 12.9 host, --register --project verity --guard 90); a guard over exactly that pod
#   (--pod-max-hours = cap / rate); `research run` of epoch_row.sh with custody (--timeout = the cap's hours less 25 min for the store,
#   and no later than 17:50Z).  Appends a line to evidence/spend.tsv and prints the WAIT checkpoint.
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
if r["status"] == "ask" and os.environ.get("COORD_OK") != "1":
    die("waits for the coordinator (" + r.get("note", "") + ")")
sub = os.environ.get("GPU_SUB")
if sub:
    if sub not in cfg["substitutes"].get(r["gpu"], []):
        die(f"{sub} is not an allowed substitute for {r['gpu']} (ask the coordinator)")
    sys.path.insert(0, "/workspace/tools/research/src")
    from research.pods import runpod
    q = '{ gpuTypes(input:{id:"%s"}) { lowestPrice(input:{gpuCount:%d, secureCloud:true}) { uninterruptablePrice } } }' % (sub, r["count"])
    price = ((runpod._graphql(q)["data"]["gpuTypes"] or [{}])[0].get("lowestPrice") or {}).get("uninterruptablePrice")
    if price is None or price > r["rate"] + 1e-9:
        die(f"{sub} x{r['count']} at ${price}/h is not at or below ${r['rate']}/h (ask the coordinator)")
    r["gpu"] = sub
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
       "ENVARGS": " ".join(f"--env {shlex.quote(k + '=' + v)}" for k, v in sorted(env.items()))}
print("; ".join(f"{k}={shlex.quote(str(v))}" for k, v in out.items()))
EOF
)"
POD=vyv-rf-epoch-$N
echo "#$N $KEY: $COUNT x $GPU, >= $MINRAM GB/GPU, cap \$$CAP (max ${MAXH} h at \$$RATE/h), $PAIRS pair(s), est ${EST} h, timeout ${TIMEOUT} s, custody ${TTL} h${NOTE:+; $NOTE}"

out=$(PYTHONPATH=/workspace/tools/research/src RESEARCH_MACHINES_D=$RESEARCH_MACHINES_D python3 "$H/create_cuda.py" 12.9,13.0 \
  --name "$POD" --gpu "$GPU" --gpu-count "$COUNT" --min-ram "$MINRAM" --disk "$DISK" --cloud SECURE --register --project verity --guard 90 2>&1)
rc=$?; echo "$out" | tail -n 6
[ "$rc" = 5 ] && { echo "NO STOCK: $COUNT x $GPU secure; not substituting a pricier shape (ask the coordinator)"; exit 5; }
[ "$rc" = 0 ] || { echo "pod create rc=$rc"; exit "$rc"; }
PODID=$($R pods list 2>/dev/null | grep " $POD-veritor-campaign" | grep -o '^[a-z0-9]*' | head -n 1)
$R pods guard --prefix "$POD-" --pod-max-hours "$MAXH" --detach > "$LANE/evidence/guard-$N.txt" 2>&1
echo "cap guard: $(tail -n 1 "$LANE/evidence/guard-$N.txt")"
$R pods ssh "$POD" -- 'nproc; free -g | head -2; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; df -h /workspace | tail -1' \
  2>/dev/null | sed "s/^/  $POD: /"

SEND=(--send "$H/epoch_row.sh" --send "$H/strict_word.py" --send "$H/store_build.sh"); CMD='exec bash "$RESEARCH_RUN_DIR/inputs/epoch_row.sh"'
[ "$N" = canary ] && { SEND=(--send "$H/canary_pod.sh"); CMD='exec bash "$RESEARCH_RUN_DIR/inputs/canary_pod.sh"'; }
run=$($R run --on "$POD" --project verity --campaign vllm-rebaseline-epoch --custody-r2 --custody-ttl "${TTL}h" --timeout "$TIMEOUT" \
  --source "$WT" --cwd source/integrations/vllm "${SEND[@]}" \
  --env ROW="$KEY" --env ROWNUM="$N" --env CLASS="$CLASS" --env EPOCH_SHA="$EPOCH_SHA" --env POD="$POD" $ENVARGS \
  -- bash -c "$CMD" 2>&1 | tee "$LANE/evidence/launch-$N.txt" | grep -o 'r20[0-9]\{6\}-[0-9]\{6\}-[0-9a-f]\{4\}' | head -n 1)
[ -n "$run" ] || { echo "launch failed (evidence/launch-$N.txt)"; exit 6; }
[ -f "$LANE/evidence/spend.tsv" ] || printf 'row\tpod\tpod_id\trun\tstart_utc\tend_utc\trate\tspent\tcap\tpairs\n' > "$LANE/evidence/spend.tsv"
printf '%s\t%s\t%s\t%s\t%s\t\t%s\tlive\t%s\t%s\n' "$N" "$POD" "$PODID" "$run" "$(date -u +%FT%TZ)" "$RATE" "$CAP" "$PAIRS" >> "$LANE/evidence/spend.tsv"
back=$(date -u -d "+$(python3 -c "print(int($EST*60))") min" +%H:%MZ)
echo "WAIT $POD $run check-back $back agent bc-75fd4007: #$N Build/Match/word check/Commit/store (${PAIRS} pair(s), est ${EST} h, cap \$$CAP)${NOTE:+; $NOTE}"
