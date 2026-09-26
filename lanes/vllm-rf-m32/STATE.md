# vllm-rf-m32 STATE

New lane (no predecessor). Agent bc-7039be6c-2a9f-5501-af51-ee96bf96b428, branch `lane/vllm-rf-m32` from origin/main `78b8935b`
(contains fee32f05). Brief: `$STORE/internal/lane-briefs/vllm-m32.md`.

## Done
- `271a0952` scheme.chunk_header passes `M & 0xFFFFFFFF` (kernels write u32 M; length bound by the step root's n). Tests in
  `tests/commit/test_production_vectors.py`: `test_chunk_header_matches_the_pre_c1_u32_header` (M in {0, 8, 2^32-1, 2^32, 2^32+7,
  5036944512, 2^40+3}; equals the pre-c1 `pack_words` header; equals core's unmasked header for M < 2^32) and
  `test_chunk_header_of_a_step_past_2_32_words` (#4's M = 5036944512 no longer raises; word 6 = M mod 2^32).
- Header-word audit (only M needs the mask):
  - chunk header, all three kernel paths (`native_tree.cu` via `native_collect.cpp` `static_cast<uint32_t>`, `hidden_gpu_tree.cu`
    `(uint32_t)`): launch_tag = step, HB = step, chunk_index = `(uint32_t)(ci+ci_base)` < M*4/chunk_bytes <= 2^27 for any real
    step, chunk_words in {32,64,128}, NB in {0,1} (committer) or the key-block cap (hidden stream), src_mask `& 0xFF` in-kernel
    and < 2^8 in core. None reaches 2^32 on a real row: unchanged.
  - thread header (`verity_tap.h` 487-489, all `(uint32_t)`): slab, m_block, n_block, tidx, seqlen_q/k, tag, nbmax -- all bounded
    by sequence lengths and head counts, far below 2^32: unchanged.
  - No CPU reference of the kernel's header exists (the CUDA copies are pinned only on GPU pods by `test_scheme_cuda.py`).

- Fix READY (`READY.md`): gate (b) run r20260925-214510-4478 PRESERVED, jdiff clean; vyv-rf-m32-cpu terminated 22:39Z;
  merge-ready handoff to vllm-coordinator and sha handoff to vllm-rf-epoch sent 22:40Z.

## Task 2: confirming gate (a) T0+T1 on main (coordinator handoff 20260925T2155Z)
- Tree origin/main `5f8d8789` (b1 dca6a867 in; 271a0952 not yet merged). Worktree ~/wt/main-5f8d8789.
- Mint 22:40:00Z on the VM: TTL 3h, object-read-only, prefixes manifests/ + objects/sha256/, piped to vyv-rf-m32-reg
  /root/r2ro.env (0600). Prefetch 26 ok / 0 fail; key deleted 22:47:08Z (prefetch trap).

- Gate (a) on main 5f8d8789 CONFIRMED: r20260925-224745-e739 rc 0, 73 passed / 85 skipped (158), = a23b's base; only the #70/#75
  skip rewordings. PRESERVED (both runs). CONFIRM handoff 20260926T0315Z sent.

## Running
- nothing. vyv-rf-m32-cpu terminated 22:39Z, vyv-rf-m32-reg terminated 03:14Z.

## Next
- none (FINAL). Spend about $8.5 total.

## Open questions
- none

## Found-not-fixed
- `test_native_jit_keying::test_pod_release_fails_closed_...` needs `tests/sweep/pod_release.sh`, which is absent (fails at base and head).
- Gate scripts that set their own PYTHONPATH miss `protocols/sampled_proofs` on post-#29 trees (gate (a) fails at collection).
