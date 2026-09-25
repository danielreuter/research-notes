#!/bin/bash
# Definition closures of every stored Program's top-level calls (specs3.py): materialize the programs trees from the local
# store, extract the spec ids once (/workspace/c2/specs3/SPECS.json), then close them through each tree given.
# From the shipped source root (research run --cwd source).  Local store only, no key.
#   usage: specs3.sh SIDE=TREE [SIDE=TREE ...]      e.g. base=/workspace/base head=$PWD
T=$PWD
OUT=${RESEARCH_RUN_DIR:-/workspace/c2/specs3-run}; mkdir -p "$OUT" /workspace/c2/progs /workspace/c2/specs3
[ -e /root/r2ro.env ] && { echo "refusing: /root/r2ro.env present"; exit 4; }
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
export PATH=/workspace/venv312/bin:$PATH PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
S=$RESEARCH_RUN_DIR/inputs/specs3.py
SPECS=/workspace/c2/specs3/SPECS.json
ROWS="11 23 39 57 60 67 68 70 73 74 75 101"
echo "start $(date -u +%FT%TZ) source $T sides $*"
if [ ! -s $SPECS ]; then
  for r in $ROWS; do
    art=$(awk -v r=$r '$1==r && $2=="programs"{print $3}' /workspace/c2/logs/prefetch.txt)
    d=/workspace/c2/progs/$r
    if [ ! -s "$d/.ok" ]; then
      rm -rf "$d"
      PYTHONPATH=$T/tools/research/src python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>> "$OUT/fetch.err" \
        && echo "$art" > "$d/.ok" || { echo "FETCH-FAIL $r $art"; exit 5; }
    fi
    echo "programs $r $art $(du -sm $d | cut -f1) MB $(find $d -name instances.json.gz | wc -l) instances"
  done
  C2_TREE=$T PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src C2_NPROC=8 python $S extract $ROWS $SPECS.tmp \
    && mv $SPECS.tmp $SPECS || { echo "EXTRACT-FAIL"; exit 6; }
fi
cp $SPECS "$OUT/SPECS.json"
for a in "$@"; do
  side=${a%%=*}; tr=${a#*=}
  ( C2_TREE=$tr PYTHONPATH=$tr/integrations/vllm:$tr/packages/verity/src python $S closure $side $SPECS "$OUT/closure-$side.json" \
      > "$OUT/closure-$side.log" 2>&1; echo "closure $side rc=$? $(date -u +%T)" ) &
done
wait
for a in "$@"; do grep -E " row | done|Error" "$OUT/closure-${a%%=*}.log" | head -40; done
echo "done $(date -u +%FT%TZ)"
