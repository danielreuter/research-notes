#!/bin/bash
# Program digests of every fixture row's stored descriptors, through the base and the head library (programs3.py).
# From the shipped head source root (research run --cwd source); base tree at /workspace/base. Local store only, no key.
#   usage: programs3.sh [ROW ...]     (default: every row with descriptors, smallest records first)
T=$PWD
B=/workspace/base
OUT=${RESEARCH_RUN_DIR:-/workspace/c2/programs3}; mkdir -p "$OUT/json" /workspace/c2/rec
[ -e /root/r2ro.env ] && { echo "refusing: /root/r2ro.env present"; exit 4; }
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
export PATH=/workspace/venv312/bin:$PATH PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
S=$RESEARCH_RUN_DIR/inputs/programs3.py
ROWS=${*:-101 11 39 60 57 73 74 75 70 68 67 23}
echo "start $(date -u +%FT%TZ) head $T base $B rows $ROWS"
for r in $ROWS; do
  art=$(awk -v r=$r '$1==r && $2=="records"{print $3}' /workspace/c2/logs/prefetch.txt)
  d=/workspace/c2/rec/$r
  if [ ! -s "$d/.ok" ]; then
    rm -rf "$d"
    PYTHONPATH=$T/tools/research/src python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>> "$OUT/fetch.err" \
      && echo "$art" > "$d/.ok" || { echo "FETCH-FAIL $r $art"; continue; }
  fi
  echo "fetched $r $(du -sm $d | cut -f1) MB $(find $d -name descriptor.json.gz | wc -l) descriptors"
done
for r in $ROWS; do for s in base head; do echo "$s $r"; done; done | xargs -P 4 -n 2 bash -c '
  s=$0; r=$1; if [ $s = base ]; then tr='"$B"'; else tr='"$T"'; fi
  C2_TREE=$tr PYTHONPATH=$tr/integrations/vllm:$tr/packages/verity/src:$tr/tools/research/src \
    python '"$S"' $s /workspace/c2/rec/$r '"$OUT"'/json/$s-$r.json > '"$OUT"'/$s-$r.log 2>&1
  echo "$s $r rc=$? $(date -u +%T)"; cat '"$OUT"'/$s-$r.log | grep -v "^\s*$" | tail -40'
echo "done $(date -u +%FT%TZ)"
