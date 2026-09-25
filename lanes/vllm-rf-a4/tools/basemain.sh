#!/bin/bash
# base gate (b) at origin/main after the 8efb918e base run releases the lock.
exec 8>/workspace/a4/basemain.lock; flock -n 8 || { echo "already running"; exit 0; }
exec 9>/workspace/a4/base.lock; flock 9
echo "basemain start $(date -u +%FT%TZ)" >> /workspace/a4/logs/progress
bash /workspace/a4/lints.sh /workspace/basemain basemain >> /workspace/a4/logs/progress 2>&1
OMP_NUM_THREADS=3 bash /workspace/a4/gate_b.sh /workspace/basemain basemain-xdist -n 12 --dist loadfile >> /workspace/a4/logs/progress 2>&1
