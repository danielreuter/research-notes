#!/bin/bash
# gate (b) at bbbe936c (/workspace/main5) once gate (b) at e818a5d4 has exited: same command, one run at a time on this pod
while ! grep -q "^exit" /workspace/out/gates/b_head5_x12.status 2>/dev/null; do sleep 15; done
OMP_NUM_THREADS=3 /workspace/rff24/gate_b.sh /workspace/main5 b_main5_x12 -n 12 --dist loadfile
