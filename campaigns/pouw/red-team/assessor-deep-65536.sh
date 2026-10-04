#!/usr/bin/env bash
# fill: owner=bc-d7d4b0d1 gpus=0 max_min=25 cpus=6 project=pous prio=0 mem_gb=8
# The assessor (bc-d7d4b0d1): clause (b) at long tails for v2-hot's Δ(n, k) table at k = 65,536, which closes k = 32,768
# and 65,536 (ratings.md 2:48 PM PDT, condition 1). CPU only. One JSON per family is the checkpoint; exit 99 while
# families remain, 0 when all are done and merged into deep-65536.json beside deep-16384.json.
set -uo pipefail
W=/workspace/pouw/fill-out/assessor-late-start
T=/workspace/research/src/294b113d55fc0cb40e5b726965be08e310686ac3
PY=/workspace/pouw/gpu7-fp4/venv/bin/python
export PYTHONPATH=$T/packages/verity/src:$T/protocols/pouw:$W
cd $W && mkdir -p deep-65536 || exit 1
FAMS="saturated@t4 rank1@t4 cancel-pair@t4 cancel-full@t4 cancel-full@spiky saturated-full@t4"
out() { echo "deep-65536/$(echo "$1" | tr '@' '_').json"; }
pids=()
for f in $FAMS; do
  o=$(out "$f")
  [ -s "$o" ] && continue
  ( $PY hot_deep_long.py --family "$f" --k 65536 --out "$o.tmp" && mv "$o.tmp" "$o" ) >> deep-65536/run.log 2>&1 &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
for f in $FAMS; do [ -s "$(out "$f")" ] || exit 99; done
$PY - <<'EOF' || exit 1
import glob, json
json.dump([json.load(open(f)) for f in sorted(glob.glob("deep-65536/*.json"))], open("deep-65536.json.tmp", "w"), indent=1)
EOF
mv deep-65536.json.tmp deep-65536.json && touch deep-65536.done
exit 0
