#!/usr/bin/env bash
# flock-bench-80gb: where Flock-CUDA's time goes. nsys (CUDA trace) of one warm-up + one steady prove for
# BLAKE3 (gpu_roundtrip vs19 = m33, vs18 = m32) and the census unit (gpu_unit nbl19 = m32, host witness).
# Kernel / memcpy totals cover BOTH proves (warm-up + steady); the per-prove GPU-busy floor is about half.
# env: NETPIPE=hopper_bf16  B3_NBLS="18 19"  UNIT_NBLS="19"
set -x
C13=/usr/local/cuda-13.3
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
export LD_LIBRARY_PATH=$C13/lib64:${LD_LIBRARY_PATH:-}
[ "$DRV" -lt 580 ] && export LD_LIBRARY_PATH=$C13/compat:$LD_LIBRARY_PATH
NSYS=$(ls /opt/nvidia/nsight-systems/*/bin/nsys $C13/nsight-systems-*/bin/nsys $C13/bin/nsys 2>/dev/null | head -1)
[ -x "$NSYS" ] || { echo "no nsys"; exit 1; }
$NSYS --version
OUT=$RESEARCH_RUN_DIR/nsys; mkdir -p $OUT
RT=$(ls -t /workspace/flock-bench-80gb/flock/target/release/deps/gpu_roundtrip-* | grep -v '\.d$' | head -1)
UT=$(ls -t /workspace/flock-bench/flock/target/release/deps/gpu_unit-* 2>/dev/null | grep -v '\.d$' | head -1)
NET=$(ls -t /workspace/flock-bench/out/gpuunit-*/net-${NETPIPE:-hopper_bf16}.txt 2>/dev/null | head -1)
prof() {  # tag bin test [env]
  local tag=$1 bin=$2 t=$3; shift 3
  ( cd $(dirname $bin)/../../../crates/flock-cuda-ffi && env "$@" $NSYS profile -t cuda,nvtx -o $OUT/$tag --force-overwrite true \
      $bin --ignored --nocapture --exact $t > $OUT/$tag.log 2>&1 )
  echo "rc=$? $tag"; grep -E "GPU proof verified|FFI: host" $OUT/$tag.log
  $NSYS stats -q -r cuda_gpu_kern_sum,cuda_gpu_mem_time_sum,cuda_api_sum -f csv -o $OUT/$tag $OUT/$tag.nsys-rep > /dev/null 2>&1
  python3 - $OUT/$tag <<'EOF'
import csv, glob, sys
base = sys.argv[1]
def tot(pat, col="Total Time (ns)"):
    fs = glob.glob(base + pat)
    if not fs: return None, []
    rows = list(csv.DictReader(open(fs[0])))
    return sum(float(r[col]) for r in rows) / 1e9, rows
k, kr = tot("_cuda_gpu_kern_sum.csv")
m, mr = tot("_cuda_gpu_mem_time_sum.csv")
print(f"NSYS {base.split('/')[-1]}: kernels {k:.4f} s total ({len(kr)} kernels), memops {m:.4f} s total (both proves)")
for r in sorted(kr, key=lambda r: -float(r["Total Time (ns)"]))[:8]:
    print(f"   {float(r['Total Time (ns)'])/1e6:9.2f} ms  x{r['Instances']:>6}  {r['Name'][:90]}")
for r in mr:
    print(f"   mem {float(r['Total Time (ns)'])/1e6:9.2f} ms  x{r['Count']:>6}  {r['Operation']}")
EOF
}
for n in ${B3_NBLS:-18 19}; do prof b3-nbl$n $RT gpu_roundtrip_vs$n; done
if [ -x "$UT" ] && [ -f "$NET" ]; then
  for n in ${UNIT_NBLS:-19}; do prof unit-${NETPIPE:-hopper_bf16}-nbl$n $UT gpu_unit_nbl$n VU_NETLIST=$NET VU_NAME=${NETPIPE:-hopper_bf16}; done
fi
rm -f $OUT/*.sqlite
