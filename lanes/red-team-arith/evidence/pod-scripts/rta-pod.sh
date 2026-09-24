#!/usr/bin/env bash
# red-team-arith (pod side, through `research run --on POD --cwd /workspace/src --send rta-trees.tgz --send rta-pod.sh`):
#   bash rta-pod.sh STEP TARGET [CONFIG...]
# STEP tests : tests_fused_test.py (arith's bit-exactness vs the old kernels) + redteam_arith_test.py --big (adversarial)
# STEP ab    : end-to-end A/B, every os.urandom draw deterministic (redteam_arith_det.py), same frozen instances,
#              one tree per commit: base 22741456, 9d1a7f15, 0baefa9d, f550fdc6, 92ea2531, tip (= /workspace/src, 92dab0ad
#              + this lane's test files).  CONFIG = NAME:REL:L:P[:extra bench-vu args, comma-separated]
#              Proof dumps (rep 1) compared by sha256 of every .stmt/.proof/.hproof/.coins + system.bin.
# Outputs under /workspace/red-team-arith/TARGET/, summaries copied into $RESEARCH_RUN_DIR.
set -uo pipefail
source /workspace/env.sh
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 LIGERO_REFERENCE_HINTS=0
STEP=$1 TGT=$2; shift 2
A=/workspace/red-team-arith/$TGT; mkdir -p $A
RD=${RESEARCH_RUN_DIR:-/tmp}
SRC=/workspace/src
TIP=$(python3 -c 'import json; print(json.load(open("/workspace/src/.research-source.json"))["commit"])' 2>/dev/null || echo tip)
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
nvidia-smi --query-gpu=name,compute_cap,driver_version --format=csv,noheader | tee $RD/gpu.txt

if [ "$STEP" = tests ]; then
  cd $SRC
  $PY -m backends.direct.ligero.tests_fused_test --reps 2 --out $A/tests_fused_test.json > $A/tests_fused_test.log 2>&1
  echo "tests_fused_test rc=$? $(grep -E '^bit-exact' $A/tests_fused_test.log)" | tee $RD/tests.txt
  $PY -m backends.direct.ligero.redteam_arith_test --big --out $A/redteam_arith_test.json > $A/redteam_arith_test.log 2>&1
  echo "redteam_arith_test rc=$? $(grep -E '^red-team verdict' $A/redteam_arith_test.log)" | tee -a $RD/tests.txt
  grep -E '^(FAIL|ERROR)' $A/redteam_arith_test.log | head -40 | tee -a $RD/tests.txt
  cp $A/tests_fused_test.json $A/tests_fused_test.log $A/redteam_arith_test.json $A/redteam_arith_test.log $RD/ 2>/dev/null
  exit 0
fi

# trees: hard-linked copies of the tip tree with the 4 changed prover files replaced by each commit's
if [ ! -f /workspace/red-team-arith/trees/.done ]; then
  mkdir -p /workspace/red-team-arith/trees && tar xzf $RD/inputs/rta-trees.tgz -C /workspace/red-team-arith/trees
  touch /workspace/red-team-arith/trees/.done
fi
tree_of() {   # REV -> source dir
  local r=$1
  [ "$r" = tip ] && { echo $SRC; return; }
  local d=/workspace/red-team-arith/src-$r
  if [ ! -d $d ]; then
    cp -al $SRC $d
    for f in pipeline.py protocol.py relchain.py tests_fused.py; do
      rm -f $d/backends/direct/ligero/$f
      cp /workspace/red-team-arith/trees/$r/backends/direct/ligero/$f $d/backends/direct/ligero/$f
    done
    find $d/backends/direct/ligero/__pycache__ -name '*.pyc' -delete 2>/dev/null
  fi
  echo $d
}
REVS=${REVS:-22741456 9d1a7f15 0baefa9d f550fdc6 92ea2531 tip}
SUM=$A/ab-summary.txt
for cfg in "$@"; do
  IFS=: read -r name rel l p extra <<< "$cfg"
  xargs=(); [ -n "${extra:-}" ] && IFS=, read -r -a xargs <<< "$extra"
  for r in $REVS; do
    d=$(tree_of $r); o=$A/ab/$name/$r; rm -rf $o; mkdir -p $o
    commit=$([ $r = tip ] && echo $TIP || cat /workspace/red-team-arith/trees/$r/COMMIT)
    t0=$(date +%s)
    (cd $d && PYTHONPATH="$d/packages/verity/src:$d/backends/numerical/python:$d/tools/research/src:$d" RESEARCH_GIT_COMMIT=$commit \
      $PY -m backends.direct.ligero.redteam_arith_det $o/urandom-trace.json -- --relation $rel bench-vu --zk --mode interactive \
        --batch $l --pipeline $p --total-vus 4096 --target -128 --reps 1 --out $o/result.json --dump-dir $o/proofs --dump-reps 1 \
        ${xargs[@]+"${xargs[@]}"} > $o/log 2>&1)
    rc=$?
    (cd $o/proofs 2>/dev/null && find . -type f \( -name '*.stmt' -o -name '*.proof' -o -name '*.hproof' -o -name '*.coins' -o -name system.bin \) \
      | sort | xargs sha256sum > $o/sha256.txt)
    agg=$(sha256sum < $o/sha256.txt | cut -c1-16)
    nf=$(wc -l < $o/sha256.txt)
    tr=$($PY -c "import json,hashlib; t=json.load(open('$o/urandom-trace.json'))['last_pass']; print(len(t), hashlib.sha256(json.dumps([(x['job'],x['i'],x['n']) for x in t]).encode()).hexdigest()[:12])" 2>/dev/null)
    echo "$(date -u +%H:%M:%SZ) $name $r commit=${commit:0:8} rc=$rc wall=$(( $(date +%s) - t0 ))s files=$nf dumps_sha=$agg urandom_last_pass=[$tr]" | tee -a $SUM
    [ $rc = 0 ] || tail -5 $o/log | sed 's/^/    /' | tee -a $SUM
  done
  base=$A/ab/$name/$(echo $REVS | cut -d' ' -f1)/sha256.txt
  for r in $REVS; do
    f=$A/ab/$name/$r/sha256.txt
    if [ -s $f ] && [ -s $base ] && cmp -s $f $base; then v=IDENTICAL; else v="DIFFERENT($(diff $base $f 2>/dev/null | grep -c '^>') files)"; fi
    echo "  $name $r vs $(echo $REVS | cut -d' ' -f1): $v" | tee -a $SUM
  done
  if [ -x "${LIGERO_VERIFY:-}" ] && [ -d $A/ab/$name/tip/proofs ]; then
    timeout 600 $LIGERO_VERIFY $A/ab/$name/tip/proofs > $A/ab/$name/tip/rust-verify.log 2>&1
    echo "  $name tip rust ligero-verify rc=$? $(tail -1 $A/ab/$name/tip/rust-verify.log)" | tee -a $SUM
  fi
done
cp $SUM $RD/ 2>/dev/null
echo DONE-ab
