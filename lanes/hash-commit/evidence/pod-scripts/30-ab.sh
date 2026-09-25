#!/usr/bin/env bash
# hash-commit, 4090 fp8-ada l=8192 p4: the committer's tests on the tip, then ${ROUNDS:-3} alternating rounds of the four
# committers on one pod (base 6e1cc576 = main's; 5d14dafa row_sponge kernel; 515ed32a + frozen rows as arrays; tip 0b40ae8a
# + batch SHA framing), each commitment built 1 + $CREPS times.  The intermediate trees are the tip minus a reverse patch.
source /workspace/hash-commit/scripts/lib.sh
S=/workspace/hash-commit/scripts
declare -A FULL=([5d14dafa]=5d14dafad08778d4f9ee6ec477a6910774c0d0e1 [515ed32a]=515ed32a0e6cc5c31bcb2c5d584b8a3de01ac5cb)
declare -A TREE=([5d14dafa]=8c357d7220a5804cfa4d51b727317dc7ee37688a [515ed32a]=9d1f5f265b4714e457a0b0e2a8b4eb677c01571f)
for c in 5d14dafa 515ed32a; do
  t=/workspace/src-$c; rm -rf $t; cp -a /workspace/src $t
  ( cd $t && patch -R -p1 -s < $S/rev-to-$c.patch ) || { echo "patch $c failed" | tee -a $LOG; exit 1; }
  got=$(cd $t && GIT_DIR=$(mktemp -d) GIT_WORK_TREE=$t bash -c 'git init -q && git add -A . && git rm -q --cached .research-source.json && git write-tree')
  echo "tree $c: got $got want ${TREE[$c]}" | tee -a $LOG
  [ "$got" = "${TREE[$c]}" ] || exit 1
  $PY -c "import json,sys;p=sys.argv[1]+'/.research-source.json';d=json.load(open(p));d.update(commit=sys.argv[2],tree=sys.argv[3],dirty=False);json.dump(d,open(p,'w'),indent=1)" $t ${FULL[$c]} ${TREE[$c]}
done
[ -n "$SKIP_TESTS" ] || tests /workspace/src backends/direct/ligero/hashchain_test.py backends/direct/ligero/leaf_test.py
export CREPS=${CREPS:-5}
for R in $(seq ${R0:-2} $(( ${R0:-2} + ${ROUNDS:-3} - 1 ))); do
  run base-fp8ada-l8192-p4-r$R /workspace/src-base fp8-ada 8192 4 5
  run k5d14-fp8ada-l8192-p4-r$R /workspace/src-5d14dafa fp8-ada 8192 4 5
  run k515e-fp8ada-l8192-p4-r$R /workspace/src-515ed32a fp8-ada 8192 4 5
  run tip-fp8ada-l8192-p4-r$R /workspace/src fp8-ada 8192 4 5
done
