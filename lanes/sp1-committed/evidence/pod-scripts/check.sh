#!/usr/bin/env bash
# sp1-committed pod check: common-crate tests, fp8-ada set regenerated (sha256 against art:4a6f7602 fp8-ada.bin),
# committed executor honest + negatives on [0,64) and a full-range execute (cycles).  Run from the source root.
set -euo pipefail
OUT=/workspace/sp1-committed
HOST=/workspace/bin/veritor-zk-host-cuda-relation-committed
WANT=531a5c019099850ad89b9d40f9eee3ebe636bbcb7c0f06180dccceb34d709ae6
VENV=$OUT/venv
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.sp1/bin:$PATH"
mkdir -p "$OUT/check"
stamp() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }

stamp "venv"
if [ ! -x "$VENV/bin/python" ]; then
  uv venv "$VENV" --python 3.12
  uv pip install --python "$VENV/bin/python" numpy torch --index-url https://download.pytorch.org/whl/cpu
fi
python() { "$VENV/bin/python" "$@"; }

stamp "cargo test veritor-zk-common"
(cd backends/sp1 && CARGO_TARGET_DIR=/workspace/sp1-target-test cargo test --release -p veritor-zk-common 2>&1 | tail -25)

stamp "fp8-ada set"
if [ ! -f "$OUT/fp8-ada.bin" ]; then
  python -m verity_sp1.format_instances --format fp8-ada --n 4096 --procs "$(nproc)" --out "$OUT/fp8-ada.bin"
fi
GOT=$(sha256sum "$OUT/fp8-ada.bin" | cut -d' ' -f1)
echo "sha256 $GOT"
[ "$GOT" = "$WANT" ] || { echo "fp8-ada.bin does not match art:4a6f7602 fp8-ada.bin"; exit 1; }
echo "matches art:4a6f7602 fp8-ada.bin"

S=(--batch "$OUT/fp8-ada.bin" --lo 0 --hi 64)
stamp "info"; "$HOST" info | tee "$OUT/check/info.json"
stamp "commit"; "$HOST" committed-commit "${S[@]}" --out "$OUT/check/statement-0-64.json"
stamp "execute honest"; "$HOST" committed-execute "${S[@]}" | tee "$OUT/check/exec-honest.json"
for j in 0 32 63; do
  stamp "execute flip-y $j"; "$HOST" committed-execute "${S[@]}" --flip-y $j | tee "$OUT/check/exec-flip-y-$j.json"
  stamp "execute tamper-x $j"; "$HOST" committed-execute "${S[@]}" --tamper-x $j | tee "$OUT/check/exec-tamper-x-$j.json"
done
for t in a b y; do
  stamp "execute wrong-root $t"; "$HOST" committed-execute "${S[@]}" --wrong-root $t | tee "$OUT/check/exec-wrong-root-$t.json"
done
stamp "execute honest full range"; "$HOST" committed-execute --batch "$OUT/fp8-ada.bin" | tee "$OUT/check/exec-honest-full.json"
stamp "done"
