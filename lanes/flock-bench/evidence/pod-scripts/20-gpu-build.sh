#!/usr/bin/env bash
# flock-bench: build Flock-CUDA roundtrip tests (patched: verity batch sizes + proof size) and the flock-zorch venv/dumpers.
set -uxo pipefail
W=/workspace/flock-bench; cd $W
source $HOME/.cargo/env
export PATH=/usr/local/cuda-13.3/bin:$PATH NVCC=/usr/local/cuda-13.3/bin/nvcc
cd $W/flock
git checkout -q crates/flock-cuda-ffi
python3 - <<'EOF'
import re, pathlib
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
git diff --stat
time cargo test -p flock-cuda-ffi --release --features gpu --no-run 2>&1 | tail -5
# flock-zorch
cd $W/flock-zorch
[ -x .venv/bin/python ] || python3.11 -m venv .venv
.venv/bin/pip install -q -r requirements.in --extra-index-url https://fractalyze.github.io/pypi/simple/ 2>&1 | tail -3
FRXV=$(sed -n 's/^frx==//p' requirements.in)
.venv/bin/pip install -q "frx-cuda12-plugin[with-cuda]==$FRXV" --extra-index-url https://fractalyze.github.io/pypi/simple/ 2>&1 | tail -3
time cargo build --release --example dump_blake3_ligerito --example dump_sha2_ligerito --example bench_blake3_ligerito_cpu --example bench_sha2_ligerito_cpu 2>&1 | tail -3
export FRX_PLATFORMS=cuda,cpu FRX_ENABLE_X64=1 XLA_PYTHON_CLIENT_PREALLOCATE=false
unset JAX_PLATFORMS JAX_ENABLE_X64
ZREV=$(grep -A3 'module_name = "zorch"' MODULE.bazel | sed -n 's/.*commit = "\([0-9a-f]*\)".*/\1/p')
[ -d $W/zorch ] || git clone -q https://github.com/fractalyze/zorch $W/zorch
git -C $W/zorch fetch -q origin; git -C $W/zorch checkout -q $ZREV; git -C $W/zorch log --oneline -1
ls $W/zorch/zorch/__init__.py
export PYTHONPATH="python:$W/zorch"
echo "PYTHONPATH=$PYTHONPATH"
ptxas --version | tail -1
.venv/bin/python -c "import frx, flock_zorch.prover; print(frx.devices())"
