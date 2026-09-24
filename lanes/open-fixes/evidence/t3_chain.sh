#!/bin/bash
PY=/workspace/venv312/bin/python
mkdir -p /workspace/results /workspace/dumps
B="bench-vu --zk --mode interactive --batch 16384 --pipeline 4 --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache --dump-reps 1"
/workspace/run.sh /workspace/src t3_v3_p4_16k $PY -m backends.direct.ligero.run --relation fp8-ada-v3 $B --dump-dir /workspace/dumps/t3_v3_p4 --out /workspace/results/t3_v3_p4.json
/workspace/run.sh /workspace/src t3_v1_p4_16k $PY -m backends.direct.ligero.run --relation fp8-ada $B --dump-dir /workspace/dumps/t3_v1_p4 --out /workspace/results/t3_v1_p4.json
for d in t3_v3_p4 t3_v1_p4; do
  for r in /workspace/dumps/$d/rep*; do
    /workspace/bin/ligero-verify batch --system /workspace/dumps/$d/system.bin --dir $r --json /workspace/results/${d}_rust_$(basename $r).json > /workspace/logs/${d}_rust_$(basename $r).log 2>&1; echo "$d $(basename $r) rust rc=$?" >> /workspace/logs/t3_rust.log
  done
done
echo T3_CHAIN_DONE >> /workspace/logs/t3_rust.log
