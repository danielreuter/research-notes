#!/usr/bin/env bash
# flock-glue: GPU kernel time per batch (nsys CUDA trace of glue_bench). A batch starts at each unit_witness_chain
# launch (the first 3 are the standalone VWIT timing pair and the warm-up); per batch: union of kernel intervals
# ("kernel"), union of kernel + memcpy/memset intervals ("gpu_busy"), first-to-last GPU op ("span"); medians.
# env: PIPES NVUS VARIANTS="devgpu devovl" REPS=3 PROFILE=fast FREPS=1
set -uxo pipefail
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
W=/workspace/flock-glue; F=$W/flock
export LD_LIBRARY_PATH=/usr/local/cuda-13.3/lib64:${LD_LIBRARY_PATH:-}
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
[ "$DRV" -lt 580 ] && export LD_LIBRARY_PATH=/usr/local/cuda-13.3/compat:$LD_LIBRARY_PATH
Q=$(awk '{ if ($1 != "max") printf "%d", $1 / $2; else print 16 }' /sys/fs/cgroup/cpu.max 2>/dev/null || echo 16)
export RAYON_NUM_THREADS=${RAYON_NUM_THREADS:-$Q}
NSYS=$(command -v nsys || ls /usr/local/cuda-13.3/bin/nsys 2>/dev/null | head -1)
$NSYS --version
OUT=${RESEARCH_RUN_DIR:-$W/out}/nsys; mkdir -p $OUT
BIN0=$(ls -t $F/target/release/deps/gpu_glue-* | grep -v '\.d$' | head -1)
mkdir -p $W/bins && BIN=$W/bins/gpu_glue-nsys-$(date -u +%H%M%S)-$$ && cp $BIN0 $BIN && sha256sum $BIN | tee $OUT/bin.sha256
cd $F/crates/flock-cuda-ffi
nbl() {  # pipe nvu kind(b3|unit)
  case $1 in *bf16) c=$(( $2 * 96 ));; *) c=$(( $2 * 48 ));; esac
  n=0; while [ $(( 1 << n )) -lt $c ]; do n=$((n + 1)); done
  [ $3 = unit ] && [ $((13 + n)) = 29 ] && n=17; echo $n
}
for pipe in ${PIPES:-ampere_bf16}; do
  for nvu in ${NVUS:-4096}; do
    for v in ${VARIANTS:-devgpu devovl}; do
      case $v in devgpu) mode=2;; devovl) mode=3;; devwit) mode=2;; esac
      grind=1; [ $v = devwit ] && grind=0
      tag=$pipe-$nvu-$v-${PROFILE:-fast}x${FREPS:-1}${TAGX:-}
      env FLOCK_GLUE_GPU_GRIND=$grind GLUE_PROFILE=${PROFILE:-fast} GLUE_FLOCK_REPS=${FREPS:-1} \
        VU_NETLIST=$W/net/net-$pipe.txt VU_NAME=$pipe VU_NVU=$nvu GLUE_MODE=$mode GLUE_REPS=${REPS:-3} \
        GLUE_B3_NBL=$(nbl $pipe $nvu b3) GLUE_UNIT_NBL=$(nbl $pipe $nvu unit) \
        $NSYS profile -t cuda -o $OUT/$tag --force-overwrite true $BIN --ignored --nocapture --exact glue_bench > $OUT/$tag.log 2>&1
      echo "rc=$? $tag"; grep -E "VSUMMARY|REJECTED|panicked" $OUT/$tag.log
      rm -f $OUT/$tag*.csv $OUT/$tag.sqlite
      $NSYS stats -q --force-overwrite true -r cuda_gpu_trace -f csv -o $OUT/$tag $OUT/$tag.nsys-rep > /dev/null 2>&1
      python3 - $OUT/$tag <<'PY' | tee -a $OUT/summary.txt
import csv, glob, statistics, sys
base = sys.argv[1]
fs = glob.glob(base + "*cuda_gpu_trace*.csv")
rows = list(csv.DictReader(open(fs[0])))
ops = []
for r in rows:
    s = float(r["Start (ns)"]); d = float(r["Duration (ns)"]); n = r["Name"]
    ops.append((s, s + d, n))
ops.sort()
wl = [s for s, e, n in ops if n.startswith("unit_witness_chain")]
starts = wl[3:]
def union(iv):
    tot, cur_s, cur_e = 0.0, None, None
    for s, e in sorted(iv):
        if cur_e is None or s > cur_e:
            if cur_e is not None: tot += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None: tot += cur_e - cur_s
    return tot
res = []
for i, b0 in enumerate(starts):
    b1 = starts[i + 1] if i + 1 < len(starts) else float("inf")
    win = [(s, e, n) for s, e, n in ops if b0 <= s < b1]
    kern = [(s, e) for s, e, n in win if not n.startswith("[CUDA")]
    allv = [(s, e) for s, e, n in win]
    wit = sum(e - s for s, e, n in win if n.startswith("unit_witness_chain") or n.startswith("unit_lincheck_transpose"))
    d2d = sum(e - s for s, e, n in win if "Device-to-Device" in n)
    res.append((union(kern) / 1e9, union(allv) / 1e9, (max(e for s, e in allv) - min(s for s, e in allv)) / 1e9, wit / 1e9, d2d / 1e9))
tag = base.split("/")[-1]
if not res:
    print(f"NSYSB {tag}: no batches found"); sys.exit()
med = lambda k: statistics.median(r[k] for r in res)
print(f"NSYSB {tag}: batches={len(res)} kernel_median={med(0):.4f} gpu_busy_median={med(1):.4f} span_median={med(2):.4f} "
      f"unit_witness_kernels={med(3):.4f} d2d={med(4):.4f}  (per batch: {' '.join(f'{r[0]:.4f}' for r in res)})")
# idle GPU gaps in the last batch (host orchestration): total and the largest, with the ops on either side
b0 = starts[-1]
win = [(s, e, n) for s, e, n in ops if s >= b0]
gaps, reach = [], None
for i, (s, e, n) in enumerate(win):
    if reach is not None and s > reach[0]:
        gaps.append((s - reach[0], reach[1], n))
    if reach is None or e > reach[0]:
        reach = (e, n)
tot = sum(g for g, _, _ in gaps)
hist = {}
for g, _, _ in gaps:
    k = "<10us" if g < 1e4 else "10-50us" if g < 5e4 else "50-200us" if g < 2e5 else "200us-1ms" if g < 1e6 else ">1ms"
    hist[k] = hist.get(k, (0, 0.0)); hist[k] = (hist[k][0] + 1, hist[k][1] + g)
print(f"NSYSGAP {tag}: {len(gaps)} idle gaps, {tot / 1e6:.2f} ms; " + " ".join(f"{k}: n={v[0]} {v[1] / 1e6:.2f}ms" for k, v in hist.items()))
for g, a, b in sorted(gaps, reverse=True)[:10]:
    print(f"   gap {g / 1e3:8.1f} us  after {a[:60]}  before {b[:60]}")
PY
      rm -f $OUT/$tag.sqlite
    done
  done
done
