#!/usr/bin/env bash
# wave-a100-2 queue B: waits for QUEUE_A_DONE, then 3 alternating live rounds (same-DC verifier) over the bare candidates
# v3 p8, v3 p4, v3x4 p4 and the committed +shared tile 64x64 cell at its better local depth (shared64p4-r1 vs shared64p8-r1).
S=/workspace/wave-a100/summary.txt
until grep -q QUEUE_A_DONE $S; do sleep 10; done
cd /workspace/wave-a100/pod-scripts
dsh=$(python3 - <<'PY'
import json
def t(tag):
    try: return {x["name"]: x["value"] for x in json.load(open(f"/workspace/wave-a100/runs/{tag}/result.json"))["measurements"]}["t.total"]
    except Exception: return 9e9
print(4 if t("shared64p4-r1") <= t("shared64p8-r1") else 8)
PY
)
echo "$(date -u +%H:%M:%S) QUEUE_B committed depth p$dsh" >> $S
C="v3p8:bf16-ampere-v3:16384:8 v3p4:bf16-ampere-v3:16384:4 x4p4:bf16-ampere-v3x4:4096:4 shared64p$dsh:bf16-ampere:16384:$dsh:--auth,included-hash-shared,--tile,64x64"
for r in 1 2 3; do bash 02-live.sh $r $C; done
echo "$(date -u +%H:%M:%S) QUEUE_B_DONE" >> $S
