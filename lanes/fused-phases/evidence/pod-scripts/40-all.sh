#!/usr/bin/env bash
# fused-phases: the seeded pre/post pairs of every cell (byte-identical proofs; no idle GPU needed), then the registrable runs
# (lane tip, genuine os.urandom, 5 reps, each on an empty GPU).
S=/workspace/fused-phases/scripts
CELLS="v3x4-p8 v3x4-p4 v3-p8 v3-p4 v1-p4" KINDS=seed bash $S/30-cells.sh
CELLS="v3x4-p8 v3x4-p4 v3-p8 v3-p4 v1-p4" KINDS=real bash $S/30-cells.sh
echo ALL_DONE
