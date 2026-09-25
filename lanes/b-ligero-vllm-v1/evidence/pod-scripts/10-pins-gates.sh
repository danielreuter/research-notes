#!/usr/bin/env bash
# b-ligero-vllm-v1: the lane's torch/GPU tests, the conformance suite on +vllm-v1, rebuild ligero-verify from the synced tree,
# leaf.fixtures (compose, one proved sub-batch, system-digest -> the leaf.rs PINS row, Rust verify with --allow-any-system),
# then the gate (honest sub-batches + the committed-operand negatives battery).
# research run --on vy-b-ligero-vllm-v1-4090 --project verity --cwd /workspace/src --send lib.sh --send 10-pins-gates.sh \
#     --env RELS=fp8-ada-x4 -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/10-pins-gates.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:-/workspace/b-ligero-vllm-v1/pins}; mkdir -p $RD
GATE_VUS=${GATE_VUS:-2048}
export PATH="$HOME/.cargo/bin:$PATH" CARGO_TARGET_DIR=/workspace/cargo-target
( cd backends/ligero-verify && cargo build --release 2>&1 | tail -1 && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ && sha256sum /workspace/bin/ligero-verify
  cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked" | head -10 )
$PY -m pytest -q backends/direct/ligero/vllm_tree_test.py backends/direct/ligero/leaf/vllm_v1_test.py > $RD/lane-tests.log 2>&1; echo "lane tests rc=$?"; tail -3 $RD/lane-tests.log
if [ "${CONF:-1}" = 1 ]; then
  for rel in ${CONF_RELS:-fp8-ada-x4}; do
    echo "=== $(date -u +%H:%M:%SZ) conformance vllm-v1 on $rel"
    VERITY_LEAF_CONFORMANCE_REL=$rel timeout 1800 $PY -m pytest -q -x backends/direct/ligero/leaf/conformance_test.py -k vllm > $RD/conf-$rel.log 2>&1
    echo "rc=$?"; tail -8 $RD/conf-$rel.log
  done
fi
for rel in ${RELS:-fp8-ada-x4}; do
  echo "=== $(date -u +%H:%M:%SZ) fixture $rel+vllm-v1"
  $PY -u -m backends.direct.ligero.leaf.fixtures --relation $rel --leaf vllm-v1 --device cuda --out $RD/fixtures/$rel-vllm-v1 > $RD/fixture-$rel.log 2>&1
  echo "rc=$?"; tail -6 $RD/fixture-$rel.log
  d=$RD/fixtures/$rel-vllm-v1
  /workspace/bin/ligero-verify system-digest --system $d/system.bin | head -c 400; echo
  /workspace/bin/ligero-verify batch --system $d/system.bin --dir $d --jobs 1 --threads 4 --target-bits 128 --allow-any-system > $d/rust_batch.out 2>&1
  echo "$rel rust batch (allow-any-system) rc=$? $(tail -n 2 $d/rust_batch.out | cut -c1-400)"
  [ "${GATES:-1}" = 1 ] || continue
  gpu_idle
  echo "=== $(date -u +%H:%M:%SZ) gate $rel+vllm-v1 --vus $GATE_VUS --batch ${GATE_BATCH:-4096}"
  t0=$(date +%s)
  $PY -u -m backends.direct.ligero.run --relation $rel+vllm-v1 gate-vu --vus $GATE_VUS --batch ${GATE_BATCH:-4096} --zk --mode interactive \
      --auth included-hash --target -128 --device cuda --instance-procs 12 --out $RD/gate-$rel.json > $RD/gate-$rel.log 2>&1
  echo "rc=$? wall=$(( $(date +%s) - t0 ))s"; tail -8 $RD/gate-$rel.log
done
