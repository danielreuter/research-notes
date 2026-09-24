#!/usr/bin/env bash
# arith port A/B: base (main 22741456: the 5 changed files restored over the tip tree) vs tip, alternating, same frozen
# instances / K / B as the Table 2 cell.  Trees from base-trees.tgz (base = main's files, baseh = main + the tip's
# pipeline.py/relchain.py harness fix; diagnostic only).
#   ARMS="base tip" ROUNDS=3 bash port-ab.sh PREFIX REL L P [extra bench-vu args, e.g. --verifier tcp://127.0.0.1:7000]
source /workspace/arith/scripts/lib.sh
prefix=$1 rel=$2 l=$3 p=$4; shift 4
BASE=227414560b6588f8e99336686ff01af8144ee2e7
for t in base baseh; do
  if [ ! -d /workspace/src-$t ]; then
    cp -a /workspace/src /workspace/src-$t && tar xzf /workspace/arith/scripts/base-trees.tgz -C /tmp && cp -r /tmp/$t/. /workspace/src-$t/
    echo "tree src-$t: $(grep -c FIXED_SLOTS /workspace/src-$t/backends/direct/ligero/pipeline.py) FIXED_SLOTS, $(grep -c intt_rows /workspace/src-$t/backends/direct/ligero/tests_fused.py) intt_rows" | tee -a $LOG
  fi
done
arm() {
  case $1 in
    base) SRC=/workspace/src-base COMMIT=$BASE run $prefix-base-r$2 $rel $l $p 5 "${EXTRA[@]}" ;;
    baseh) SRC=/workspace/src-baseh COMMIT=$BASE-harness run $prefix-baseh-r$2 $rel $l $p 5 "${EXTRA[@]}" ;;
    tip) SRC=/workspace/src COMMIT=$TIP run $prefix-tip-r$2 $rel $l $p 5 "${EXTRA[@]}" ;;
  esac
}
EXTRA=("$@")
arms=(${ARMS:-base tip})
for rr in $(seq ${ROUNDS:-3}); do
  if [ $((rr % 2)) = 1 ]; then order="${arms[*]}"; else order=$(printf '%s\n' "${arms[@]}" | tac | tr '\n' ' '); fi
  for a in $order; do arm $a $rr; done
done
echo DONE-port-$prefix
