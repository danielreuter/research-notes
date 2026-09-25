#!/usr/bin/env bash
# flock-bench-80gb: Flock-CUDA (succinctlabs/flock cuda-ghash + flock-cuda-ffi, BLAKE3-only full on-device prover)
# rebuilt for sm_$SM (build.rs hard-codes sm_120), run through CUDA 13.3 forward-compat (driver 570 on these pods).
# Same patch as lanes/flock-bench/evidence/pod-scripts/20-gpu-build.sh (proof size print + verity batch sizes).
# nbl = log2(BLAKE3 compressions): 12/13 (FP8/BF16 N=64), 16/17 (N=1024), 18/19 (N=4096).
# env: SM=90  CUDA_NBLS="12 13 16 17 18 19"  CUDA_REPS=3
set -uxo pipefail
W=/workspace/flock-bench-80gb; OUT=$W/out/gpu-${TAG:-x}-$(date -u +%H%MZ); mkdir -p $OUT
source $HOME/.cargo/env
SM=${SM:-90}
export PATH=/usr/local/cuda-13.3/bin:$PATH NVCC=/usr/local/cuda-13.3/bin/nvcc
export LD_LIBRARY_PATH=/usr/local/cuda-13.3/compat:/usr/local/cuda-13.3/lib64:${LD_LIBRARY_PATH:-}
ls -la /usr/local/cuda
cd $W/flock
git checkout -q crates/flock-cuda-ffi
sed -i "s/arch=compute_120,code=sm_120/arch=compute_$SM,code=sm_$SM/; s#/usr/local/cuda/lib64#/usr/local/cuda-13.3/lib64#g" crates/flock-cuda-ffi/build.rs
grep -n "gencode\|lib64" -A1 crates/flock-cuda-ffi/build.rs | head
python3 - <<'EOF'
import pathlib
p = pathlib.Path("crates/flock-cuda-ffi/Cargo.toml"); s = p.read_text()
if "bincode" not in s:
    s = s.replace("[dev-dependencies]\n", "[dev-dependencies]\nbincode = { workspace = true }\n", 1); p.write_text(s)
p = pathlib.Path("crates/flock-cuda-ffi/tests/gpu_roundtrip.rs"); s = p.read_text()
ins = ('    println!("VSIZE m={m} proof_bytes={} commitment_bytes={} prove_s={prove_secs:.4} warmup_s={warmup_secs:.4} verify_s={:.4}",\n'
       '        bincode::serialize(&proof).unwrap().len(), bincode::serialize(&commitment).unwrap().len(), t1.elapsed().as_secs_f64());\n')
assert s.count("    if TAMPER {") == 1
s = s.replace("    if TAMPER {", ins + "    if TAMPER {", 1)
for nbl in (12, 13, 16, 17, 18, 19):
    s += f"\n#[test]\n#[ignore]\nfn gpu_roundtrip_vs{nbl}() {{\n    roundtrip::<{nbl}, false>();\n}}\n"
p.write_text(s)
EOF
time cargo test -p flock-cuda-ffi --release --features gpu --no-run 2>&1 | grep -E 'error|warning: unused|Finished|Executable|nvcc' | head -30
nvidia-smi --query-gpu=name,driver_version,clocks.max.sm,power.limit,memory.total --format=csv | tee $OUT/gpu.txt
for rep in $(seq 1 ${CUDA_REPS:-3}); do
  for nbl in ${CUDA_NBLS:-12 13 16 17 18 19}; do
    /usr/bin/time -v cargo test -p flock-cuda-ffi --release --features gpu --test gpu_roundtrip -- --ignored --nocapture --exact gpu_roundtrip_vs$nbl \
      > $OUT/flockcuda-nbl$nbl-r$rep.txt 2>&1
    echo "rc=$? nbl=$nbl rep=$rep"; grep -E "VSIZE|GPU proof verified|panicked|error|Maximum resident" $OUT/flockcuda-nbl$nbl-r$rep.txt | head -5
  done
done
grep -h VSIZE $OUT/flockcuda-*.txt > $OUT/vsize.txt
cp -r $OUT "$RESEARCH_RUN_DIR/out" 2>/dev/null || true
