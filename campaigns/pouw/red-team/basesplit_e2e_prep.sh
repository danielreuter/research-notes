#!/usr/bin/env bash
# The base-split end-to-end replay, CPU stage (no GPU lease): build the driver's five variants and form both families'
# operands on the exact reference (tree bfd950d8), into $W, which the GPU fill chunks (basesplit_e2e_fill.sh) read.
#   research run --on vy-nebius-2 ... --send basesplit_e2e_{prep.sh,rows.py,sm120.cu,check.py} -- bash inputs/basesplit_e2e_prep.sh
set -euo pipefail
cd "${RESEARCH_RUN_DIR:-$PWD}"
W=/workspace/pouw/fill-out/assessor-basesplit-e2e
T=/workspace/research/src/bfd950d81d3b78fdcd680adb1dd881910e8340f4
C=/workspace/pouw/harness/build/cutlass-v4.8.0
NVCC=/usr/local/cuda/bin/nvcc
mkdir -p $W/bin $W/src $W/ops
cp inputs/basesplit_e2e_rows.py inputs/basesplit_e2e_sm120.cu inputs/basesplit_e2e_check.py $W/src/
sha256sum $W/src/* > $W/src/SHA256SUMS
FL="-O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -I$C/include -I$C/tools/util/include -I$C/examples/common --expt-relaxed-constexpr -DNDEBUG -diag-suppress 20012"
$NVCC --version | tail -1 > nvcc.txt
for v in "dense128 -DVARIANT_DENSE128" "dense256 -DVARIANT_DENSE256" "sparse -DVARIANT_SPARSE" \
         "dense128_bf16 -DVARIANT_DENSE128 -DOUT_BF16" "sparse_bf16 -DVARIANT_SPARSE -DOUT_BF16"; do
  set -- $v; name=$1; shift
  ( $NVCC $FL "$@" -o $W/bin/$name $W/src/basesplit_e2e_sm120.cu > build-$name.log 2>&1 \
      && echo "built $name" >> build-status.txt || echo "FAILED $name" >> build-status.txt ) &
done
export PYTHONPATH=$T/packages/verity/src:$T/protocols/pouw
cd /workspace/research/src/$RESEARCH_SOURCE_SHA
for fam in gauss flat; do
  uv run --no-dev python $W/src/basesplit_e2e_rows.py --family $fam --rows 256 --out $W/ops > $RESEARCH_RUN_DIR/rows-$fam.json 2> $RESEARCH_RUN_DIR/rows-$fam.err &
done
wait
cd "$RESEARCH_RUN_DIR"
for b in $W/bin/*; do /usr/local/cuda/bin/cuobjdump -sass $b | grep -oE "OMMA[A-Z0-9._]*" | sort | uniq -c > sass-$(basename $b).txt; done
for fam in gauss flat; do cp $W/ops/$fam/reference.json reference-$fam.json 2>/dev/null || true; done
ls -la $W/bin $W/ops/* > manifest.txt
cat build-status.txt
grep -h -m3 "error" build-*.log || true
! grep -q FAILED build-status.txt
