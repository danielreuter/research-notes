#!/bin/bash
# rl_check.sh TREE TAG [gates]  -- relayout check on a git-archive tree: imports of every module, pytest collection (default testpaths
# and everything collectible), then optionally the cleanup-2 gates (lints / main / extra / real-HF / research / core / root) with the
# test paths of whichever layout TREE has.  Logs /workspace/relayout/logs/TAG/.
T=$1; TAG=$2; L=/workspace/relayout/logs/$TAG; mkdir -p $L; LOCK=/workspace/ramlock/integrator-relayout-$TAG.json
echo "{\"owner\":\"integrator\",\"gb\":48,\"started\":\"$(date -u +%FT%TZ)\",\"pid\":$$,\"note\":\"lane/vllm-relayout check @ $(cat $T/.sha) ($TAG)\"}" > $LOCK
trap "rm -f $LOCK" EXIT
export PYTHONPATH=$T/packages/verity/src:$T/integrations/vllm:$T/tools/research/src:$T/backends/numerical/python:/workspace/p5_tools
export OMP_NUM_THREADS=3
unset VERITY_REGRESSION
PY=/workspace/venv312/bin/python
run() { $PY -c "import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execv(sys.executable, [sys.executable, \"-m\", \"pytest\", *sys.argv[1:]])" "$@"; }
V=$T/integrations/vllm
if [ -d $V/verity_capture ]; then
  ALL="tests verity_capture verity_vllm"; [ -d $V/verity_vllm_numerics ] && ALL="$ALL verity_vllm_numerics"; [ -d $V/verity_vllm_adapter ] && ALL="$ALL verity_vllm_adapter"
  RH="tests/ir/test_derive_realhf.py tests/ir/test_derive_hf5b_realhf.py"; PB=tests/test_pod_bootstrap.py
else
  ALL="tests verity_vllm"; RH="tests/program/test_derive_realhf.py tests/program/test_derive_hf5b_realhf.py"; PB=tests/ops/test_pod_bootstrap.py
fi
IGN=""; for f in $RH; do IGN="$IGN --ignore=$f"; done
echo "start $(date -u +%FT%TZ) sha $(cat $T/.sha) tag $TAG"
[ -d $T/.git ] || ( cd $T && git init -q . && git add -A >/dev/null 2>&1 && git -c user.name=x -c user.email=x commit -qm tree >/dev/null )   # test_relayout_map reads git ls-files
cd $V
$PY /workspace/relayout/rl_imports.py $V $L/imports.json > $L/imports.log 2>&1; echo "imports: $(tail -1 $L/imports.log) $(date -u +%FT%TZ)"
run --collect-only -q -p no:cacheprovider > $L/collect_default.txt 2>&1; echo "collect default exit $? $(tail -1 $L/collect_default.txt)"
run --collect-only -q -p no:cacheprovider $ALL > $L/collect_all.txt 2>&1; echo "collect all exit $? $(tail -1 $L/collect_all.txt)"
[ "$3" = gates ] || { echo "done $(date -u +%FT%TZ)"; exit 0; }
( cd $T
  run tools/research/tests -rfE -p no:cacheprovider --junitxml=$L/research.xml > $L/research.log 2>&1; echo "research exit $? $(date -u +%FT%TZ)"
  run packages/verity/tests -n 4 --dist loadfile -rfE -p no:cacheprovider --junitxml=$L/core.xml > $L/core.log 2>&1; echo "core exit $? $(date -u +%FT%TZ)"
  run tests -rfE -p no:cacheprovider --junitxml=$L/root.xml > $L/root.log 2>&1; echo "root exit $? $(date -u +%FT%TZ)" ) &
run tests/test_no_by_name_rules.py tests/test_no_dead_modules.py -rfE -p no:cacheprovider --junitxml=$L/lints.xml > $L/lints.log 2>&1
echo "lints exit $? $(date -u +%FT%TZ)"
run -n 10 --dist loadfile $IGN -rfE -p no:cacheprovider --junitxml=$L/main.xml > $L/main.log 2>&1
echo "main exit $? $(date -u +%FT%TZ)"
run tests/acquire tests/test_no_by_name_rules.py $PB tests/regression -rfE -p no:cacheprovider --junitxml=$L/extra.xml > $L/extra.log 2>&1
echo "extra exit $? $(date -u +%FT%TZ)"
run -n 8 --dist load $RH -rfE -p no:cacheprovider --junitxml=$L/realhf.xml > $L/realhf.log 2>&1
echo "realhf exit $? $(date -u +%FT%TZ)"
if [ -d verity_capture ]; then   # tests the old testpaths never collected but the moved tree's `tests` does
  run verity_vllm/commit_bench tests/test_relayout_map.py -rfE -p no:cacheprovider --junitxml=$L/more.xml > $L/more.log 2>&1
  echo "more exit $? $(date -u +%FT%TZ)"
fi
wait; echo "done $(date -u +%FT%TZ)"
