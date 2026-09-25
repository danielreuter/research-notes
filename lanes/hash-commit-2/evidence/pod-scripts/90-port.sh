#!/usr/bin/env bash
# hash-commit-2 portability (sm_80 A100 / sm_90 H100): the GPU committer at bcf75db7 (== main's) on a non-sm_89 part.
#   1 arch facts (compute cap, NVRTC version, fv3_top block size)   2 byte-identity suites (frame-v3 + vllm-v1 GPU trees ==
#   core vectors / host builders / commit_cost references)   3 neighbour suites   4 per-piece profile at the fp8 shape (4096)
#   5 commit_cost --impl gpu at 4096 (rows 1536/3072 B, words)   6 bench-vu bf16-hopper+blake3 GPU arm then host arm, 1 round
#   (evidence sha vs the 4090's c90e6d0d; Rust batch verdict).   Outputs /workspace/hash-commit-2/{runs.txt,tests-*.log,prof.txt,cc/,runs/}
S=/workspace/hash-commit-2/scripts; source $S/lib.sh
{ nvidia-smi --query-gpu=name,compute_cap,driver_version,memory.total --format=csv,noheader
  cd /workspace/src && $PY $S/arch.py; } 2>&1 | tee $HC/arch.txt
tests /workspace/src backends/shared/hash_gpu/tests/test_frame_v3.py backends/direct/ligero/frame_gpu_test.py tests/test_commit_cost_benchmark.py
cp $HC/tests.log $HC/tests-cg.log
bash $S/61-cg-neighbours.sh
gpu_idle && ( cd /workspace/src && $PY $S/75-cg-prof.py > $HC/prof.txt 2>&1; echo "$(date -u +%H:%M:%SZ) prof rc=$?" | tee -a $LOG )
bash $S/70-cg-commit-cost.sh
LIGERO_COMMIT_GPU=1 run cg-gpu-bf16-hopper_blake3-r1 /workspace/src bf16-hopper+blake3 ${BATCH:-8192} ${DEPTH:-2} ${REPS:-5}
[ "${HOST_ARM:-1}" = 1 ] && LIGERO_COMMIT_GPU=0 run cg-host-bf16-hopper_blake3-r1 /workspace/src bf16-hopper+blake3 ${BATCH:-8192} ${DEPTH:-2} ${REPS:-5}
echo "$(date -u +%H:%M:%SZ) 90-port done" | tee -a $LOG
