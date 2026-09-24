#!/usr/bin/env bash
# verify-night: re-run the instance-equiv/v1 checker on the 15 registered files (a) --check, (b) regenerate from scratch.
# Tree: lane/verify-night @ 1b3c7be6 (= fused-phases 9989797f's instance_equiv.py). Outputs under /workspace/verify-night/equiv-*.
cd /workspace/src && source /workspace/env.sh
O=/workspace/verify-night
( echo "=== check $(date -u +%H:%M:%S)"
  $PY -m verity_numerical.bench.instance_equiv --check $O/equiv/*.json/*.json; echo "check rc=$?"
  echo "=== regen $(date -u +%H:%M:%S)"
  $PY -m verity_numerical.bench.instance_equiv --out-dir $O/equiv-regen \
      $(for b in fp8-ada bf16-hopper fp8-hopper; do for s in v2 v3 v2x4 v3x4 x4; do echo --relation $b-$s; done; done); echo "regen rc=$?"
  echo "=== done $(date -u +%H:%M:%S)" ) > $O/equiv-check.out 2>&1
