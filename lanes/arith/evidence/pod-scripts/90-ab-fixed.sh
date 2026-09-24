#!/usr/bin/env bash
# arith step 4 (4090): step 3 (f550fdc6, /workspace/src-s3) vs tip (+ fixed slot per sub-batch in prove_many),
# fp8-ada-v3x4 l=4096 p8, 4 rounds alternating. Pipeline race test first. Nothing else may run on the pod meanwhile.
source /workspace/arith/scripts/lib.sh
(cd /workspace/src && env -u PYTHONPATH PYTHONPATH="/workspace/src/packages/verity/src:/workspace/src/backends/numerical/python:/workspace/src" \
  $PY -m pytest -q -x backends/direct/ligero/pipeline_race_test.py > $A/pipeline_race_test-s4.out 2>&1; echo "pipeline_race_test s4 rc=$? $(tail -1 $A/pipeline_race_test-s4.out)" | tee -a $LOG)
arm() {
  case $1 in
    s3) SRC=/workspace/src-s3 COMMIT=f550fdc681e746f3963d71cb66625d4402d676fb run s4-s3-p8-r$2 fp8-ada-v3x4 4096 8 5 ;;
    tip) SRC=/workspace/src COMMIT=$TIP run s4-tip-p8-r$2 fp8-ada-v3x4 4096 8 5 ;;
  esac
}
for rr in 1 2 3 4; do
  if [ $((rr % 2)) = 1 ]; then order="s3 tip"; else order="tip s3"; fi
  for a in $order; do arm $a $rr; done
done
echo DONE-90
