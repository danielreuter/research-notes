#!/usr/bin/env bash
# pytest backends/direct/ligero on the post-freeze tree 11c7075 (cwd = the shipped tree), thread-bounded, per-test timeout.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
PY=/workspace/venv312/bin/python
export LIGERO_VERIFY=/workspace/bin/ligero-verify
export OMP_NUM_THREADS=16 TORCH_NUM_THREADS=16 MKL_NUM_THREADS=16
echo "=== [$(date -u +%H:%M:%S)] pytest backends/direct/ligero -q --ignore=backends/direct/ligero/privsel -x --timeout 600 --durations=15"
find backends/direct/ligero -name '._*' -delete 2>/dev/null
"$PY" -m pytest backends/direct/ligero -q --ignore=backends/direct/ligero/privsel -x --timeout 600 --durations=15 -p no:cacheprovider 2>&1 | tail -60
rc=${PIPESTATUS[0]}
echo "=== [$(date -u +%H:%M:%S)] pytest rc=$rc"
echo
echo "=== [$(date -u +%H:%M:%S)] pytest backends/direct/ligero/pipeline_race_test.py -v"
"$PY" -m pytest backends/direct/ligero/pipeline_race_test.py -v --timeout 600 -p no:cacheprovider 2>&1 | tail -15
echo "=== [$(date -u +%H:%M:%S)] pipeline_race_test rc=${PIPESTATUS[0]}"
exit $rc
