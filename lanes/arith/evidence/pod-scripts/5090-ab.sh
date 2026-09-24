#!/usr/bin/env bash
# arith 5090 port: base (main 22741456) vs tip, fp4-nvf4 l=8192 p8 local coins (cell art:d5c9e1f3, fp4/chain.py), 4
# alternating rounds, then register + reverify + preserved.
while pgrep -f "[p]od_bootstrap.sh" >/dev/null; do sleep 5; done
grep -q BOOTSTRAP_OK /workspace/arith/bootstrap.log || { echo "NO BOOTSTRAP_OK"; exit 1; }
ROUNDS=${ROUNDS:-4} bash /workspace/arith/scripts/port-ab.sh f4 fp4-nvf4 8192 8
echo DONE-5090
