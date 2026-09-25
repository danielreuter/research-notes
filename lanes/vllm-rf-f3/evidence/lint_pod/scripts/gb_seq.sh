#!/bin/bash
# gate (b) at the rebased head, then at main, on this pod one after the other (-n 12 --dist loadfile, OMP_NUM_THREADS=3: the settings of
# the green run at 4fb0eb2c), each in a fresh copy of its tree.
#   usage: gb_seq.sh      logs: /workspace/rff3/logs/gb_{head,main}.{log,xml,env,rss}, logs/gb_seq.DONE
cd /workspace/rff3 || exit 3
export OMP_NUM_THREADS=3
for pair in head:/workspace/head main:/workspace/main; do
  TAG=${pair%%:*}; T=${pair#*:}; C=$T-gb
  rm -rf "$C"; cp -a "$T" "$C"
  ./gate_b.sh "$C" gb_$TAG -n 12 --dist loadfile
done
touch logs/gb_seq.DONE
