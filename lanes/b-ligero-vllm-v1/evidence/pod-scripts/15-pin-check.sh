#!/usr/bin/env bash
# b-ligero-vllm-v1: rebuild ligero-verify with the PINS row (sources touched: a synced tree can carry older mtimes than the
# build), cargo test, the PINNED batch verify of the fixture FIX_RUN wrote, the conformance suite on +vllm-v1, the gadget-row
# negatives, then the per-proof screen (CONFIGS) at 4096 VUs.
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
export PATH="$HOME/.cargo/bin:$PATH" CARGO_TARGET_DIR=/workspace/cargo-target
( cd backends/ligero-verify && touch src/*.rs && cargo build --release 2>&1 | tail -1 && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ && sha256sum /workspace/bin/ligero-verify
  cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked|vllm" | head -12 )
for d in /workspace/research/runs/${FIX_RUN:?}/fixtures/*; do
  $V system-digest --system $d/system.bin | head -c 300; echo
  $V batch --system $d/system.bin --dir $d --jobs 1 --threads 4 --target-bits 128 --json $RD/rust_batch_$(basename $d).json > $RD/rust_batch_$(basename $d).out 2>&1
  echo "$(basename $d) PINNED batch rc=$? $(tail -n 1 $RD/rust_batch_$(basename $d).out | cut -c1-300)"
done
echo "=== $(date -u +%H:%M:%SZ) conformance vllm-v1 on ${REL:-fp8-ada-x4}"
VERITY_LEAF_CONFORMANCE_REL=${REL:-fp8-ada-x4} timeout 1800 $PY -m pytest -q backends/direct/ligero/leaf/conformance_test.py -k vllm > $RD/conf.log 2>&1
echo "rc=$?"; tail -3 $RD/conf.log
gpu_idle
echo "=== $(date -u +%H:%M:%SZ) gadget-row negatives"
REL=${REL:-fp8-ada-x4} OUT=$RD/gadget-negs.json $PY -u "$IN/20-gadget-negs.py" > $RD/gadget-negs.log 2>&1
echo "rc=$?"; tail -2 $RD/gadget-negs.log | cut -c1-300
[ -n "${CONFIGS:-}" ] && bash "$IN/30-screen.sh"
exit 0
