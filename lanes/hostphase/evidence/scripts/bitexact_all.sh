#!/bin/bash
# lane hostphase: bit-exactness of lane/hostphase (cwd = the shipped tree) against main 5a8a744 (/workspace/src-main).
# Same seeds, same coins, same mask keys (bitexact.py's deterministic os.urandom); sha256sum every .stmt/.proof/.coins.
set -u
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
PY=/workspace/venv312/bin/python
HERE=$(pwd)
OUT=${RESEARCH_RUN_DIR}/bitexact
mkdir -p "$OUT"
H=$RESEARCH_RUN_DIR/inputs/bitexact.py
echo "lane tree: $HERE"; echo "main tree: /workspace/src-main"
echo "--- tree diff (lane vs main), backends/direct/ligero:"
diff -rq /workspace/src-main/backends/direct/ligero "$HERE/backends/direct/ligero" | grep -v __pycache__
echo "--- Rust verifier identical to main?"
diff -rq /workspace/src-main/backends/ligero-verify "$HERE/backends/ligero-verify" && echo "ligero-verify: IDENTICAL"

echo "=== fused witness / hints graph tests (lane tree)"
cd "$HERE" && PYTHONPATH=packages/verity/src:backends/numerical/python:. $PY -m pytest backends/direct/ligero/witness_device_test.py -x -q -p no:cacheprovider 2>&1 | tail -5
rc=${PIPESTATUS[0]}
if [ "$rc" != "0" ]; then echo "FUSED WITNESS TEST FAILED rc=$rc"; fi

total_files=0; total_same=0
run_pair () {   # tag rel vus zkflag mode [impl]
  local tag=$1 rel=$2 vus=$3 zk=$4 mode=$5 impl=${6:-device}
  local zkarg=""; [ "$zk" = "zk" ] && zkarg="--zk"
  echo "=== $tag ($rel $mode $zk impl=$impl)"
  $PY "$H" --tree /workspace/src-main --rel "$rel" $zkarg --mode "$mode" --vus "$vus" --subs 3 --seed 20260922 --out "$OUT/$tag/main" 2>&1 | grep -v Warning | tail -6
  $PY "$H" --tree "$HERE" --rel "$rel" $zkarg --mode "$mode" --vus "$vus" --subs 3 --seed 20260922 --impl "$impl" --out "$OUT/$tag/lane" 2>&1 | grep -v Warning | tail -6
  local n=0 same=0
  for f in "$OUT/$tag/main"/*.stmt "$OUT/$tag/main"/*.proof "$OUT/$tag/main"/*.coins "$OUT/$tag/main"/system.bin; do
    [ -e "$f" ] || continue
    n=$((n+1))
    b=$(basename "$f")
    a=$(sha256sum "$f" | cut -d' ' -f1); c=$(sha256sum "$OUT/$tag/lane/$b" 2>/dev/null | cut -d' ' -f1)
    if [ "$a" = "$c" ]; then same=$((same+1)); else echo "  DIFF $b main=$a lane=$c"; fi
  done
  echo "$tag: $same / $n files identical"
  echo "$tag $rel $mode $zk $impl $same $n" >> "$OUT/summary.txt"
  total_files=$((total_files+n)); total_same=$((total_same+same))
}
run_pair bf16h-int-nonzk bf16-hopper 170 nozk interactive
run_pair bf16h-fs-zk     bf16-hopper 170 zk   fiat-shamir
run_pair bf16h-int-zk    bf16-hopper 170 zk   interactive
run_pair bf16h-int-zk-legacy bf16-hopper 170 zk interactive legacy
run_pair fp8h-int-nonzk  fp8-hopper  341 nozk interactive
run_pair fp8h-fs-zk      fp8-hopper  341 zk   fiat-shamir
run_pair fp8h-int-zk     fp8-hopper  341 zk   interactive
echo "TOTAL: $total_same / $total_files files identical"
echo "TOTAL $total_same $total_files" >> "$OUT/summary.txt"
echo "=== Rust ligero-verify on the lane dumps (system digest + batch, interactive: --coins)"
LV=$(ls /workspace/bin/ligero-verify 2>/dev/null || ls /workspace/cargo-target/release/ligero-verify 2>/dev/null | head -1)
echo "ligero-verify: $LV"
for tag in bf16h-int-nonzk bf16h-fs-zk bf16h-int-zk fp8h-int-nonzk fp8h-fs-zk fp8h-int-zk; do
  d="$OUT/$tag/lane"
  echo "-- $tag: $($LV system-digest --system "$d/system.bin" 2>&1 | tail -1)"
  $LV batch --system "$d/system.bin" --dir "$d" --jobs 3 --threads 1 --target-bits 128 --json "$d/rust.json" 2>&1 | tail -2
done
# clean the scratch proof bytes (keep digests + json): the run-files should stay small
find "$OUT" -name '*.proof' -delete
echo "BITEXACT_DONE"
