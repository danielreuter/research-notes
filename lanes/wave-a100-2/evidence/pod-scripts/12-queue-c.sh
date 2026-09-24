#!/usr/bin/env bash
# wave-a100-2 queue C: after QUEUE_B_DONE, live round 4 over the bare candidates (reversed order), then the unshared
# +hash drill-down (bf16-ampere --auth included-hash, l=16384 p8) local + live, one cell each.
S=/workspace/wave-a100/summary.txt
until grep -q QUEUE_B_DONE $S; do sleep 10; done
cd /workspace/wave-a100/pod-scripts
bash 02-live.sh 4 v3p8:bf16-ampere-v3:16384:8 v3p4:bf16-ampere-v3:16384:4 x4p4:bf16-ampere-v3x4:4096:4
bash 03-local.sh 1 hashp8:bf16-ampere:16384:8:--auth,included-hash
bash 02-live.sh 1 hashp8:bf16-ampere:16384:8:--auth,included-hash
echo "$(date -u +%H:%M:%S) QUEUE_C_DONE" >> $S
