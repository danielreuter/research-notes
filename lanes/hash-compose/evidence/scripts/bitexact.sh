#!/usr/bin/env bash
# Bare-path byte-identity for the Ampere BF16 relation (vu.py --relation bf16) main a55b3fc vs lane tree, deterministic mode
# (cpu, fiat-shamir, non-ZK), plus the bare GPU gate and a Rust verify of the pod dump with the rebuilt (new pins) binary.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/cargo-target
PY=/workspace/venv312/bin/python
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
stage "rebuild ligero-verify from the lane tree"
( cd /workspace/src/backends/ligero-verify && cargo build --release 2>&1 | tail -1 && cp "$CARGO_TARGET_DIR/release/ligero-verify" /workspace/bin/ && sha256sum /workspace/bin/ligero-verify )
for T in src-main src; do
  stage "bare bf16 (vu.py) CPU deterministic dump from /workspace/$T"
  cd /workspace/$T && export PYTHONPATH=packages/verity/src:backends/numerical/python:.
  rm -rf /workspace/bx/$T; mkdir -p /workspace/bx/$T
  OMP_NUM_THREADS=8 $PY -m backends.direct.ligero.run --relation bf16 bench-vu --device cpu --mode fiat-shamir --batch 960 --total-vus 10 --reps 1 \
     --root /workspace/bench-instances/v1 --dump-dir /workspace/bx/$T/proofs --dump-reps 1 --out /workspace/bx/$T/result.json 2>&1 | tail -2 | cut -c1-200
  ( cd /workspace/bx/$T/proofs && sha256sum system.bin rep1/sub_00.stmt rep1/sub_00.proof )
  $PY -c "import json; r=json.load(open('/workspace/bx/$T/result.json')); print('statement_format', r['workload_fingerprint'].get('statement_format'), 'instances', r['workload_fingerprint']['instances'])"
done
stage "diff"
cd /workspace/bx && for f in system.bin rep1/sub_00.stmt rep1/sub_00.proof; do cmp src-main/proofs/$f src/proofs/$f && echo "IDENTICAL $f"; done
stage "Rust verify of the lane tree's bare dump (pinned bf16-ampere)"
/workspace/bin/ligero-verify batch --dir /workspace/bx/src/proofs/rep1 --system /workspace/bx/src/proofs/system.bin --target-bits 128 --threads 4 | cut -c1-600
/workspace/bin/ligero-verify system-digest --system /workspace/bx/src/proofs/system.bin
stage "bare GPU gate bf16 (vu.py, 64 VUs) on the lane tree"
cd /workspace/src && export PYTHONPATH=packages/verity/src:backends/numerical/python:.
$PY -m backends.direct.ligero.run --relation bf16 gate-vu --device cuda --vus 64 --root /workspace/bench-instances/v1 2>&1 | tail -3 | cut -c1-300
stage "Rust verify of the hashed bf16-ampere fixture dump with the rebuilt binary"
/workspace/bin/ligero-verify batch --dir /workspace/fx/bf16-ampere-hash/rep1 --system /workspace/fx/bf16-ampere-hash/system.bin --target-bits 128 --threads 4 | cut -c1-600
echo BITEXACT_DONE
