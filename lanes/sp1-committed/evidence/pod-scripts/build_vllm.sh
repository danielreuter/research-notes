#!/usr/bin/env bash
# sp1-committed: build + install the relation-committed-vllm host (pod_bootstrap.sh), rebuild the frame-v3 committed host at
# this tip (not installed) and require its guest identity to be the pinned one, run the committed unit tests, and the vllm
# host's executor honest + negatives on [0,64) and a full-range execute.  Run from the source root.
set -euo pipefail
OUT=/workspace/sp1-committed
PIN_ELF=f4fc749f33904bc88af9e492f61d0741b7234193f985492c67fcdf2bb5e88624
PIN_VK=0x009893321b66abfb52751a49dc9f1ea774c491f142910b64f206841da19f3a66
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.sp1/bin:$PATH"
stamp() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
mkdir -p "$OUT/check-vllm"

SP1_HOST_FEATURES=cuda,relation-committed-vllm bash backends/sp1/pod_bootstrap.sh
# the same-pod baseline: the bare guest (relation only, operands unbound) on the same set
SP1_HOST_FEATURES=cuda,relation-bare bash backends/sp1/pod_bootstrap.sh

stamp "frame-v3 committed guest at this tip"
(cd backends/sp1 && CARGO_TARGET_DIR=/workspace/sp1-target-cuda-relation-committed cargo build --release -p veritor-zk-host --features cuda,relation-committed 2>&1 | tail -2)
/workspace/sp1-target-cuda-relation-committed/release/veritor-zk-host info | tee "$OUT/check-vllm/frame-v3-info.json"
grep -q "\"elf_sha256\":\"$PIN_ELF\"" "$OUT/check-vllm/frame-v3-info.json" && grep -q "\"vk_hash\":\"$PIN_VK\"" "$OUT/check-vllm/frame-v3-info.json" \
  || { echo "the frame-v3 committed guest changed at this tip"; exit 1; }
echo "frame-v3 committed identity unchanged: elf $PIN_ELF vk $PIN_VK"

stamp "cargo test committed"
(cd backends/sp1 && CARGO_TARGET_DIR=/workspace/sp1-target-test cargo test --release -p veritor-zk-common --lib committed 2>&1 | grep -E "^test |test result|error|panicked")

HOST=/workspace/bin/veritor-zk-host-cuda-relation-committed-vllm
S=(--batch "$OUT/fp8-ada.bin" --lo 0 --hi 64)
stamp "info"; "$HOST" info | tee "$OUT/check-vllm/info.json"
stamp "execute honest"; "$HOST" committed-execute "${S[@]}" | tee "$OUT/check-vllm/exec-honest.json"
for j in 0 32 63; do
  stamp "execute flip-y $j"; "$HOST" committed-execute "${S[@]}" --flip-y $j | tee "$OUT/check-vllm/exec-flip-y-$j.json"
  stamp "execute tamper-x $j"; "$HOST" committed-execute "${S[@]}" --tamper-x $j | tee "$OUT/check-vllm/exec-tamper-x-$j.json"
done
for t in a b y; do
  stamp "execute wrong-root $t"; "$HOST" committed-execute "${S[@]}" --wrong-root $t | tee "$OUT/check-vllm/exec-wrong-root-$t.json"
done
stamp "execute honest full range"; "$HOST" committed-execute --batch "$OUT/fp8-ada.bin" | tee "$OUT/check-vllm/exec-honest-full.json"
stamp "done"
