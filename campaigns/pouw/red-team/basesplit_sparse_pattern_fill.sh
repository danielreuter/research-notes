#!/usr/bin/env bash
# fill: owner=bc-d7d4b0d1 gpus=1 on=2-4 max_min=8 cpus=8 project=pous prio=10 mem_gb=32
# The assessor (bc-d7d4b0d1): does the sm_120 sparse NVFP4 kernel reproduce the exact words on operands that meet the
# hardware's sparse rule with two nonzero pairs per 8-chunk (pairs2) and with one (pairs1, the split's ΔA shape)?
set -uo pipefail
W=/workspace/pouw/fill-out/assessor-basesplit-e2e
[ -n "${GPU_LEASE_UUID:-}" ] || exit 3
for s in pairs2 pairs1; do
  mkdir -p $W/dumps/$s
  for v in dense128 sparse; do $W/bin/$v check $W/ops/$s $W/dumps/$s || exit 1; done
done
echo "{\"uuid\":\"$GPU_LEASE_UUID\",\"t\":\"$(date -u +%FT%TZ)\"}" > $W/dumps/pattern-run.json
exit 0
