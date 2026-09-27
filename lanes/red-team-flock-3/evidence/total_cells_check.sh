#!/usr/bin/env bash
# red-team-flock-3: TG6 + PB1-PB4 + CN (gemm_cell_check.py: my CPU replay of every recorded session with a build of the cell's
# commit, other-session / swapped-rep negatives, instance files regenerated from the registered input set) and the shared-NAT
# placement (nat_check.py, PR #91's assess on the runs' own probes) for flock-backend's 9 total-unit L40S cells.
set -uo pipefail
E=$(cd "$(dirname "$0")" && pwd)
export PYTHONPATH=/workspace/tools/research/src:${PYTHONPATH:-} PL=/tmp/rtf3/placement_852816d6.py
CELLS="art:199bccee art:c6b96f7e art:c3a3d2c7 art:3e1bf074 art:5bdcd1d1 art:216143fd art:3367e633 art:b1e5fed5 art:062f4951"
python3 $E/nat_check.py $CELLS
for a in $CELLS; do
  python3 $E/gemm_cell_check.py $a --regen 2>&1 | grep -E '^GEMMCELL|^regen|Traceback|Error' | cut -c1-3000
done
