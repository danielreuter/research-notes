#!/usr/bin/env bash
# ligero-hygiene item 3: leaf/conformance_test::test_committed_operand_negatives_rejected[dummy|poseidon2|sha256] on an
# unloaded CPU pod, sequentially (one case at a time, all cores), each under cProfile, long timeout.  --cwd source.
set -uo pipefail
W=/workspace; O=${RESEARCH_RUN_DIR:-$W/ligero-hygiene}; mkdir -p "$O"
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null 2>&1 || curl -fsSL https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
PY=$W/venv312/bin/python
[ -x "$PY" ] || uv venv $W/venv312 --python 3.12 2>&1 | tail -1
"$PY" -c "import torch" 2>/dev/null || uv pip install --python "$PY" --index-url https://download.pytorch.org/whl/cpu "torch==2.6.0" 2>&1 | tail -1
uv pip install --python "$PY" numpy blake3 pytest pytest-timeout 2>&1 | tail -1
q=$(awk '{print $1}' /sys/fs/cgroup/cpu.max 2>/dev/null); p=$(awk '{print $2}' /sys/fs/cgroup/cpu.max 2>/dev/null)
T=$(nproc); [ -n "$q" ] && [ "$q" != max ] && T=$((q / p))
export OMP_NUM_THREADS=$T MKL_NUM_THREADS=$T OPENBLAS_NUM_THREADS=$T VY_CPU_THREADS=$T
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/tools/research/src:$PWD"
echo "=== $(date -u +%H:%M:%SZ) source ${RESEARCH_SOURCE_SHA:-?} nproc $(nproc) quota $T load $(cat /proc/loadavg)"; grep -m1 'model name' /proc/cpuinfo
rc=0
for s in ${SCHEMES:-dummy poseidon2 sha256}; do
  echo "=== $(date -u +%H:%M:%SZ) [$s] start load $(cat /proc/loadavg)"
  "$PY" -m cProfile -o "$O/prof_$s.pstats" -m pytest -p no:cacheprovider -q -rfEs --timeout ${TIMEOUT:-7200} --durations=5 \
    "backends/direct/ligero/leaf/conformance_test.py::test_committed_operand_negatives_rejected[$s]" 2>&1 | tee "$O/pytest_$s.log" | tail -12
  r=${PIPESTATUS[0]}; [ $r -eq 0 ] || rc=1
  echo "=== $(date -u +%H:%M:%SZ) [$s] rc=$r load $(cat /proc/loadavg)"
  "$PY" -c "import pstats; pstats.Stats('$O/prof_$s.pstats').sort_stats('cumulative').print_stats(25)" > "$O/prof_$s.txt" 2>&1
  "$PY" -c "import pstats; pstats.Stats('$O/prof_$s.pstats').sort_stats('tottime').print_stats(15)" >> "$O/prof_$s.txt" 2>&1
done
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"; exit $rc
