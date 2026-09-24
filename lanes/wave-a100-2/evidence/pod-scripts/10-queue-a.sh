#!/usr/bin/env bash
# wave-a100-2 queue A (03:58Z): bare rounds 2 (reversed) + 3 over all six candidates, then committed local p4/p8 round 1.
cd /workspace/wave-a100/pod-scripts
B6="bare-v1p4:bf16-ampere:16384:4 bare-v1p8:bf16-ampere:16384:8 bare-v3p4:bf16-ampere-v3:16384:4 bare-v3p8:bf16-ampere-v3:16384:8 bare-x4p4:bf16-ampere-v3x4:4096:4 bare-x4p8:bf16-ampere-v3x4:4096:8"
bash 03-local.sh 2 $B6
bash 03-local.sh 3 $B6
bash 03-local.sh 1 shared64p4:bf16-ampere:16384:4:--auth,included-hash-shared,--tile,64x64 shared64p8:bf16-ampere:16384:8:--auth,included-hash-shared,--tile,64x64
echo "$(date -u +%H:%M:%S) QUEUE_A_DONE" >> /workspace/wave-a100/summary.txt
