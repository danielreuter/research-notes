#!/usr/bin/env bash
# gates.sh: brief §2 gates on vy-dev-h100 from the frozen tree (cwd): gate-vu --vus 2048 --batch 16384 for bf16-hopper and fp8-hopper,
# bare and --auth included-hash; then the live-verifier probe.  Every gate's rc is printed; the script's rc is the OR of them.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
PY=/workspace/venv312/bin/python
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/tools/research/src:$PWD"
RD=${RESEARCH_RUN_DIR:-/tmp}
fail=0
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
stage "pytest backends/direct/ligero -q -x  (bootstrap run: collection ERROR in privsel/relation_test.py = relmin-private, failing on main per the brief; here again, then without privsel)"
"$PY" -m pytest backends/direct/ligero -q -x -p no:cacheprovider > "$RD/pytest_full.log" 2>&1; echo "PYTEST_FULL rc=$?"; tail -4 "$RD/pytest_full.log"
"$PY" -m pytest backends/direct/ligero -q -x -p no:cacheprovider --ignore=backends/direct/ligero/privsel > "$RD/pytest_noprivsel.log" 2>&1; rc=$?; echo "PYTEST_NOPRIVSEL rc=$rc"; tail -4 "$RD/pytest_noprivsel.log"
[ $rc -eq 0 ] || fail=1
for rel in bf16-hopper fp8-hopper; do
  for auth in "" "--auth included-hash"; do
    tag="${rel}${auth:+-hash}"
    stage "gate-vu $rel $auth"
    t0=$(date +%s)
    "$PY" -m backends.direct.ligero.run --relation "$rel" gate-vu --vus 2048 --batch 16384 --device cuda $auth \
        --instance-procs 16 --instances-cache /workspace/instances-cache > "$RD/gate_${tag}.log" 2>&1
    rc=$?
    echo "GATE $tag rc=$rc wall=$(( $(date +%s) - t0 ))s"
    tail -25 "$RD/gate_${tag}.log"
    [ $rc -eq 0 ] || fail=1
  done
done
stage "live probe"
"$PY" -m backends.direct.ligero.live probe --verifier tcp://213.173.105.69:30899 --mb 0.5 --repeat 6 2>&1 | tail -12
stage "done"
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader; cat /proc/loadavg
if [ $fail -eq 0 ]; then echo GATES_OK; else echo GATES_FAILED; exit 1; fi
