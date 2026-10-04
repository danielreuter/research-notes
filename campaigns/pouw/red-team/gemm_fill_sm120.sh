#!/usr/bin/env bash
# Writer: bc-cb8013f7 (by its own report), an agent the sm_120 PoUW coordinator (bc-2aa33ad8) started by mistake, not the assessor. The assessor (bc-d7d4b0d1) reviewed and adopted it (run r20260930-085618-5cfa), 30 Sep 2026.
# Red-team fill job (bc-d7d4b0d1) on node 2: one group of `simt_gemm_sm120` tasks, restartable and chunked.
#   gemm_fill_sm120.sh <group>        groups: ffma, lowp-ffma, packed, dp4a, strassen
# Each (task, shape) writes out/<group>/<task>@<m>x<n>x<k>.json once, atomically; a restart skips what exists. After a chunk
# (CHUNK_TASKS tasks or CHUNK_MIN minutes) it exits 99 if tasks remain, 0 when the group is done. A task that fails writes
# its error in place of a result, so a bad task can't loop the job. Every group also times cuBLASLt BF16, E4M3 and NVFP4 at
# 8,192^3 on the same die, as controls for its ratios. Screening only: nothing here is a panel number.
set -uo pipefail
GROUP=${1:?group}
ROOT=/workspace/pouw/red-team/gemm-fill
BIN=$ROOT/bin/simt_gemm_sm120
SRC=$ROOT/src/simt_gemm_sm120.cu
OUT=$ROOT/out/$GROUP
CHUNK_TASKS=${CHUNK_TASKS:-8}
CHUNK_MIN=${CHUNK_MIN:-12}
TARGET_MS=${TARGET_MS:-4000}
SEED=20261007
mkdir -p "$OUT"
UUID=${GPU_LEASE_UUID:?run under gpu-lease (the fill runner does)}
echo "group=$GROUP uuid=$UUID cvd=${CUDA_VISIBLE_DEVICES:-?} job=${FILL_JOB:-?} start=$(date -u +%FT%TZ)"

if [ ! -x "$BIN" ]; then
  /usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -Xptxas -v "$SRC" -o "$BIN" \
    -lcublas -lcublasLt 2> "$ROOT/bin/ptxas.log" || { echo "build failed" >&2; exit 2; }
fi
if [ ! -s "$OUT/build.json" ]; then
  # SASS gate: every CUDA-core kernel must be free of tensor-core instructions; record what its mainloop issues.
  /usr/local/cuda/bin/cuobjdump -sass "$BIN" > "$OUT/sass.txt"
  python3 - "$OUT/sass.txt" "$OUT/build.json" "$SRC" "$BIN" <<'PY' || { echo "SASS gate failed" >&2; exit 3; }
import hashlib, json, re, sys
sass, out, src, binp = sys.argv[1:5]
kern, counts = None, {}
for line in open(sass):
    m = re.search(r"Function : (\S+)", line)
    if m:
        kern = m.group(1); counts[kern] = {}
        continue
    m = re.search(r"/\*[0-9a-f]{4,}\*/\s+(?:@!?U?P\w+\s+)?([A-Z][A-Z0-9_]*)(\.[A-Z0-9_.]+)?", line)
    if kern and m:
        op = m.group(1)
        counts[kern][op] = counts[kern].get(op, 0) + 1
tc = ("HMMA", "IMMA", "QMMA", "OMMA", "HGMMA", "UTCMMA", "BMMA", "DMMA")
bad = {k: [o for o in c if o.startswith(tc)] for k, c in counts.items() if "simt_gemm" in k}
bad = {k: v for k, v in bad.items() if v}
keep = ("FFMA", "HFMA2", "IDP", "IDP4A", "FADD", "FMUL", "I2F", "F2F", "PRMT", "LDS", "STS", "LDG", "IMAD", "HADD2")
summary = {k: {o: n for o, n in c.items() if o in keep} for k, c in counts.items() if "simt_gemm" in k}
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
json.dump({"src_sha256": h(src), "bin_sha256": h(binp), "tensor_core_ops_in_simt_kernels": bad, "sass_counts": summary},
          open(out, "w"), indent=1)
sys.exit(1 if bad else 0)
PY
fi

S8=8192x8192x8192; S16=16384x16384x16384; D8=32x8192x8192
CONTROLS="lt_bf16@$S8 lt_e4m3@$S8 lt_nvfp4@$S8"
case "$GROUP" in
  ffma) TASKS="cublas_sgemm_pedantic@$S8 f32_ffma:128x128x8:8x8@$S8 f32_ffma:128x128x16:8x8@$S8 f32_ffma:256x128x8:16x8@$S8
               f32_ffma:64x64x16:4x4@$S8 f32_ffma:32x128x16:4x4@$S8 bf16_ffma:128x128x8:8x8@$S8 bf16_ffma:128x128x16:8x8@$S8
               bf16_ffma:256x128x8:16x8@$S8 cublas_sgemm_pedantic@$S16 f32_ffma:128x128x16:8x8@$S16 bf16_ffma:128x128x16:8x8@$S16
               f32_ffma:32x128x16:4x4@$D8" ;;
  lowp-ffma) TASKS="e4m3_ffma:128x128x16:8x8@$S8 e4m3_ffma:128x128x32:8x8@$S8 e4m3_ffma:256x128x16:16x8@$S8
               e4m3_ffma:32x128x16:4x4@$S8 nvfp4_ffma:128x128x32:8x8@$S8 nvfp4_ffma:256x128x32:16x8@$S8
               e4m3_ffma:128x128x32:8x8@$S16 nvfp4_ffma:128x128x32:8x8@$S16 e4m3_ffma:32x128x16:4x4@$D8" ;;
  packed) TASKS="e4m3_hfma2:128x128x8:8x8:p64@$S8 e4m3_hfma2:128x128x16:8x8:p64@$S8 e4m3_hfma2:128x128x8:8x8:p0@$S8
               bf16_hfma2:128x128x8:8x8:p16@$S8 bf16_hfma2:128x128x16:8x8:p32@$S8 bf16_hfma2:128x128x8:8x8:p0@$S8
               e4m3_hfma2:128x128x16:8x8:p64@$S16 bf16_hfma2:128x128x16:8x8:p32@$S16" ;;
  dp4a) TASKS="i8_dp4a:128x128x8:8x8@$S8 i8_dp4a:128x128x16:8x8@$S8 i8_dp4a:256x128x8:16x8@$S8 i8_dp4a:32x128x16:4x4@$S8
               nvfp4_dp4a:128x128x8:8x8@$S8 nvfp4_dp4a:128x128x16:8x8@$S8 nvfp4_dp4a:32x128x16:4x4@$S8
               i8_dp4a:128x128x16:8x8@$S16 nvfp4_dp4a:128x128x16:8x8@$S16 i8_dp4a:32x128x16:4x4@$D8
               nvfp4_dp4a:32x128x16:4x4@$D8" ;;
  strassen) TASKS="strassen1_e4m3_f16@$S8 lt_f16_f32@$S8 lt_f16_f32@4096x4096x4096 lt_f16_f32@2048x2048x2048
               lt_e4m3_f32@$S8 lt_e4m3_f32@4096x4096x4096 lt_e4m3_f32@2048x2048x2048 lt_nvfp4@$S16 lt_e4m3@$S16
               strassen1_e4m3_f16@$S16 lt_f16_f32@$S16 lt_e4m3_f32@$S16" ;;
  *) echo "unknown group $GROUP" >&2; exit 2 ;;
esac
TASKS="$CONTROLS $TASKS"

t0=$(date +%s); ran=0; left=0
for tk in $TASKS; do
  task=${tk%@*}; shape=${tk#*@}
  f="$OUT/$(echo "$task" | tr ':' '_')@$shape.json"
  [ -s "$f" ] && continue
  if [ "$ran" -ge "$CHUNK_TASKS" ] || [ $(( $(date +%s) - t0 )) -ge $(( CHUNK_MIN * 60 )) ]; then left=1; break; fi
  IFS=x read -r m n k <<< "$shape"
  nvidia-smi --id="$UUID" --query-gpu=timestamp,clocks.sm,power.draw,temperature.gpu,clocks_event_reasons.active \
    --format=csv,noheader -lms 500 > "$f.clocks" 2>/dev/null &
  SMI=$!
  "$BIN" "$task" "$m" "$n" "$k" "$TARGET_MS" "$SEED" > "$f.tmp" 2> "$f.err"; rc=$?
  kill "$SMI" 2>/dev/null; wait "$SMI" 2>/dev/null
  python3 - "$f" "$rc" "$UUID" "${FILL_JOB:-}" <<'PY'
import json, os, statistics, sys
f, rc, uuid, job = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
clk = []
for line in open(f + ".clocks", errors="replace"):
    p = [x.strip() for x in line.split(",")]
    try: clk.append((float(p[1].split()[0]), float(p[2].split()[0]), p[4]))
    except Exception: pass
try:
    r = json.loads(open(f + ".tmp").read().strip().splitlines()[-1]) if rc == 0 else None
except Exception:
    r = None
if r is None:
    r = {"error": f"rc={rc}", "stderr": open(f + ".err", errors="replace").read()[-2000:]}
r.update({"uuid": uuid, "fill_job": job, "clock": {
    "sm_mhz_median": statistics.median(c[0] for c in clk) if clk else None,
    "power_w_median": statistics.median(c[1] for c in clk) if clk else None,
    "throttle_reasons": sorted({c[2] for c in clk}), "samples": len(clk)}})
json.dump(r, open(f + ".part", "w"))
os.replace(f + ".part", f)
for x in (".tmp", ".clocks"):
    try: os.remove(f + x)
    except FileNotFoundError: pass
PY
  echo "$(date -u +%FT%TZ) $task@$shape rc=$rc $(head -c 300 "$f")"
  ran=$((ran + 1))
done
if [ "$left" -eq 1 ]; then echo "chunk done, more remain"; exit 99; fi
echo "group $GROUP done $(date -u +%FT%TZ)"; exit 0
