#!/bin/bash
# lane enc-hopper checkpoint validation (cwd = the shipped lane tree): pytest backends/direct/ligero, bit-exactness vs
# main 6babe27 (/workspace/src-main) with seeded coins + mask keys (bf16-hopper, fp8-hopper via bitexact.py; bf16-ampere
# (vu.py) + fp4-nvf4 via bitexact_cli.py), Rust ligero-verify on the lane dumps, the six gates.
set -u
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export PYTHONPATH=packages/verity/src:backends/numerical/python:.
PY=/workspace/venv312/bin/python
HERE=$(pwd)
OUT=${RESEARCH_RUN_DIR}/bitexact
mkdir -p "$OUT"
H=$RESEARCH_RUN_DIR/inputs/bitexact.py
HC=$RESEARCH_RUN_DIR/inputs/bitexact_cli.py
echo "lane tree: $HERE"; echo "main tree: /workspace/src-main"
echo "--- tree diff (lane vs main), backends/direct/ligero:"
diff -rq /workspace/src-main/backends/direct/ligero "$HERE/backends/direct/ligero" | grep -v __pycache__
echo "--- Rust verifier identical to main?"
diff -rq /workspace/src-main/backends/ligero-verify "$HERE/backends/ligero-verify" && echo "ligero-verify: IDENTICAL"
nvidia-smi --query-gpu=name,clocks.sm,temperature.gpu --format=csv,noheader; cat /proc/loadavg

echo "=== pytest backends/direct/ligero (lane tree)"
t0=$(date +%s)
$PY -m pytest backends/direct/ligero -q -p no:cacheprovider --deselect backends/direct/ligero/v2 2>&1 | tail -8
echo "pytest rc=${PIPESTATUS[0]} wall=$(( $(date +%s) - t0 ))s"
echo "=== encode_simt_test (bit-exact vs torch, timing)"
$PY -m backends.direct.ligero.encode_simt_test --device cuda --rows 3328 --reps 5 2>&1 | grep -v Warning | tail -4

total_files=0; total_same=0
cmp_dirs () {   # tag maindir lanedir
  local tag=$1 a=$2 b=$3 n=0 same=0
  for f in $(cd "$a" && find . -type f \( -name '*.stmt' -o -name '*.proof' -o -name '*.coins' -o -name 'system.bin' \) | sort); do
    n=$((n+1))
    x=$(sha256sum "$a/$f" | cut -d' ' -f1); y=$(sha256sum "$b/$f" 2>/dev/null | cut -d' ' -f1)
    if [ "$x" = "$y" ]; then same=$((same+1)); else echo "  DIFF $f main=$x lane=$y"; fi
  done
  echo "$tag: $same / $n files identical"
  echo "$tag $same $n" >> "$OUT/summary.txt"
  total_files=$((total_files+n)); total_same=$((total_same+same))
}
run_pair () {   # tag rel vus zkflag
  local tag=$1 rel=$2 vus=$3 zk=$4 zkarg=""
  [ "$zk" = "zk" ] && zkarg="--zk"
  echo "=== $tag ($rel interactive $zk)"
  $PY "$H" --tree /workspace/src-main --rel "$rel" $zkarg --mode interactive --vus "$vus" --subs 3 --seed 20260922 --out "$OUT/$tag/main" 2>&1 | grep -v Warning | tail -4
  $PY "$H" --tree "$HERE" --rel "$rel" $zkarg --mode interactive --vus "$vus" --subs 3 --seed 20260922 --out "$OUT/$tag/lane" 2>&1 | grep -v Warning | tail -4
  cmp_dirs "$tag" "$OUT/$tag/main" "$OUT/$tag/lane"
}
run_cli () {    # tag  -- run.py argv (without --dump-dir)
  local tag=$1; shift
  echo "=== $tag (cli: $*)"
  $PY "$HC" --tree /workspace/src-main --seed 20260922 -- "$@" --dump-dir "$OUT/$tag/main" --dump-reps 1 2>&1 | grep -v Warning | tail -4
  $PY "$HC" --tree "$HERE" --seed 20260922 -- "$@" --dump-dir "$OUT/$tag/lane" --dump-reps 1 2>&1 | grep -v Warning | tail -4
  cmp_dirs "$tag" "$OUT/$tag/main" "$OUT/$tag/lane"
}
run_pair bf16h-int-zk    bf16-hopper 170 zk
run_pair bf16h-int-nonzk bf16-hopper 170 nozk
run_pair fp8h-int-zk     fp8-hopper  341 zk
run_pair fp8h-int-nonzk  fp8-hopper  341 nozk
run_cli  bf16a-int-zk    bench-vu --zk --mode interactive --root /workspace/bench-instances/v1 --batch 16384 --total-vus 340 --reps 1 --device cuda --target -128
run_cli  bf16a-int-nonzk bench-vu --mode interactive --root /workspace/bench-instances/v1 --batch 16384 --total-vus 340 --reps 1 --device cuda --target -128
run_cli  fp4-int-zk      --relation fp4-nvf4 bench-vu --zk --mode interactive --batch 4096 --total-vus 170 --reps 1 --device cuda --target -128 --instances-cache /workspace/instances-cache
run_cli  fp4-int-nonzk   --relation fp4-nvf4 bench-vu --mode interactive --batch 4096 --total-vus 170 --reps 1 --device cuda --target -128 --instances-cache /workspace/instances-cache
echo "TOTAL: $total_same / $total_files files identical"
echo "TOTAL $total_same $total_files" >> "$OUT/summary.txt"

echo "=== Rust ligero-verify on the lane dumps (batch --target-bits 128)"
LV=/workspace/bin/ligero-verify
for tag in bf16h-int-zk bf16h-int-nonzk fp8h-int-zk fp8h-int-nonzk; do
  d="$OUT/$tag/lane"
  $LV batch --system "$d/system.bin" --dir "$d" --jobs 3 --threads 1 --target-bits 128 --json "$d/rust.json" 2>&1 | tail -1
done
for tag in bf16a-int-zk bf16a-int-nonzk fp4-int-zk fp4-int-nonzk; do
  d="$OUT/$tag/lane"; sd=$(ls "$d"/system.bin "$d"/proofs/system.bin 2>/dev/null | head -1); dd=$(dirname "$sd")
  rd=$(ls -d "$dd"/rep1 2>/dev/null || echo "$dd")
  echo "-- $tag: $sd / $rd"
  $LV batch --system "$sd" --dir "$rd" --jobs 3 --threads 1 --target-bits 128 --json "$d/rust.json" 2>&1 | tail -1
done
find "$OUT" -name '*.proof' -delete
echo "BITEXACT_DONE"

gate () {
  local name=$1; shift
  echo "=== gate $name: $*"
  t0=$(date +%s)
  $PY -m backends.direct.ligero.run "$@" 2>&1 | grep -v Warning | tail -4
  echo "gate $name rc=${PIPESTATUS[0]} wall=$(( $(date +%s) - t0 ))s"
}
gate bf16-ampere gate-vu --root /workspace/bench-instances/v1 --vus 64 --device cuda
gate bf16-hopper --relation bf16-hopper gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate bf16-hopper-zk --relation bf16-hopper gate-vu --vus 64 --device cuda --zk --instances-cache /workspace/instances-cache
gate fp8-hopper --relation fp8-hopper gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate fp8-ada --relation fp8-ada gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate fp4-nvf4 --relation fp4-nvf4 gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
echo GATES_DONE
