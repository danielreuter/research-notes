#!/usr/bin/env bash
# agkr-bound: register (1) the operands-committed scaffold (frame-v3 + vllm-v1 cells, negatives with pins) and (2) the
# hash spike (survey §4.3) as gate-log/v1 trees; then preserve the runs.  usage: bash 17_put.sh
set -euo pipefail
IN=$RESEARCH_RUN_DIR/inputs
R=/workspace/research/runs
A=/workspace/agkr-bound
small() { (cd "$1" && find . -type f \( -name '*.json' -o -name '*.log' -o -name '*.txt' \) -size -4M ! -name circuit.txt ! -name epilogue.txt) ; }
copy_small() { local s=$1 d=$2; mkdir -p "$d"; small "$s" | while read -r f; do mkdir -p "$d/$(dirname "$f")"; cp "$s/$f" "$d/$f"; done; }

T=$A/commit-evidence; rm -rf $T; mkdir -p $T/runs
for r in r20260925-072901-b125 r20260925-074931-1329 r20260925-075248-f4dc r20260925-085244-5d8e; do cp $R/$r/stdout.log $T/runs/$r.stdout.log; done
cp $IN/09_commit_dev.sh $IN/10_commit_neg.py $IN/11_commit_neg.sh $T/ 2>/dev/null || true
for c in bf16-ampere-sha256 fp8-hopper-blake3 fp4-nvf4-sha256 bf16-ampere-vllm-v1 fp8-hopper-vllm-v1; do
  copy_small $A/commit/$c $T/$c
  [ -d $A/commit/neg-$c ] && copy_small $A/commit/neg-$c $T/neg-$c
done
du -sh $T
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR operands-committed SCAFFOLD (lane/agkr-bound 83582436..caacca10) on A100 vy-agkr-bound2: per-VU x-row / W-column digests published as 32 epilogue limbs, sha256(commitment.txt) absorbed; verity-gkr-verify rebuilds the frame-v3 (sha256/row/v1, blake3-keyed/row/v2) or vllm-v1 (pos-leaf/v0, StepDomain chunk null, PROVISIONAL operand-domain mapping) trees natively and compares the pinned roots. Relations R+sha256 / R+blake3 / R+vllm-v1 have NO circuit pin (digest columns unconstrained in-proof), so every cell status is failed by design; scaffold check accepted, roots match: bf16-ampere+sha256 t.total 0.883, fp8-hopper+blake3 0.459, fp4-nvf4+sha256 0.402 (unpinned), bf16-ampere+vllm-v1 0.862, fp8-hopper+vllm-v1 0.431 (1 rep each). Negatives with pins compiled in (r20260925-085244-5d8e): wrong digest, swapped W, y word, limb range, spec manifest, spec leaf/domain, no commitment, relabelled claims rejected; gap_alt_operand ACCEPTED (the scaffold gap, structural: 32 digest wires referenced by no gate)", "run_id": "r20260925-085244-5d8e", "source_commit": "caacca10", "candidate": "A-GKR", "variant": "A-GKR, operands committed (scaffold)"}' --ref public_input_binding=art:559147e1

T=$A/hash-evidence; rm -rf $T; mkdir -p $T/runs
for r in r20260925-080740-fb11 r20260925-081528-c188 r20260925-084251-099a; do cp $R/$r/stdout.log $T/runs/$r.stdout.log; done
cp $R/r20260925-084251-099a/result.json $T/agkr-bf16-cpu-result.json
cp $IN/12_hash_spike.sh $IN/13_link_stub.sh $IN/14_agkr_cpu.sh $IN/15_link_gpu.py $IN/16_link_gpu.sh $T/ 2>/dev/null || true
copy_small $A/hash $T/hash
copy_small $A/link $T/link
du -sh $T
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "Hash-proving survey 4.3 CPU spike for A-GKR on vy-agkr-bound2 (EPYC 7742 Zen 2, 13-thread cgroup, no AVX-512; A100-SXM4-80GB), per 4,096-VU BF16 batch = 393,216 SHA-256 compressions: A-GKR BF16 alone CPU 361.5 s (run-vu, 175M committed, depth 355) vs A100 cell 0.86 s; (b) in-field Longfellow flat SHA-256 in BabyBear (tools/sha256_flat.py, 6,657 committed/compression, 36,929 wires, depth 5) Rust CPU B=64 3.26 s, B=4096 106.7 s (arith-bound), extrapolated ~10,240 s per batch (~28x A-GKR), GPU prover infeasible (dense layers); (a) Flock b684b12 hash_throughput portable path, 13 threads: SHA-256 5.00 s / BLAKE3 2.18 s at 2^18 (~7.5 / ~3.3 s per batch); link A-GKR side stub (tools/link_stub.py, 512 operand bits/unit k=1, booleanity + recomposition; cross-field check NOT built) 393,216 units CPU 138.3 s (+38%), A100 0.55 s warm (+64%); k=2 173 s, k=4 563 s CPU", "run_id": "r20260925-084251-099a", "source_commit": "caacca10", "candidate": "A-GKR", "variant": "hash spike (survey 4.3)"}'

bash $IN/04_store.sh push r20260925-072901-b125 r20260925-074931-1329 r20260925-075248-f4dc r20260925-080740-fb11 r20260925-081528-c188 r20260925-084251-099a
