#!/usr/bin/env bash
# b-ligero-vllm-v1: after WAIT_RUN ends, rebuild ligero-verify with the new PINS (sources touched), cargo test, the PINNED
# batch verify of WAIT_RUN's plateau dump (producer check), and the gadget-row negatives on REL.
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
for _ in $(seq 360); do grep -q '"state": "\(done\|failed\|killed\)"' /workspace/research/runs/$WAIT_RUN/status.json 2>/dev/null && break; sleep 10; done
export PATH="$HOME/.cargo/bin:$PATH" CARGO_TARGET_DIR=/workspace/cargo-target
( cd backends/ligero-verify && touch src/*.rs && cargo build --release 2>&1 | tail -1 && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ && sha256sum /workspace/bin/ligero-verify
  cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked" | head -6 )
for sd in /workspace/research/runs/$WAIT_RUN/*/sweep.json; do
  pl=$($PY -c "import json;d=json.load(open('$sd'));print([p['dir'] for p in d['points'] if p['point']==d['plateau_point']][0])")
  P=$(dirname $sd)/$pl/proofs; echo "plateau $P"
  $V system-digest --system $P/system.bin | head -c 300; echo
  $V batch --system $P/system.bin --dir $P/rep1 --jobs $NT --threads 1 --target-bits 128 --json $RD/rust_batch_plateau.json > $RD/rust_batch_plateau.out 2>&1
  echo "PINNED plateau batch rc=$? $(tail -n 1 $RD/rust_batch_plateau.out | cut -c1-400)"
done
gpu_idle
REL=${REL:?} OUT=$RD/gadget-negs.json $PY -u "$IN/20-gadget-negs.py" > $RD/gadget-negs.log 2>&1; echo "gadget negs rc=$?"; tail -1 $RD/gadget-negs.log | cut -c1-300
