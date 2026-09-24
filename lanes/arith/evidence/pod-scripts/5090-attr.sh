#!/usr/bin/env bash
# arith 5090 attribution: the tip looked slower than base on fp4-nvf4 l=8192 p8. Arms: base, baseh (main kernels + the
# harness commits), tip, tipnf (tip with pipeline.FIXED_SLOTS = False). 3 rotating rounds. Diagnostic trees; meta only.
source /workspace/arith/scripts/lib.sh
while pgrep -f "[5]090-ab.sh" >/dev/null; do sleep 5; done
rm -rf /workspace/src-tipnf && cp -a /workspace/src /workspace/src-tipnf && sed -i 's/^FIXED_SLOTS = True$/FIXED_SLOTS = False/' /workspace/src-tipnf/backends/direct/ligero/pipeline.py
echo "tipnf: $(grep -c '^FIXED_SLOTS = False' /workspace/src-tipnf/backends/direct/ligero/pipeline.py) FIXED_SLOTS=False" | tee -a $LOG
BASE=227414560b6588f8e99336686ff01af8144ee2e7
arm() {
  case $1 in
    base) SRC=/workspace/src-base COMMIT=$BASE run f4a-base-r$2 fp4-nvf4 8192 8 5 ;;
    baseh) SRC=/workspace/src-baseh COMMIT=$BASE-harness run f4a-baseh-r$2 fp4-nvf4 8192 8 5 ;;
    tip) SRC=/workspace/src COMMIT=$TIP run f4a-tip-r$2 fp4-nvf4 8192 8 5 ;;
    tipnf) SRC=/workspace/src-tipnf COMMIT=$TIP-nofixedslots run f4a-tipnf-r$2 fp4-nvf4 8192 8 5 ;;
  esac
}
for rr in 1 2 3; do
  case $rr in 1) o="base baseh tip tipnf";; 2) o="tipnf tip baseh base";; 3) o="tip base tipnf baseh";; esac
  for a in $o; do arm $a $rr; done
done
echo DONE-attr
