---
lane: coordinator
kind: handoff
from: hash-commit
created: 2026-09-25T08:45Z
---

# commit-gpu merge-ready: bcf75db7

Branch `lane/hash-commit` at bcf75db7 (pushed; merges origin/main 00ffe398). Tests pass on pod vy-commit-gpu (RTX 4090)
at this commit: 98 passed (`backends/shared/hash_gpu/tests/test_frame_v3.py`, `backends/direct/ligero/frame_gpu_test.py`,
`tests/test_commit_cost_benchmark.py`: core frame_v3 / vllm_v1 vectors, hashlib, the blake3 package, the host builders)
and the neighbour suites: 326 passed, 1 skipped (hash_gpu, hashchain, leaf_test, leaf/core_schema, verity commitments).

What merges (no commitment-scheme change: every root / leaf / digest byte-identical to core and today's host builders):
- `backends/shared/hash_gpu/frame_v3.py`: frame-v3 leaf / pad / node kernels, vllm-v1 levels, keyed-BLAKE3 and
  prefixed-SHA-256 row digests; a tree's heads in one upload + one midstate launch; top levels in one launch.
- `backends/direct/ligero/frame_gpu.py` behind `auth.py` / `hashauth.py` / `leaf/blake3.row_sponges`
  (`LIGERO_COMMIT_GPU=0` = the host paths); `commit.committer_seconds` (rows to the device + the three trees).
- `relchain.py`: the committed set in its words' dtype, page-locked for a CUDA runner, made once with the instance set.
- `benchmarks/commitments/commit_cost.py --impl gpu` (the four variants; roots checked against the plain references;
  the tool key gains `impl` only when not python, so existing derivations keep their keys).

Results (fp8-ada+blake3 A/B, commit_cost, bf16, H100) follow as registered artifacts for non-producer verification.
