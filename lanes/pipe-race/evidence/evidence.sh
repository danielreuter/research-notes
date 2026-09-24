#!/usr/bin/env bash
# Evidence runs on the FIXED tree (sequential: one GPU workload at a time).
source /workspace/env.sh; tree fix
OUT=/workspace/prace/fix; mkdir -p $OUT
echo "=== [$(date -u +%H:%M:%S)] kernel race test (fixed): l=16384/8192/4096, plain + ZK(t_pad=256)"
for l in 16384 8192 4096; do for tp in 0 256; do $PY /workspace/prace/enc_race.py $l 3769 20 $tp 2>&1 | grep RESULT; done; done
echo "=== [$(date -u +%H:%M:%S)] prover harness zk depth 4,3 x 5 runs (65 sub-batches each)"
$PY -m backends.direct.ligero.pipeline_race_test --relation fp8-ada --total-vus 4096 --batch 16384 --depth 4 3 2 --runs 5 2>&1 | tail -20
echo "=== [$(date -u +%H:%M:%S)] prover harness NO-zk depth 1,4,3 x 3 runs + byte identity"
$PY -m backends.direct.ligero.pipeline_race_test --relation fp8-ada --total-vus 4096 --batch 16384 --depth 1 4 3 --runs 3 --no-zk 2>&1 | tail -14
echo "=== [$(date -u +%H:%M:%S)] bench-vu p4 with dumps (3 reps, dump 3) for the Rust verifier"
$PY -m backends.direct.ligero.run --relation fp8-ada bench-vu --zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 --pipeline 4 --target -128 --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache --out $OUT/p4.json --dump-dir $OUT/dumps_p4 --dump-reps 3 > $OUT/p4.log 2>&1; echo "bench p4 exit $?"; grep -E "^rep|t.total|REJECT|Error|assert" $OUT/p4.log | head -12
echo "=== [$(date -u +%H:%M:%S)] bench-vu p2 (3 reps) for the t.total comparison"
$PY -m backends.direct.ligero.run --relation fp8-ada bench-vu --zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 --pipeline 2 --target -128 --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache --out $OUT/p2.json > $OUT/p2.log 2>&1; echo "bench p2 exit $?"; grep -E "^rep|t.total" $OUT/p2.log | head -8
echo "=== [$(date -u +%H:%M:%S)] Rust ligero-verify batch on the p4 dumps"
for r in 1 2 3; do /workspace/bin/ligero-verify batch --dir $OUT/dumps_p4/rep$r --system $OUT/dumps_p4/system.bin --target-bits 128 2>&1 | tail -2; done
echo "=== [$(date -u +%H:%M:%S)] EVIDENCE_DONE"
