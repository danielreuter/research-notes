#!/usr/bin/env bash
# wave-4090-2: after the local queue (cells-local.out says CELLS_DONE), the live phase against the same-DC verifier
# (vy-wave-4090-verifier, EU-RO-1, tcp://213.173.110.201:12166): bare headline candidates v3x4 p8 / p4 alternated over
# 3 rounds (p8,p4 / p4,p8 / p8,p4), then committed shared r1-r3, then the drill-downs.
cd /workspace/wave-4090
until grep -q CELLS_DONE cells-local.out 2>/dev/null; do sleep 10; done
CELLS="bare-v3x4-p8-r1 bare-v3x4-p4-r1 bare-v3x4-p4-r2 bare-v3x4-p8-r2 bare-v3x4-p8-r3 bare-v3x4-p4-r3 shared-r1 shared-r2 shared-r3 hash ajtai blake3" \
  MODES=live bash scripts/30-cells.sh
